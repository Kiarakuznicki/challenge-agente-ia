import streamlit as st

from app import obtener_vectorstore
from src.agent import responder_pregunta

st.set_page_config(
    page_title="Nexalend | Asistente Interno",
    page_icon="🤖",
    layout="wide",
)

st.markdown(
    """
    <style>
    .nexalend-header {
        background: linear-gradient(135deg, #6d28d9 0%, #2563eb 100%);
        padding: 24px 28px;
        border-radius: 16px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 14px;
        position: sticky;
        top: 0;
        z-index: 999;
        align-items: center;
        gap: 14px;
    }
    .nexalend-logo {
        width: 46px; height: 46px;
        background: rgba(255,255,255,0.2);
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 22px; color: white;
        flex-shrink: 0;
    }
    .nexalend-title { color: white; font-size: 20px; font-weight: 700; margin: 0; }
    .nexalend-subtitle { color: rgba(255,255,255,0.85); font-size: 13px; margin: 0; }

    div[data-testid="stChatMessage"] {
        border-radius: 16px;
        padding: 4px 8px;
    }

    .stButton button {
        background: #f5f4ff;
        color: #6d28d9;
        border: 1px solid #e0d9ff;
        border-radius: 999px;
        font-size: 13px;
        padding: 6px 14px;
    }
    .stButton button:hover {
        background: #6d28d9;
        color: white;
        border-color: #6d28d9;
    }

    .fuente-caption {
        color: #6b7280;
        font-size: 12px;
        margin-top: -8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="nexalend-header">
        <div class="nexalend-logo">N</div>
        <div>
            <p class="nexalend-title">Nexalend</p>
            <p class="nexalend-subtitle">Asistente de documentos internos - ¡NO PROPORCIONAR DATOS PERSONALES!</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "vectorstore" not in st.session_state:
    with st.spinner("Cargando/indexando la base de conocimiento..."):
        st.session_state.vectorstore = obtener_vectorstore()

if "historial" not in st.session_state:
    st.session_state.historial = []

if "pregunta_sugerida" not in st.session_state:
    st.session_state.pregunta_sugerida = None

if not st.session_state.historial:
    st.write("Preguntame lo que necesites saber sobre la empresa")
    col1, col2, col3 = st.columns(3)
    sugerencias = [
        "¿Qué es NexaLend?",
        "3 definiciones clave",
        "Estrategia de seguridad",
    ]
    for columna, sugerencia in zip([col1, col2, col3], sugerencias):
        with columna:
            if st.button(sugerencia, use_container_width=True):
                st.session_state.pregunta_sugerida = sugerencia

for turno in st.session_state.historial:
    with st.chat_message("user", avatar="🧑"):
        st.write(turno["pregunta"])
    with st.chat_message("assistant", avatar="🤖"):
        st.write(turno["respuesta"])
        if turno["fuentes"]:
            st.markdown(
                f'<p class="fuente-caption">Fuente: {", ".join(turno["fuentes"])}</p>',
                unsafe_allow_html=True,
            )



pregunta_input = st.chat_input("Escribí tu pregunta sobre los documentos...")
pregunta_final = pregunta_input or st.session_state.pregunta_sugerida
st.session_state.pregunta_sugerida = None

if pregunta_final:
    with st.spinner("Buscando en los documentos..."):
        resultado = responder_pregunta(pregunta_final, st.session_state.vectorstore)
    fuentes = sorted(
        {
            f"{d.metadata.get('source', 'documento')} (pág. {d.metadata.get('page', '?')})"
            for d in resultado["fuentes"]
        }
    )
    st.session_state.historial.append(
        {"pregunta": pregunta_final, "respuesta": resultado["respuesta"], "fuentes": fuentes}
    )
    st.rerun()