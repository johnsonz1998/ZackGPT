# app/vector_memory.py

import json
from pathlib import Path
from llama_index.core import VectorStoreIndex, Document
from llama_index.embeddings.openai import OpenAIEmbedding
from app.memory_engine import MEMORY_DIR

class VectorMemoryEngine:
    def __init__(self, model_name="text-embedding-3-small"):
        self.embed_model = OpenAIEmbedding(model=model_name)
        self.index = None

    def load_documents(self):
        documents = []
        for file in MEMORY_DIR.glob("*.json"):
            with open(file, "r") as f:
                entry = json.load(f)
                if "embedding" in entry:
                    doc_text = f"{entry['question']} {entry['answer']}"
                    documents.append(Document(text=doc_text, metadata=entry))
        return documents

    def build_index(self):
        docs = self.load_documents()
        self.index = VectorStoreIndex.from_documents(docs, embed_model=self.embed_model)

    def query(self, prompt, top_k=3):
        if not self.index:
            self.build_index()
        engine = self.index.as_query_engine(similarity_top_k=top_k)
        return engine.query(prompt)
