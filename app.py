"""Launch the current Humbertito web app from the existing Streamlit listing."""

import os
from urllib.parse import urlsplit

import streamlit as st

st.set_page_config(page_title="Librería Bazar Humbertito", page_icon="📚")
st.title("Librería Bazar Humbertito")

PUBLIC_URL = "https://humbertito-production.up.railway.app"
web_url = os.getenv("HUMBERTITO_WEB_URL", "").strip() or PUBLIC_URL

try:
    address = urlsplit(web_url)
    if address.scheme != "https" or not address.netloc or address.username or address.password:
        raise ValueError
except ValueError:
    st.error("Configura HUMBERTITO_WEB_URL con la dirección HTTPS del sistema.")
else:
    st.link_button("Abrir Humbertito", web_url, type="primary")
