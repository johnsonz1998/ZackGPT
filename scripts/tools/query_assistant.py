# query_assistant.py — Load FAISS index, run query through GPT-4 with matching embedding model

import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

load_dotenv()

INDEX_DIR = "embeddings/"
LLM = OpenAI(model="gpt-4-turbo")
EMBED_MODEL = OpenAIEmbedding(model="text-embedding-3-large")

def load_index():
    print("📦 Loading FAISS index from:", INDEX_DIR)
    storage_context = StorageContext.from_defaults(persist_dir=INDEX_DIR)
    return load_index_from_storage(storage_context)

def ask_question(index, question, system_prompt=None):
    prompt = (
        f"{system_prompt}\n\n"
        f"User: {question}\n"
        f"Assistant:"
    )

    query_engine = index.as_query_engine(llm=LLM, embed_model=EMBED_MODEL)
    response = query_engine.query(prompt)
    return str(response)

if __name__ == "__main__":
    index = load_index()
    print("🤖 Ask me anything about your data.")
    while True:
        question = input("🔎 > ")
        if question.lower() in {"exit", "quit"}:
            break
        answer = ask_question(index, question)
        print("💬", answer)
