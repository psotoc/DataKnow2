from __future__ import annotations
import os
import streamlit as st
from dotenv import load_dotenv
from rag import ask

load_dotenv()


K_DEFAULT = 4

st.set_page_config(page_title="Asistente Legal", page_icon="⚖️", layout="centered")
st.title("⚖️ Asistente Legal")

# ===== UI =====
query = st.text_input(
    "Escribe tu pregunta",
    placeholder=""
)

col1, col2 = st.columns([1, 1])
with col1:
    clear_btn = st.button("Limpiar")
with col2:
    ask_btn = st.button("Consultar", type="primary")
    

if clear_btn:
    st.rerun()

if ask_btn and query.strip():
    if not os.getenv("OPENAI_API_KEY"):
        st.error("No encuentro OPENAI_API_KEY en el entorno. Configura tu .env o variable de entorno.")
    else:
        with st.spinner("Generando respuesta..."):
            try:
                ans = ask(query, k=K_DEFAULT)
                st.markdown("### Respuesta")
                st.markdown(ans)
            except Exception as e:
                st.error(f"Hubo un error al responder: {e}")

st.divider()
st.caption("© 24/08/2025")
