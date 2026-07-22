import os
import shutil
import time

from chromadb.api.client import SharedSystemClient
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

import config

MARCADOR_COMPLETO = "_indexacion_completa.ok"


def crear_embeddings():
    return GoogleGenerativeAIEmbeddings(model=config.EMBEDDING_MODEL)


def indexacion_completa() -> bool:
    """Indica si ya existe un indice completo y confiable en disco."""
    marcador = os.path.join(config.PERSIST_DIRECTORY, MARCADOR_COMPLETO)
    return os.path.isfile(marcador)


def crear_vectorstore(chunks, tamano_lote: int = 20, pausa_segundos: int = 15):
    marcador = os.path.join(config.PERSIST_DIRECTORY, MARCADOR_COMPLETO)
    if os.path.isfile(marcador):
        os.remove(marcador)

    SharedSystemClient.clear_system_cache()

    embeddings = crear_embeddings()
    db = Chroma(
        collection_name=config.COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=config.PERSIST_DIRECTORY,
    )

    total = len(chunks)
    total_lotes = (total + tamano_lote - 1) // tamano_lote

    for indice_lote, inicio in enumerate(range(0, total, tamano_lote), start=1):
        lote = chunks[inicio: inicio + tamano_lote]
        print(f"Indexando lote {indice_lote}/{total_lotes} ({len(lote)} fragmentos)...")

        intentos_maximos = 4
        for intento in range(1, intentos_maximos + 1):
            try:
                db.add_documents(lote)
                break
            except Exception as e:
                if intento == intentos_maximos:
                    raise
                espera = 65  # el limite de Google es "por minuto"; 65s da margen de sobra
                print(f"  Error en el lote {indice_lote} (intento {intento}/{intentos_maximos}): {e}")
                print(f"  Reintentando en {espera}s...")
                time.sleep(espera)

        es_ultimo_lote = indice_lote == total_lotes
        if not es_ultimo_lote:
            print(f"  Pausando {pausa_segundos}s para respetar el límite gratuito de la API...")
            time.sleep(pausa_segundos)

    # Solo si TODOS los lotes terminaron bien, marcamos el indice como completo.
    os.makedirs(config.PERSIST_DIRECTORY, exist_ok=True)
    with open(marcador, "w") as f:
        f.write("ok")

    return db


def cargar_vectorstore():
    SharedSystemClient.clear_system_cache()
    embeddings = crear_embeddings()
    db = Chroma(
        collection_name=config.COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=config.PERSIST_DIRECTORY,
    )
    return db


if __name__ == "__main__":
    from src.loader import cargar_y_dividir_pdfs

    chunks = cargar_y_dividir_pdfs()
    print(f"Indexando {len(chunks)} fragmentos en lotes...")
    db = crear_vectorstore(chunks)
    print("Vector store creado y persistido en:", config.PERSIST_DIRECTORY)

    resultados = db.similarity_search("política de privacidad", k=2)
    print("\n--- Prueba de búsqueda semántica ---")
    for r in resultados:
        print(f"({r.metadata.get('source')}, página {r.metadata.get('page')}):", r.page_content[:150], "...\n")