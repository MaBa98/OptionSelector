import streamlit as st
from src.ib_client import IBClient

def safe_connect(host: str, port: int, client_id: int) -> IBClient:
    """
    Tenta la connessione IB, fallback a demo.
    """
    client = IBClient.connect(host, port, client_id)
    if client.ib is None:
        st.warning("Connessione IB fallita: modalità demo attivata")
    return client

def format_percentage(x: float) -> str:
    return f"{x*100:.2f}%"
