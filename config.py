import os
from dotenv import load_dotenv

load_dotenv()  

DATA_DIR = "data"  

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

PERSIST_DIRECTORY = "db"
COLLECTION_NAME = "doc_base"

EMBEDDING_MODEL = "gemini-embedding-001"

LLM_MODEL = "openai/gpt-oss-120b"
LLM_TEMPERATURE = 0

TOP_K = 4  

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GOOGLE_API_KEY:
    raise EnvironmentError(
        "No se encontro GOOGLE_API_KEY. Copia .env.example a .env y completa tu clave "
        "obtenida en https://aistudio.google.com/app/apikey"
    )

if not GROQ_API_KEY:
    raise EnvironmentError(
        "No se encontro GROQ_API_KEY. Copia .env.example a .env y completa tu clave "
        "obtenida gratis en https://console.groq.com/keys"
    )