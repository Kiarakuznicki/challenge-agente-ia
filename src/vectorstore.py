from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

import config

def crear_embeddings():
    return GoogleGenerativeAIEmbeddings(model=config.EMBEDDING_MODEL)

def crear_vectorstore(chunks):
    embeddings = crear_embeddings()
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=config.COLLECTION_NAME,
        persist_directory=config.PERSIST_DIRECTORY,
    )
    return db

def cargar_vectorstore():
    embeddings = crear_embeddings()
    db = Chroma(
        collection_name=config.COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=config.PERSIST_DIRECTORY,
    )
    return db

if __name__ == "__main__":
    from src.loader import cargar_y_dividir_pdf
    chunks = cargar_y_dividir_pdf()
    print(f"Indexando {len(chunks)}")
    db = crear_vectorstore(chunks)
    print("Vector store creado y persistido en:", config.PERSIST_DIRECTORY)

    resultados = db.similarity_search("¿Cada cuánto hay que renovar la contraseña?", k=2)
    print("\n--- Prueba de busqueda semantica ---")
    for r in resultados:
        print(f"(pagina {r.metadata.get('page')}):", r.page_content[:150], "...\n")