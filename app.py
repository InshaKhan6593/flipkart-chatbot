from flask import render_template, Flask, request, Response, session
from prometheus_client import Counter, generate_latest
from flipkart.data_ingestion import DataIngestor
from flipkart.rag_chain import RAGChainBuilder
from dotenv import load_dotenv
from uuid import uuid4

load_dotenv()
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Request")

def create_app():
    app = Flask(__name__)
    app.secret_key = "your-secret-key"  # Required if using Flask sessions

    vector_store = DataIngestor().ingest(load_existing=True)
    rag_chain = RAGChainBuilder(vector_store).build_chain()

    @app.route("/")
    def index():
        REQUEST_COUNT.inc()
        return render_template("index.html")
    
    @app.route("/get", methods=["POST"])
    def get_response():
        user_input = request.form["msg"]

        # Generate a session ID once and reuse it
        if "session_id" not in session:
            session["session_id"] = str(uuid4())

        session_id = session["session_id"]

        response = rag_chain.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}}
        )

        return response
    
    @app.route("/metrics")
    def metrics():
        return Response(generate_latest(), mimetype="text/plain")
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
