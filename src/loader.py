import glob
import os

from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config


def leer_pdfs(directorio: str) -> list[Document]:
    rutas_pdf = sorted(glob.glob(os.path.join(directorio, "*.pdf")))
    if not rutas_pdf:
        raise FileNotFoundError(f"No se encontraron archivos .pdf en '{directorio}'")

    documentos = []
    for ruta in rutas_pdf:
        nombre_archivo = os.path.basename(ruta)
        reader = PdfReader(ruta)
        for numero_pagina, pagina in enumerate(reader.pages, start=1):
            texto = pagina.extract_text() or ""
            if texto.strip():
                documentos.append(
                    Document(
                        page_content=texto,
                        metadata={"source": nombre_archivo, "page": numero_pagina},
                    )
                )
    return documentos


def cargar_y_dividir_pdfs(directorio: str = config.DATA_DIR):
    documentos = leer_pdfs(directorio)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(documentos)
    return chunks


def cargar_y_dividir_csv(path_csv: str, columnas_texto: list[str] | None = None):
    import pandas as pd

    df = pd.read_csv(path_csv)
    columnas = columnas_texto or list(df.columns)

    documentos = []
    for indice_fila, fila in df.iterrows():
        texto = " | ".join(f"{columna}: {fila[columna]}" for columna in columnas)
        documentos.append(
            Document(
                page_content=texto,
                metadata={"source": os.path.basename(path_csv), "fila": int(indice_fila)},
            )
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    return splitter.split_documents(documentos)


if __name__ == "__main__":
    chunks = cargar_y_dividir_pdfs()
    fuentes = sorted({c.metadata["source"] for c in chunks})
    print(f"Se generaron {len(chunks)} fragmentos, de {len(fuentes)} documentos: {fuentes}\n")
    print("--- Ejemplo del primer fragmento ---")
    print(chunks[0].page_content[:300])
    print("\n--- Metadata del primer fragmento ---")
    print(chunks[0].metadata)