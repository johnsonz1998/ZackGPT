# ingest_text.py — Load local files, OCR images, embed with OpenAI, and store in FAISS with rich metadata

import os
import tempfile
import pytesseract
from PIL import Image
from dotenv import load_dotenv
from datetime import datetime
from llama_index.core import VectorStoreIndex, Document, StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore

load_dotenv()

DATA_DIR = "data/"
INDEX_DIR = "embeddings/"
SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".png", ".jpg", ".jpeg"}
EMBED_MODEL = OpenAIEmbedding(model="text-embedding-3-large")

def extract_text_from_image(filepath):
    try:
        image = Image.open(filepath)
        return pytesseract.image_to_string(image)
    except Exception as e:
        print(f"⚠️ Failed to OCR {filepath}: {e}")
        return ""

def load_documents():
    print("📁 Scanning:", DATA_DIR)
    documents = []

    for root, _, files in os.walk(DATA_DIR):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            full_path = os.path.join(root, file)

            if ext not in SUPPORTED_EXTENSIONS:
                print(f"⏭️ Skipping unsupported file: {file}")
                continue

            if ext in {".png", ".jpg", ".jpeg"}:
                text = extract_text_from_image(full_path)
            else:
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                except Exception as e:
                    print(f"⚠️ Failed to read {file}: {e}")
                    continue

            if text.strip():
                metadata = {
                    "file": file,
                    "path": full_path,
                    "type": ext,
                    "source": infer_source(full_path),
                    "indexed_at": datetime.utcnow().isoformat()
                }
                documents.append(Document(text=text, metadata=metadata))
                print(f"📄 Loaded: {file} | source: {metadata['source']}")
            else:
                print(f"⚠️ No text extracted from: {file}")

    return documents

def infer_source(path):
    if "calendar" in path.lower():
        return "calendar"
    if "messages" in path.lower():
        return "messages"
    return "manual_upload"

def create_vector_index(documents):
    print("📊 Embedding and indexing documents...")
    storage_context = StorageContext.from_defaults()
    index = VectorStoreIndex.from_documents(
        documents,
        embed_model=EMBED_MODEL,
        storage_context=storage_context,
        show_progress=True
    )
    index.storage_context.persist(persist_dir=INDEX_DIR)
    print("✅ Index saved to:", INDEX_DIR)

if __name__ == "__main__":
    docs = load_documents()
    if docs:
        create_vector_index(docs)
    else:
        print("⚠️ No documents to index.")