markdown# Nexalend | Asistente de IA sobre documentos internos

Agente conversacional que responde preguntas en lenguaje natural sobre la documentación interna de Nexalend (una fintech), usando **RAG (Retrieval-Augmented Generation)** para fundamentar cada respuesta en el contenido real de los documentos, en vez de depender del conocimiento general del modelo.

---

## Descripción

Nexalend cuenta con múltiples documentos internos (FAQ, términos y condiciones, políticas de privacidad, seguridad, tarifas, soporte técnico, RRHH). Este agente permite consultarlos en lenguaje natural sin necesidad de abrir cada archivo manualmente, citando siempre de qué documento y página sale cada respuesta.

## Arquitectura

Usuario
│ pregunta en lenguaje natural
▼
streamlit_app.py (interfaz web, paleta violeta/azul/blanco)
│
▼
src/agent.py ── Retriever ──▶ Chroma (vector store) ──▶ data/\*.pdf
│ (ya indexados)
│
└── Prompt + contexto recuperado ──▶ Gemini (LLM) ──▶ Respuesta + fuentes

1. **`src/loader.py`** (Etapa 1) — recorre automáticamente todos los PDFs de `data/`, extrae su texto con `pypdf` y lo divide en fragmentos (chunks) con `RecursiveCharacterTextSplitter`.
2. **`src/vectorstore.py`** — convierte esos fragmentos en embeddings (`GoogleGenerativeAIEmbeddings`) y los indexa en un vector store local (`Chroma`), en lotes con pausas (para respetar el límite de la capa gratuita de la API). La indexación se marca como completa recién al terminar todos los lotes, para evitar quedar con un índice a medio construir si el proceso se interrumpe.
3. **`src/agent.py`** (Etapa 2) — dada una pregunta, recupera los fragmentos más relevantes (Retrieval) y le pide a Gemini que responda basándose únicamente en ellos (Generation), citando el documento y la página de origen.
4. **`streamlit_app.py`** — interfaz web con diseño propio (tema violeta/azul/blanco), historial de conversación y preguntas sugeridas.
5. **`app.py`** — contiene la lógica compartida de carga/indexación del vector store, reutilizada por la interfaz.

## Tecnologías utilizadas

| Categoría        | Tecnología                                                                             |
| ---------------- | -------------------------------------------------------------------------------------- |
| Lenguaje         | Python 3.12+                                                                           |
| Orquestación     | LangChain (`langchain-core`, `langchain-text-splitters`)                               |
| Lectura de PDF   | `pypdf`                                                                                |
| Embeddings + LLM | Google Gemini (`langchain-google-genai`) — `gemini-embedding-001` y `gemini-3.5-flash` |
| Vector store     | Chroma (`langchain-chroma`), persistido en `db/`                                       |
| Interfaz         | Streamlit, con theming y CSS personalizado                                             |
| Deploy           | Streamlit Community Cloud                                                              |

## Estructura del proyecto

challenge-agente-ia/
├── data/ # documentos base (9 PDFs de Nexalend)
├── src/
│ ├── loader.py # Etapa 1: lectura y chunking multi-documento
│ ├── vectorstore.py # embeddings + Chroma, indexacion en lotes
│ └── agent.py # Etapa 2: cadena RAG
├── .streamlit/
│ └── config.toml # tema visual (violeta/azul/blanco)
├── app.py # logica de carga/indexacion del vector store
├── streamlit_app.py # interfaz web (punto de entrada del deploy)
├── config.py # parametros centralizados
├── requirements.txt
├── .env.example
└── .gitignore

## Instalación y ejecución local

```bash
git clone https://github.com/Kiarakuznicki/challenge-agente-ia.git
cd challenge-agente-ia

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt

copy .env.example .env          # Windows
# cp .env.example .env          # Mac/Linux
```

Editá `.env` y pegá tu propia clave de Gemini (se consigue gratis en https://aistudio.google.com/app/apikey):
GOOGLE_API_KEY=tu_clave_aquiv

Ejecutar:

```bash
streamlit run streamlit_app.py
```

La primera ejecución indexa los 9 documentos (tarda unos minutos, por las pausas necesarias para respetar el límite gratuito de la API). Las siguientes ejecuciones cargan el índice ya guardado en `db/` y son instantáneas.

## Ejemplos de preguntas y respuestas

> ⚠️ COMPLETAR: reemplazar estos 4 ejemplos por preguntas reales que hayas probado en tu propia app, con la respuesta exacta que te dio.

**Pregunta:** [completar]
**Respuesta:** [completar]

**Pregunta:** [completar]
**Respuesta:** [completar]

**Pregunta:** [completar]
**Respuesta:** [completar]

**Pregunta:** (una que sepas que NO está en los documentos, para mostrar que el agente no inventa)
**Respuesta:** [completar — debería decir algo como "No encontré esa información en el documento"]

## Deploy

**Nota sobre la plataforma elegida:** el enunciado del challenge sugiere Oracle Cloud Infrastructure (OCI) para el despliegue, permitiendo explícitamente el uso de "otra herramienta si tiene más sentido". Se optó por **Streamlit Community Cloud** por tratarse de la plataforma nativa del framework de la interfaz (Streamlit), lo que permite un despliegue continuo directamente desde este repositorio de GitHub, sin necesidad de gestionar infraestructura de servidor por separado.

- **URL pública:** https://challenge-agente-ia-m83srbauwlccweayczlomi.streamlit.app
- **Evidencia:** _(agregar acá la captura de pantalla de la app funcionando)_

## Limitaciones conocidas

- La capa gratuita de la API de Gemini tiene un límite de solicitudes por minuto. Bajo uso intenso o simultáneo, puede aparecer un error temporal (HTTP 429); reintentar tras unos segundos lo resuelve.
- La app se "duerme" tras un período de inactividad prolongado (comportamiento estándar de Streamlit Community Cloud); la primera visita tras la inactividad puede tardar unos segundos más en responder.

## Autor

Kiara Kuznicki — Challenge Oracle + Alura, Generación G10
