from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

import config

SYSTEM_PROMPT = """Sos un asistente interno que responde preguntas de empleados
basandote EXCLUSIVAMENTE en los fragmentos de documento que se te dan como contexto.

Reglas:
1. Si la respuesta esta en el contexto, respondela de forma clara y directa, en español.
2. Si el contexto NO contiene informacion suficiente para responder, decilo
   explicitamente (por ejemplo: "No encontré esa información en el documento")
   en vez de inventar una respuesta.
3. No agregues datos que no esten en el contexto, aunque los sepas de otra fuente.

Contexto recuperado del documento:
{context}
"""

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "{pregunta}"),
    ]
)


def crear_llm():
    return ChatGoogleGenerativeAI(
        model=config.LLM_MODEL,
        temperature=config.LLM_TEMPERATURE,
    )


def formatear_contexto(documentos) -> str:
    """Concatena los fragmentos recuperados en un solo bloque de texto para el prompt."""
    partes = []
    for i, doc in enumerate(documentos, start=1):
        fuente = doc.metadata.get("source", "?")
        pagina = doc.metadata.get("page", "?")
        partes.append(f"[Fragmento {i} - {fuente}, página {pagina}]\n{doc.page_content}")
    return "\n\n".join(partes)


def responder_pregunta(pregunta: str, vectorstore, llm=None) -> dict:
    """
    Ejecuta el flujo RAG completo para una pregunta y devuelve tanto la
    respuesta como los fragmentos que se usaron como fuente.
    """
    llm = llm or crear_llm()
    retriever = vectorstore.as_retriever(search_kwargs={"k": config.TOP_K})

    # 1) Retrieval
    documentos = retriever.invoke(pregunta)
    contexto = formatear_contexto(documentos)

    # 2) Generation
    cadena = PROMPT | llm | StrOutputParser()
    respuesta = cadena.invoke({"context": contexto, "pregunta": pregunta})

    return {"respuesta": respuesta, "fuentes": documentos}


if __name__ == "__main__":
    # Prueba aislada de punta a punta. Requiere que ya exista el vector
    # store (haber corrido antes python -m src.vectorstore).
    from src.vectorstore import cargar_vectorstore

    db = cargar_vectorstore()
    resultado = responder_pregunta("¿Cada cuánto hay que renovar la contraseña?", db)
    print("Respuesta:", resultado["respuesta"])
    print("\nFuentes usadas:")
    for doc in resultado["fuentes"]:
        print(f"- {doc.metadata.get('source')} (página {doc.metadata.get('page')})")