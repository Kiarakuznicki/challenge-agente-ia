import os
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = "data"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

PERSIST_DIRECTORY = "db"
COLLECTION_NAME = "doc_base"

EMBEDDING_MODEL = "gemini-embedding-001"
LLM_MODEL = "gemini-3.5-flash"
LLM_TEMPERATURE = 0

TOP_K = 6

try: 
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
except EnvironmentError:
    print("No se encontró GOOGLE_API_KEY,tiene que existir el archivo .env con la clave adentro")

