from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config

def leer_pdf(path_pdf: str) -> list[Document]:
    """Extrae el texto de cada pagina del PDF y arma un Document por pagina."""
    reader = PdfReader(path_pdf)
    documentos = []
    for numero_pagina, pagina in enumerate(reader.pages, start=1):
        texto = pagina.extract_text() or ""
        if texto.strip():  # descartamos paginas vacias
            documentos.append(
                Document(
                    page_content=texto,
                    metadata={"source": path_pdf, "page": numero_pagina},
                )
            )
    return documentos

def cargar_y_dividir_pdf(path_pdf: str = config.PDF_PATH):
    documentos = leer_pdf(path_pdf)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(documentos)
    return chunks

if __name__ == "__main__":
    chunks = cargar_y_dividir_pdf()
    print(f"Se generaron {len(chunks)} fragmentos.\n")
    print("--- Ejemplo del primer fragmento ---")
    print(chunks[0].page_content)
    print("\n--- Metadata del primer fragmento ---")
    print(chunks[0].metadata)