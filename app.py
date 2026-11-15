"""Punto de entrada de la interfaz Streamlit."""

import streamlit as st


st.navigation(
    [st.Page("streamlit_ui/app.py", title="Humbertito")],
    position="hidden",
).run()
