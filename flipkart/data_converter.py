import pandas as pd
from langchain_core.documents import Document

class DataConverter:
    def __init__(self,file_path:str):
        self.file_path = file_path
    
    def convert(self):
        df = pd.read_csv(self.file_path, usecols=["product_title", "review"])
        documents = [
            Document(page_content=row["review"], metadata={"product_name": row["product_title"]})
            for _, row in df.iterrows()
        ]

        return documents

        # df.iterrows return two things index and row
        # we dont care about the index and fetches title and reviews from row
