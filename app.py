import os

import config
from src.loader import cargar_y_dividir_pdf
from src.vectorstore import crear_vectorstore, cargar_vectorstore
from src.agent import responder_pregunta

def obtener_vectorstore():
    if os.path.isdir(config.PERSIST_DIRECTORY) and os.listdir(config.PERSIST_DIRECTORY):
        print(f"Cargando vector store existente desde '{config.PERSIST_DIRECTORY}'...")
        return cargar_vectorstore()

    print(f"No hay un vector store previo. Procesando '{config.PDF_PATH}'...")
    chunks = cargar_y_dividir_pdf()
    print(f"Documento dividido en {len(chunks)} fragmentos. Generando embeddings...")
    db = crear_vectorstore(chunks)
    print("Vector store creado y guardado. Las próximas ejecuciones van a ser más rápidas.\n")
    return db

def main():
    print("=" * 60)
    print(" Agente de IA - Preguntas sobre el documento interno")
    print("=" * 60)

    db = obtener_vectorstore()

    print("\nAgente listo. Escribí tu pregunta (o 'salir' para terminar).\n")
    while True:
        pregunta = input("Pregunta: ").strip()
        if not pregunta:
            continue
        if pregunta.lower() in {"salir", "exit", "quit"}:
            print("¡Listo, nos vemos!")
            break

        resultado = responder_pregunta(pregunta, db)
        print("\nRespuesta:", resultado["respuesta"])
        paginas = sorted({doc.metadata.get("page") for doc in resultado["fuentes"]})
        print(f"(Fuente: páginas {paginas} del documento)\n")

if __name__ == "__main__":
    main()
      