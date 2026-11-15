"""Launch the current Humbertito web app from the existing Streamlit listing."""

import os
from urllib.parse import urlsplit

import streamlit as st

st.set_page_config(page_title="Librería Bazar Humbertito", page_icon="📚")
st.title("Librería Bazar Humbertito")

web_url = os.getenv("HUMBERTITO_WEB_URL", "").strip()
if web_url:
    try:
        address = urlsplit(web_url)
        if address.scheme != "https" or not address.netloc or address.username or address.password:
            raise ValueError
    except ValueError:
        st.error("Configura HUMBERTITO_WEB_URL con la dirección HTTPS del sistema.")
    else:
        st.link_button("Abrir Humbertito", web_url, type="primary")
else:
    st.write("Abre Humbertito en la computadora donde está iniciado el sistema.")
    st.link_button("Abrir en este equipo", "http://127.0.0.1:3000", type="primary")
    st.link_button(
        "Ver instrucciones de arranque",
        "https://github.com/luiangelsb26/librer-a-bazar-humbertito#ejecuci%C3%B3n-local",
    )
