import os

import config
from src.loader import cargar_y_dividir_pdfs
from src.vectorstore import crear_vectorstore, cargar_vectorstore
from src.agent import responder_pregunta

def obtener_vectorstore():
    if os.path.isdir(config.PERSIST_DIRECTORY) and os.listdir(config.PERSIST_DIRECTORY):
        print(f"Cargando vector store existente desde '{config.PERSIST_DIRECTORY}'...")
        return cargar_vectorstore()

    print(f"No hay un vector store previo. Procesando documentos en '{config.DATA_DIR}'...")
    chunks = cargar_y_dividir_pdfs()
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
        fuentes = sorted({f"{d.metadata.get('source')} (pág. {d.metadata.get('page')})" for d in resultado["fuentes"]})
        print(f"(Fuentes: {', '.join(fuentes)})\n")

if __name__ == "__main__":
    main()
      