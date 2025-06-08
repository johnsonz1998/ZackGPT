import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def test_connection():
    try:
        res = client.models.list()
        if any('gpt-4' in m.id for m in res.data):
            print("✅ GPT-4 access confirmed.")
        else:
            print("⚠️ GPT-4 not found in your model list.")
    except Exception as e:
        print("❌ OpenAI API error:", e)

if __name__ == "__main__":
    test_connection()
