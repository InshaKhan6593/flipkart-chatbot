from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableMap, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

from flipkart.config import Config

class RAGChainBuilder:
    def __init__(self,vector_store):
        self.vector_store = vector_store
        self.llm = ChatGroq(model=Config.MODEL, temperature=0.1)
        self.history_store = {}
    
    def _get_session_history(self,sesstion_id:str) -> ChatMessageHistory:
        if sesstion_id not in self.history_store:
            self.history_store[sesstion_id] = ChatMessageHistory()
        return self.history_store[sesstion_id]
    
    def build_chain(self):
        retriever = self.vector_store.as_retriever(
            search_type = "similarity",
            search_kwargs={"k": 3}
        )

        context_prompt = ChatPromptTemplate.from_messages([
            ("system", "Given the following chat history and the user's latest question, rewrite it as a standalone question that can be understood without prior context."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful e-commerce assistant. Use the provided product titles and reviews to answer user queries. 
            Stick strictly to the context provided. Be concise and helpful.

            CONTEXT:
            {context}

            QUESTION: {input}"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        question_rewriter = context_prompt | self.llm | StrOutputParser()

        # Step 2: context_chain that feeds rewritten question to retriever
        context_chain = RunnableLambda(
            lambda x: {"input": x["input"], "chat_history": x["chat_history"]}
        ) | question_rewriter | retriever


        rag_chain = RunnableMap({
            "input": lambda x: x["input"],
            "chat_history": lambda x: x["chat_history"],
            "context": context_chain
        }) | qa_prompt | self.llm | StrOutputParser()

        return RunnableWithMessageHistory(
            rag_chain,
            self._get_session_history,
            input_messages_key = "input",
            history_messages_key = "chat_history",
            output_message_key = "answer"
        )



