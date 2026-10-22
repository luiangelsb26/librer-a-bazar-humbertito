import io
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import importlib
import math
import hashlib
import re
import unicodedata
from datetime import datetime
import analysis
import prediction
import database
import auth

if not hasattr(database, "reiniciar_datos"):
    database = importlib.reload(database)

# ==========================================================
# CONFIGURACIÓN
# ==========================================================

st.set_page_config(
    page_title="Librería Bazar Humbertito",
    page_icon="B",
    layout="wide"
)


def notificar_exito(mensaje):
    notificaciones = st.session_state.setdefault(
        "_notificaciones_exito",
        [],
    )
    notificaciones.append(mensaje)


def mostrar_grafico_fijo(figura, clave):
    """Muestra una gráfica fija, conserva la información emergente al pasar."""
    figura.update_xaxes(fixedrange=True)
    figura.update_yaxes(fixedrange=True)
    figura.update_layout(dragmode=False)
    st.plotly_chart(
        figura,
        config={
            "scrollZoom": False,
            "displayModeBar": False,
            "displaylogo": False,
            "responsive": True,
        },
        key=clave,
        theme="streamlit",
        width="stretch",
        height=430,
    )


def formatear_numero_es(valor, decimales=0):
    """Usa punto para miles y coma para decimales, como en formato local."""
    numero = f"{float(valor):,.{decimales}f}"
    return numero.replace(",", "\0").replace(".", ",").replace("\0", ".")


def formatear_soles(valor):
    return f"S/ {formatear_numero_es(valor, 2)}"


for mensaje_notificacion in st.session_state.pop(
    "_notificaciones_exito",
    [],
):
    st.toast(
        mensaje_notificacion,
        icon=":material/check_circle:",
    )


database.configurar_desde_streamlit()


# ==========================================================
# APARIENCIA Y NAVEGACIÓN
# ==========================================================

if "tema_blanco" not in st.session_state:
    st.session_state.tema_blanco = False


def alternar_tema():
    st.session_state.tema_blanco = not st.session_state.tema_blanco


st.markdown("""
    <style>
    
/* ==========================================
   MENÚ LATERAL - HUMBERTITO IA
   ========================================== */

/* Panel lateral */
[data-testid="stSidebar"] {
    background-color: #20232D;
    border-right: 1px solid #343A47;
}

/* Permitir desplazamiento vertical */
[data-testid="stSidebar"] > div:first-child {
    height: 100vh;
    overflow-y: auto;
    overflow-x: hidden;
    scrollbar-width: thin;
    scrollbar-color: #50596A #20232D;
}

/* Contenedor interno */
[data-testid="stSidebarContent"] {
    padding: 1.2rem 1rem 2rem 1rem;
    overflow-y: auto;
    overflow-x: hidden;
}

/* Barra de desplazamiento en Chrome y Edge */
[data-testid="stSidebarContent"]::-webkit-scrollbar {
    width: 6px;
}

[data-testid="stSidebarContent"]::-webkit-scrollbar-thumb {
    background: #50596A;
    border-radius: 10px;
}

[data-testid="stSidebarContent"]::-webkit-scrollbar-track {
    background: #20232D;
}

/* Separadores */
[data-testid="stSidebar"] hr {
    border-color: #343A47;
    margin: 1rem 0;
}

/* Botones del menú */
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    min-height: 46px;
    border-radius: 10px;
    border: 1px solid transparent;
    background-color: #292D38;
    color: #E0E5ED;
    font-size: 14px;
    font-weight: 500;
    text-align: left;
    padding: 0.65rem 1rem;
    margin-bottom: 5px;
    transition: background-color 0.2s ease,
                border-color 0.2s ease;
}

/* Efecto al pasar el cursor */
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #353B49;
    border-color: #4B586A;
    color: #FFFFFF;
}

/* Botones de cierre de sesión */
[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background-color: #252A35;
    border-color: #3A414F;
}

/* Ajustes para pantallas pequeñas */
@media (max-width: 768px) {
    [data-testid="stSidebarContent"] {
        padding: 0.8rem;
    }

    [data-testid="stSidebar"] .stButton > button {
        min-height: 44px;
        font-size: 13px;
    }
}
        :root {
            --humbertito-accent: #d45b45;
            --humbertito-accent-soft: rgba(212, 91, 69, 0.14);
            --humbertito-teal: #2d8177;
        }
        html, body, [class*="css"] {
            font-family: "Trebuchet MS", "Segoe UI", sans-serif;
        }
        [data-testid="stAppViewContainer"] {
            background-image: radial-gradient(
                circle at 100% 0%, rgba(212, 91, 69, 0.08), transparent 28rem
            );
        }
        [data-testid="stArrowVegaLiteChart"],
        [data-testid="stVegaLiteChart"],
        [data-testid="stPyplotChart"] {
            animation: none !important;
            transition: none !important;
            transform: none !important;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
            margin: 0 0 0.15rem 0;
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: 0.01em;
            color: var(--humbertito-accent);
        }
        [data-testid="stSidebar"] > div:first-child {
            padding: 4.8rem 1.875rem 1rem;
            overflow: hidden !important;
        }
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebarCollapsedControl"] {
            position: fixed !important;
            top: 0.8rem !important;
            left: 16.8rem !important;
            z-index: 1000000 !important;
            display: block !important;
        }
        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="stSidebarCollapsedControl"] button,
        [data-testid="stSidebar"] button[aria-label*="sidebar" i],
        [data-testid="stSidebar"] button[aria-label*="barra lateral" i] {
            width: 2.65rem !important;
            height: 1.9rem !important;
            min-width: 2.65rem !important;
            min-height: 1.9rem !important;
            padding: 0 0.35rem !important;
            border: 1px solid #cbd4dc !important;
            border-radius: 0.5rem !important;
            background: #edf0f3 !important;
            color: #263238 !important;
            box-shadow: 0 2px 7px rgba(38, 50, 56, 0.14) !important;
            transform: none !important;
            transition: none !important;
        }
        [data-testid="stSidebarCollapseButton"] button:hover,
        [data-testid="stSidebarCollapsedControl"] button:hover,
        [data-testid="stSidebar"] button[aria-label*="sidebar" i]:hover,
        [data-testid="stSidebar"] button[aria-label*="barra lateral" i]:hover {
            background: #e1e6ea !important;
            border-color: #2d8177 !important;
            color: #263238 !important;
            transform: none !important;
        }
        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="stSidebarCollapsedControl"] button,
        [data-testid="stSidebar"] button[aria-label*="sidebar" i],
        [data-testid="stSidebar"] button[aria-label*="barra lateral" i] {
            background: #2d8177 !important;
            border: 1px solid #8ed1c8 !important;
            color: #ffffff !important;
            box-shadow: 0 3px 9px rgba(15, 23, 42, 0.22) !important;
        }
        [data-testid="stSidebarCollapseButton"] button:hover,
        [data-testid="stSidebarCollapsedControl"] button:hover,
        [data-testid="stSidebar"] button[aria-label*="sidebar" i]:hover,
        [data-testid="stSidebar"] button[aria-label*="barra lateral" i]:hover {
            background: #24665f !important;
            border-color: #b5e1db !important;
            color: #ffffff !important;
        }
        [data-testid="stSidebarCollapseButton"] button svg,
        [data-testid="stSidebarCollapsedControl"] button svg,
        [data-testid="stSidebarCollapseButton"] button svg *,
        [data-testid="stSidebarCollapsedControl"] button svg * {
            color: #ffffff !important;
            stroke: #ffffff !important;
        }
        button[aria-label*="open sidebar" i],
        button[aria-label*="close sidebar" i],
        button[aria-label*="expand sidebar" i],
        button[aria-label*="collapse sidebar" i],
        button[aria-label*="abrir barra lateral" i],
        button[aria-label*="cerrar barra lateral" i] {
            display: flex !important;
            position: fixed !important;
            top: 0.8rem !important;
            left: 16.8rem !important;
            z-index: 1000001 !important;
            width: 2.65rem !important;
            height: 1.9rem !important;
            min-width: 2.65rem !important;
            min-height: 1.9rem !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 0 !important;
            border: 1px solid #8ed1c8 !important;
            border-radius: 0.5rem !important;
            background: #2d8177 !important;
            color: #ffffff !important;
            box-shadow: 0 3px 9px rgba(15, 23, 42, 0.22) !important;
            opacity: 1 !important;
            visibility: visible !important;
        }
        button[aria-label*="open sidebar" i] svg,
        button[aria-label*="close sidebar" i] svg,
        button[aria-label*="expand sidebar" i] svg,
        button[aria-label*="collapse sidebar" i] svg,
        button[aria-label*="abrir barra lateral" i] svg,
        button[aria-label*="cerrar barra lateral" i] svg {
            color: #ffffff !important;
            stroke: #ffffff !important;
        }
        [data-testid="stSidebarCollapseButton"] button:focus-visible,
        [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_item_"] button:focus-visible,
        [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_active"] button:focus-visible {
            outline: 2px solid rgba(148, 163, 184, 0.42) !important;
            outline-offset: 2px !important;
        }
        [data-testid="stSidebarCollapseButton"] svg,
        [data-testid="stSidebar"] [data-testid="stExpander"] summary svg {
            width: 1rem !important;
            height: 1rem !important;
            stroke-width: 2.5 !important;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] summary {
            cursor: pointer !important;
            font-weight: 650 !important;
            letter-spacing: 0.01em !important;
        }
        [data-testid="stSidebar"] {
            flex: 0 0 280px;
            width: 280px;
            min-width: 280px;
            max-width: 280px;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
            overflow: visible;
        }
        [data-testid="stSidebar"] .sidebar-brand {
            padding: 0.25rem 0.8rem 1.15rem 0.95rem;
            border-left: 3px solid var(--humbertito-accent);
            border-bottom: 1px solid rgba(128, 128, 128, 0.22);
            background: rgba(128, 128, 128, 0.035);
            border-radius: 0 0.45rem 0.45rem 0;
            width: 100%;
            box-sizing: border-box;
            position: static !important;
            transform: none !important;
            transition: none !important;
            animation: none !important;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"]:has(.sidebar-brand) {
            position: static !important;
            transform: none !important;
            transition: none !important;
            animation: none !important;
        }
        [data-testid="stSidebar"] .sidebar-brand-title {
            display: flex;
            align-items: flex-start;
            color: var(--humbertito-accent);
            font-family: Georgia, "Times New Roman", serif;
            font-size: 1.22rem;
            font-weight: 750;
            line-height: 1.12;
            letter-spacing: 0.025em;
        }
        [data-testid="stSidebar"] .sidebar-brand-name {
            min-width: 0;
            max-width: 225px;
            display: block;
            white-space: nowrap;
        }
        [data-testid="stSidebar"] .sidebar-brand-subtitle {
            margin-top: 0.55rem;
            color: rgba(250, 250, 250, 0.66);
            font-size: 0.8rem;
            line-height: 1.4;
            letter-spacing: 0.045em;
            white-space: nowrap;
        }
        [data-testid="stSidebar"] hr {
            margin: 0.8rem 0 1.45rem;
            opacity: 0.35;
        }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] strong {
            color: var(--humbertito-accent);
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4 {
            margin: 0.35rem 0 0.65rem 0;
            font-size: 0.95rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            text-transform: uppercase;
        }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            margin-top: 0.35rem;
        }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            font-size: 0.82rem;
            line-height: 1.35;
        }
        [data-testid="stMainBlockContainer"] {
            max-width: 1400px;
            padding: 2rem 2.5rem 3rem;
        }
        [data-testid="stMain"] p {
            line-height: 1.55;
        }
        [data-testid="stMain"] hr {
            margin: 1.35rem 0;
            opacity: 0.45;
        }
        [data-testid="stSidebar"] [role="group"] {
            min-height: 2.75rem;
            transition: border-color 160ms ease, box-shadow 160ms ease;
        }
        [data-testid="stSidebar"] [role="group"]:focus-within {
            box-shadow: 0 0 0 3px rgba(255, 75, 75, 0.18);
        }
        [data-testid="stSidebar"] [role="group"] [role="combobox"] {
            font-size: 0.95rem;
            font-weight: 600;
        }
        [data-testid="stSidebar"] [role="group"] button {
            min-height: 2.75rem;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] button {
            min-height: 2.7rem;
            font-weight: 600;
            letter-spacing: 0.01em;
            width: 100%;
            justify-content: center;
            text-align: center;
            transform: none !important;
            transition: none !important;
        }
        [data-testid="stSidebar"] [data-testid="stButton"],
        [data-testid="stSidebar"] [data-testid="stButton"] button,
        [data-testid="stSidebar"] [class*="st-key-menu_item_"],
        [data-testid="stSidebar"] [class*="st-key-menu_active"] {
            transform: none !important;
            transition: none !important;
            animation: none !important;
            will-change: auto !important;
        }
        [data-testid="stSidebar"] [data-testid="stSelectbox"],
        [data-testid="stSidebar"] [data-testid="stButton"],
        [data-testid="stSidebar"] [role="group"] {
            width: 100%;
            max-width: 252px;
            box-sizing: border-box;
        }
        [data-testid="stSidebar"] [data-testid="stSelectbox"] [role="combobox"],
        [data-testid="stSidebar"] [role="group"] {
            width: 100%;
            box-sizing: border-box;
        }
        [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_"] {
            width: 100% !important;
            max-width: 252px;
        }
        [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_"] [data-testid="stButton"] {
            width: 100% !important;
            max-width: 252px;
        }
        [data-testid="stSidebar"] [role="group"] {
            border-radius: 0.5rem;
        }
        [data-testid="stMain"] [data-testid="stTextInput"],
        [data-testid="stMain"] [data-testid="stNumberInput"],
        [data-testid="stMain"] [data-testid="stTextArea"],
        [data-testid="stMain"] [data-testid="stSelectbox"] {
            width: 100%;
            max-width: 520px;
        }
        [class*="st-key-menu_item_"] button,
        [class*="st-key-menu_active"] button {
            min-height: 2.7rem;
            padding: 0.6rem 0.75rem;
            border: 1px solid var(--humbertito-accent) !important;
            border-radius: 0.5rem;
            background: var(--humbertito-accent) !important;
            color: #ffffff !important;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.12);
            transform: none !important;
            transition: none !important;
        }
        [class*="st-key-menu_item_"] button:hover,
        [class*="st-key-menu_active"] button:hover {
            background: #b94735 !important;
            border-color: #b94735 !important;
            color: #ffffff !important;
            transform: none !important;
        }
        [class*="st-key-menu_active"] button {
            background: var(--humbertito-accent) !important;
            border-color: var(--humbertito-accent) !important;
            color: #ffffff !important;
        }
        [class*="st-key-menu_active"] button:hover {
            background: #b94735 !important;
            border-color: #b94735 !important;
            color: #ffffff !important;
        }
        [class*="st-key-theme_toggle"] {
            position: fixed !important;
            top: 4.25rem;
            right: 1.5rem;
            z-index: 999999;
            width: auto;
            box-sizing: border-box;
            padding: 0;
        }
        [class*="st-key-theme_toggle"] button {
            width: 3rem;
            min-width: 3rem;
            height: 3rem;
            min-height: 3rem;
            margin: 0;
            padding: 0;
            border-radius: 50%;
            font-size: 1.15rem;
            font-weight: 650;
            letter-spacing: 0.01em;
            border: 1px solid #2d8177 !important;
            background: #2d8177 !important;
            color: #ffffff !important;
            box-shadow: 0 4px 12px rgba(20, 28, 32, 0.18);
            transition: background-color 160ms ease, border-color 160ms ease, color 160ms ease !important;
        }
        [class*="st-key-theme_toggle"] button:hover {
            transform: none !important;
            background: #24665f !important;
            border-color: #24665f !important;
            box-shadow: 0 4px 12px rgba(20, 28, 32, 0.18);
        }
        [class*="st-key-theme_toggle"] button:focus-visible {
            outline: 3px solid rgba(45, 129, 119, 0.35);
            outline-offset: 3px;
        }
        @media (max-width: 640px) {
            [class*="st-key-theme_toggle"] {
                top: 3.75rem;
                right: 0.65rem;
            }
            [class*="st-key-theme_toggle"] button {
                width: 2.75rem;
                min-width: 2.75rem;
                height: 2.75rem;
                min-height: 2.75rem;
                font-size: 1.05rem;
            }
        }
        [data-testid="stMain"] h1 {
            margin-top: 0.5rem;
            margin-bottom: 0.35rem;
            font-size: clamp(1.65rem, 3vw, 2.35rem);
            font-weight: 750;
            letter-spacing: -0.02em;
            font-family: Georgia, "Times New Roman", serif;
            color: var(--humbertito-accent);
        }
        [data-testid="stMain"] h1 + h3 {
            margin-top: 0;
            margin-bottom: 0.55rem;
            font-size: 1.05rem;
            font-weight: 600;
            opacity: 0.82;
        }
        .quick-card {
            margin: 0 0.2rem 0.75rem;
            padding: 1rem 1.1rem;
            box-sizing: border-box;
            width: 100%;
            min-width: 0;
            overflow: hidden;
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 0.8rem;
            background: linear-gradient(135deg, rgba(212, 91, 69, 0.08), rgba(45, 129, 119, 0.07));
            box-shadow: 0 10px 20px rgba(20, 28, 32, 0.06);
            min-height: 8.35rem;
        }
        .quick-card strong {
            display: block;
            margin-bottom: 0.3rem;
            font-size: 1rem;
            color: var(--humbertito-accent);
        }
        .quick-card p {
            margin: 0;
            line-height: 1.5;
            font-size: 0.9rem;
            overflow-wrap: anywhere;
            word-break: normal;
        }
        [class*="st-key-quick_"] {
            margin: 0 0.2rem;
        }
        [class*="st-key-quick_"] button {
            margin-top: 0.15rem;
        }
        .alert-list {
            margin: 0.9rem 0 1.15rem;
            padding: 0.8rem 1rem 0.8rem 2rem;
            box-sizing: border-box;
            max-width: 100%;
            overflow-wrap: anywhere;
            border-left: 2px solid var(--humbertito-teal);
            border-radius: 0 0.35rem 0.35rem 0;
            background: rgba(45, 129, 119, 0.06);
            color: #263238;
        }
        .alert-list li {
            margin-bottom: 0.45rem;
            line-height: 1.5;
            font-size: 0.86rem;
            max-width: 100%;
            overflow-wrap: anywhere;
            word-break: normal;
        }
        .alert-list li:last-child {
            margin-bottom: 0;
        }
        [data-testid="stMain"] h2 {
            margin-top: 0.75rem;
            margin-bottom: 0.85rem;
            padding-bottom: 0.45rem;
            font-size: clamp(1.35rem, 2.4vw, 1.85rem);
            font-weight: 750;
            letter-spacing: -0.01em;
            border-bottom: 2px solid var(--humbertito-accent-soft);
        }
        [data-testid="stMain"] h3 {
            margin-top: 1.2rem;
            margin-bottom: 0.65rem;
            font-size: 1.1rem;
            font-weight: 700;
        }
        [data-testid="stMetric"] {
            min-height: 6.2rem;
            padding: 1rem 1.1rem;
            border: 1px solid rgba(128, 128, 128, 0.28);
            border-radius: 0.65rem;
            border-top: 3px solid var(--humbertito-accent);
            box-shadow: 0 8px 20px rgba(20, 28, 32, 0.07);
            transition: none !important;
            transform: none !important;
        }
        [data-testid="stMetric"]:hover {
            transform: none !important;
            box-shadow: 0 8px 20px rgba(20, 28, 32, 0.07);
        }
        [data-testid="stMetricLabel"] {
            font-weight: 650;
        }
        [data-testid="stMetricValue"] {
            font-size: clamp(1.3rem, 2.2vw, 1.8rem);
            font-weight: 750;
        }
        [data-testid="stForm"] {
            padding: 1.25rem;
            border: 1px solid rgba(128, 128, 128, 0.28);
            border-radius: 0.65rem;
            box-shadow: 0 8px 20px rgba(20, 28, 32, 0.05);
        }
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stSelectbox"] [role="combobox"] {
            min-height: 2.65rem;
            border-radius: 0.45rem;
            transition: border-color 160ms ease, box-shadow 160ms ease;
        }
        [data-testid="stTextInput"] input:focus,
        [data-testid="stNumberInput"] input:focus,
        [data-testid="stTextArea"] textarea:focus,
        [data-testid="stSelectbox"] [role="combobox"]:focus {
            box-shadow: 0 0 0 3px rgba(255, 75, 75, 0.16);
        }
        [data-testid="stMain"] button {
            min-height: 2.55rem;
            border-radius: 0.45rem;
            font-weight: 650;
            transition: none !important;
            transform: none !important;
        }
        [data-testid="stMain"] button:hover {
            transform: none !important;
            box-shadow: none !important;
        }
        [data-testid="stTabs"] [role="tablist"] {
            gap: 0.75rem;
            border-bottom: 1px solid rgba(128, 128, 128, 0.3);
        }
        [data-testid="stTabs"] button[role="tab"] {
            min-height: 2.7rem;
            padding: 0.65rem 0.8rem;
            font-weight: 650;
            border-radius: 0.45rem 0.45rem 0 0;
        }
        [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            color: var(--humbertito-accent);
            background: var(--humbertito-accent-soft);
        }
        [data-testid="stDataFrame"] {
            border: 1px solid rgba(128, 128, 128, 0.28);
            border-radius: 0.65rem;
            overflow: hidden;
        }
        [data-testid="stTable"] {
            width: 100%;
            overflow-x: auto;
            border: 1px solid rgba(128, 128, 128, 0.28);
            border-radius: 0.65rem;
        }
        [data-testid="stTable"] table {
            width: 100%;
            border-collapse: collapse;
        }
        [data-testid="stTable"] th,
        [data-testid="stTable"] td {
            padding: 0.7rem 0.8rem;
            text-align: left;
            border-bottom: 1px solid rgba(128, 128, 128, 0.2);
        }
        [data-testid="stArrowVegaLiteChart"],
        [data-testid="stVegaLiteChart"],
        [data-testid="stPyplotChart"] {
            padding: 0.5rem;
            border: 1px solid rgba(128, 128, 128, 0.22);
            border-radius: 0.65rem;
        }
        [data-testid="stArrowVegaLiteChart"] *,
        [data-testid="stVegaLiteChart"] *,
        [data-testid="stPyplotChart"] * {
            animation: none !important;
            transition: none !important;
        }
        [data-testid="stAlert"] {
            width: 100%;
            max-width: 980px;
            margin: 0.75rem 0;
            border: 0;
            background: transparent;
            box-sizing: border-box;
            overflow: hidden;
        }
        [data-testid="stAlertContainer"] {
            box-sizing: border-box;
            display: flex;
            align-items: center;
            width: 100%;
            max-width: 100%;
            overflow: hidden;
            min-height: 3rem;
            padding: 0.8rem 1rem;
            border: none !important;
            border-radius: 0 !important;
            box-shadow: 0 2px 7px rgba(15, 23, 42, 0.07);
        }
        [data-testid="stAlert"] svg {
            display: none !important;
        }
        [data-testid="stAlertContainer"] > div {
            width: 100%;
            min-width: 0;
            max-width: 100%;
            box-sizing: border-box;
            overflow-wrap: anywhere;
        }
        [data-testid="stAlertContentSuccess"],
        [data-testid="stAlertContentInfo"],
        [data-testid="stAlertContentWarning"],
        [data-testid="stAlertContentError"] {
            width: 100% !important;
            min-width: 0 !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
            overflow-wrap: anywhere !important;
        }
        [data-testid="stAlert"] p {
            text-align: left !important;
            max-width: 100%;
            overflow-wrap: anywhere;
            word-break: normal;
        }
        [data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) [data-testid="stAlertContainer"] {
            background: #123c2d;
            border: none !important;
        }
        [data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) [data-testid="stAlertContainer"] {
            background: #17324d;
            border: none !important;
        }
        [data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) [data-testid="stAlertContainer"] {
            background: #4a3517;
            border: none !important;
        }
        [data-testid="stAlert"]:has([data-testid="stAlertContentError"]) [data-testid="stAlertContainer"] {
            background: #4c2930;
            border: none !important;
        }
        [data-testid="stAlert"] p {
            margin: 0;
            font-size: 0.9rem;
            line-height: 1.45;
        }
        [data-testid="stForm"],
        [data-testid="stMetric"],
        [data-testid="stDataFrame"],
        [data-testid="stTable"],
        [data-testid="stExpander"] {
            box-sizing: border-box;
            min-width: 0;
            max-width: 100%;
            overflow-wrap: anywhere;
        }
        [data-testid="stPopover"] [role="listbox"],
        [role="listbox"] {
            border-radius: 0.45rem;
            box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
        }
        [role="option"] {
            min-height: 2.35rem;
            padding: 0.55rem 0.75rem;
        }
        [data-testid="stMain"] button[kind="primaryFormSubmit"] {
            font-weight: 700;
            background: var(--humbertito-accent);
            border-color: var(--humbertito-accent);
            color: #ffffff;
        }


/* ==========================================================
   SIDEBAR PROFESIONAL - HUMBERTITO
   ========================================================== */
[data-testid="stSidebar"] {
    width: 280px !important;
    min-width: 280px !important;
    max-width: 280px !important;
}
[data-testid="stSidebar"] > div:first-child {
    height: 100vh !important;
    max-height: 100vh !important;
    padding: 4.8rem 1rem 1rem !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    scrollbar-width: thin;
    scrollbar-color: #596273 transparent;
}
[data-testid="stSidebarContent"] {
    padding: 0 !important;
    overflow: visible !important;
}
[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar { width: 6px; }
[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-track { background: transparent; }
[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-thumb {
    background: #596273;
    border-radius: 10px;
}
[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-thumb:hover { background: #758096; }
[data-testid="stSidebar"] .sidebar-brand {
    margin: 0 0 1rem 0 !important;
    padding: 0.9rem 0.9rem 1rem !important;
    border-left: 3px solid var(--humbertito-accent) !important;
    border-bottom: 1px solid rgba(128,128,128,0.18) !important;
    border-radius: 0 10px 10px 0 !important;
    background: rgba(255,255,255,0.025) !important;
}
[data-testid="stSidebar"] .user-card {
    margin: 0.45rem 0 0.85rem !important;
    padding: 0.8rem 0.85rem !important;
    border: 1px solid rgba(128,128,128,0.20) !important;
    border-radius: 10px !important;
    background: rgba(255,255,255,0.035) !important;
    box-sizing: border-box !important;
}
[data-testid="stSidebar"] .user-name {
    font-size: 0.92rem !important;
    font-weight: 700 !important;
    line-height: 1.3 !important;
    margin-bottom: 0.25rem !important;
    overflow-wrap: anywhere !important;
}
[data-testid="stSidebar"] .user-role {
    font-size: 0.76rem !important;
    line-height: 1.35 !important;
    opacity: 0.68 !important;
}
[data-testid="stSidebar"] .sidebar-section-title {
    margin: 0.95rem 0 0.55rem !important;
    font-size: 0.69rem !important;
    font-weight: 750 !important;
    letter-spacing: 0.10em !important;
    text-transform: uppercase !important;
    opacity: 0.55 !important;
}
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    min-height: 42px !important;
    margin: 0 0 5px 0 !important;
    padding: 0.55rem 0.8rem !important;
    border-radius: 8px !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    color: inherit !important;
    font-size: 0.86rem !important;
    font-weight: 600 !important;
    justify-content: flex-start !important;
    text-align: left !important;
    box-shadow: none !important;
    transform: none !important;
    transition: background-color 120ms ease, border-color 120ms ease, color 120ms ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(212,91,69,0.10) !important;
    border-color: rgba(212,91,69,0.22) !important;
    color: var(--humbertito-accent) !important;
}
[data-testid="stSidebar"] [class*="st-key-menu_active"] button {
    background: var(--humbertito-accent) !important;
    border-color: var(--humbertito-accent) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important;
}
[data-testid="stSidebar"] [class*="st-key-menu_active"] button:hover {
    background: #b94735 !important;
    border-color: #b94735 !important;
    color: #ffffff !important;
}
[data-testid="stSidebar"] [class*="st-key-cerrar_sesion"] button {
    background: rgba(128,128,128,0.08) !important;
    border-color: rgba(128,128,128,0.18) !important;
}
[data-testid="stSidebar"] [class*="st-key-cerrar_sesion"] button:hover {
    background: rgba(212,91,69,0.10) !important;
    border-color: rgba(212,91,69,0.22) !important;
    color: var(--humbertito-accent) !important;
}
[data-testid="stSidebar"] .active-section {
    margin: 0.65rem 0 0.15rem !important;
    padding: 0.55rem 0.7rem !important;
    border-radius: 7px !important;
    background: rgba(128,128,128,0.06) !important;
    border: 1px solid rgba(128,128,128,0.10) !important;
    font-size: 0.72rem !important;
    line-height: 1.4 !important;
    box-sizing: border-box !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] {
    margin-top: 0.25rem !important;
    border: 1px solid rgba(128,128,128,0.18) !important;
    border-radius: 9px !important;
    overflow: hidden !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary {
    padding: 0.7rem 0.8rem !important;
    font-size: 0.82rem !important;
    font-weight: 650 !important;
}
[data-testid="stSidebar"] hr {
    margin: 0.75rem 0 !important;
    opacity: 0.25 !important;
}
@media (max-width: 768px) {
    [data-testid="stSidebar"] {
        width: 270px !important;
        min-width: 270px !important;
        max-width: 270px !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding: 4.2rem 0.8rem 0.8rem !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        min-height: 42px !important;
        font-size: 0.84rem !important;
    }
}

    </style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
/* ==========================================================
   HUMBERTITO IA — DISEÑO PREMIUM MODERNO
   ========================================================== */
:root {
    --hb-accent: #2f8f83;
    --hb-accent-2: #55b8a9;
    --hb-dark-bg: #0a1016;
    --hb-dark-surface: #121a23;
    --hb-dark-surface-2: #18232e;
    --hb-dark-border: rgba(148,163,184,.15);
    --hb-dark-text: #edf5f7;
    --hb-dark-muted: #91a3ad;
}
[data-testid="stAppViewContainer"] {
    background:
      radial-gradient(circle at 92% 0%, rgba(47,143,131,.12), transparent 25rem),
      radial-gradient(circle at 0% 100%, rgba(74,105,150,.08), transparent 23rem),
      var(--hb-dark-bg);
}
[data-testid="stMainBlockContainer"] {
    max-width: 1480px !important;
    padding: 2.25rem 2.6rem 3.5rem !important;
}
.hb-page-header {
    display:flex; align-items:flex-end; justify-content:space-between;
    gap:1rem; margin:0 0 1.45rem;
}
.hb-page-title {
    margin:0; font-family:Georgia,"Times New Roman",serif;
    font-size:clamp(1.8rem,3vw,2.55rem); font-weight:800;
    letter-spacing:-.035em; color:var(--hb-dark-text);
}
.hb-page-subtitle {
    margin:.35rem 0 0; color:var(--hb-dark-muted);
    font-size:.91rem; line-height:1.5;
}
.hb-status-pill {
    display:inline-flex; align-items:center; gap:.45rem;
    padding:.48rem .78rem; border:1px solid rgba(85,184,169,.24);
    border-radius:999px; background:rgba(47,143,131,.10);
    color:#8ed9ce; font-size:.76rem; font-weight:750; white-space:nowrap;
}
.hb-status-dot {
    width:.48rem; height:.48rem; border-radius:50%;
    background:#55b8a9; box-shadow:0 0 0 4px rgba(85,184,169,.10);
}
[data-testid="stMetric"] {
    position:relative; overflow:hidden; min-height:8.25rem !important;
    padding:1.15rem 1.2rem !important;
    border:1px solid var(--hb-dark-border) !important;
    border-radius:15px !important;
    background:linear-gradient(145deg,rgba(255,255,255,.055),rgba(255,255,255,.018)) !important;
    box-shadow:0 14px 32px rgba(0,0,0,.15) !important;
}
[data-testid="stMetric"]::after {
    content:""; position:absolute; width:7rem; height:7rem;
    right:-3rem; top:-3rem; border-radius:50%;
    background:rgba(47,143,131,.10); pointer-events:none;
}
[data-testid="stMetricLabel"] {
    color:var(--hb-dark-muted) !important; font-size:.76rem !important;
    font-weight:700 !important; text-transform:uppercase; letter-spacing:.055em;
}
[data-testid="stMetricValue"] {
    color:var(--hb-dark-text) !important;
    font-size:clamp(1.45rem,2.3vw,2rem) !important;
    font-weight:800 !important; letter-spacing:-.025em;
}
[data-testid="stForm"] {
    padding:1.3rem !important; border:1px solid var(--hb-dark-border) !important;
    border-radius:15px !important; background:rgba(18,26,35,.84) !important;
    box-shadow:0 16px 35px rgba(0,0,0,.13) !important;
}
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-baseweb="select"] > div {
    border-radius:9px !important; border-color:rgba(148,163,184,.20) !important;
    background:#101821 !important; color:var(--hb-dark-text) !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color:rgba(85,184,169,.70) !important;
    box-shadow:0 0 0 3px rgba(47,143,131,.14) !important;
}
[data-testid="stMain"] button {
    border-radius:9px !important; font-weight:700 !important;
}
[data-testid="stMain"] button[kind="primary"],
[data-testid="stMain"] button[kind="primaryFormSubmit"] {
    background:linear-gradient(135deg,#2f8f83,#26776e) !important;
    border-color:#2f8f83 !important; color:#fff !important;
    box-shadow:0 7px 18px rgba(47,143,131,.20) !important;
}
[data-testid="stMain"] button[kind="primary"]:hover,
[data-testid="stMain"] button[kind="primaryFormSubmit"]:hover {
    background:linear-gradient(135deg,#3ca193,#2f8178) !important;
    border-color:#3ca193 !important; transform:none !important; box-shadow:0 7px 18px rgba(47,143,131,.20) !important;
}
[data-testid="stTabs"] [role="tablist"] {
    gap:.3rem; padding:.25rem; border:1px solid var(--hb-dark-border);
    border-radius:11px; background:rgba(255,255,255,.025);
}
[data-testid="stTabs"] button[role="tab"] {
    border-radius:8px !important; color:var(--hb-dark-muted) !important;
    font-weight:700 !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color:#dff8f4 !important; background:rgba(47,143,131,.16) !important;
}
[data-testid="stDataFrame"], [data-testid="stTable"] {
    border:1px solid var(--hb-dark-border) !important;
    border-radius:13px !important; overflow:hidden !important;
    box-shadow:0 10px 25px rgba(0,0,0,.10);
}
[data-testid="stTable"] th {
    background:#17222c !important; color:#b9d4d1 !important;
    font-weight:750 !important; border-bottom:1px solid rgba(148,163,184,.18) !important;
}
[data-testid="stTable"] td {
    background:#111a23 !important; color:#dbe5e8 !important;
    border-bottom:1px solid rgba(148,163,184,.10) !important;
}
[data-testid="stAlertContainer"] {
    border-radius:11px !important; border:1px solid rgba(148,163,184,.12) !important;
}
[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#111820 0%,#0d141b 100%) !important;
    border-right:1px solid rgba(148,163,184,.12) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding:4.6rem .9rem 1rem !important;
}
[data-testid="stSidebar"] .sidebar-brand {
    margin-bottom:.9rem !important; padding:1rem !important;
    border:1px solid rgba(85,184,169,.16) !important;
    border-left:3px solid #3fa395 !important; border-radius:12px !important;
    background:linear-gradient(145deg,rgba(47,143,131,.09),rgba(255,255,255,.025)) !important;
}
[data-testid="stSidebar"] .user-card {
    border:1px solid rgba(148,163,184,.13) !important;
    border-radius:12px !important; background:rgba(255,255,255,.035) !important;
}
[data-testid="stSidebar"] .stButton > button {
    border:1px solid transparent !important; border-radius:9px !important;
    background:transparent !important; color:#aebdc5 !important; font-weight:650 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background:rgba(47,143,131,.09) !important;
    border-color:rgba(47,143,131,.16) !important; color:#d8f1ed !important;
}
[data-testid="stSidebar"] [class*="st-key-menu_active"] button {
    background:linear-gradient(135deg,rgba(47,143,131,.95),rgba(38,119,110,.95)) !important;
    border-color:rgba(120,215,202,.25) !important; color:#fff !important;
    box-shadow:0 7px 18px rgba(47,143,131,.18) !important;
}
::-webkit-scrollbar { width:7px; height:7px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:#3b4b56; border-radius:99px; }
::-webkit-scrollbar-thumb:hover { background:#536773; }

/* ---------- CLARO ---------- */
body:has(.hb-light-mode) [data-testid="stAppViewContainer"] {
    background:
      radial-gradient(circle at 92% 0%,rgba(47,143,131,.10),transparent 24rem),
      linear-gradient(180deg,#f9fbfc 0%,#f0f4f5 100%) !important;
}
body:has(.hb-light-mode) .hb-page-title { color:#17262d; }
body:has(.hb-light-mode) .hb-page-subtitle { color:#687980; }
body:has(.hb-light-mode) [data-testid="stMetric"] {
    border-color:#e0e8eb !important; background:rgba(255,255,255,.92) !important;
    box-shadow:0 12px 28px rgba(34,52,61,.07) !important;
}
body:has(.hb-light-mode) [data-testid="stMetricLabel"] { color:#71818a !important; }
body:has(.hb-light-mode) [data-testid="stMetricValue"] { color:#17262d !important; }
body:has(.hb-light-mode) [data-testid="stForm"] {
    background:rgba(255,255,255,.94) !important; border-color:#e0e7ea !important;
    box-shadow:0 12px 28px rgba(34,52,61,.06) !important;
}
body:has(.hb-light-mode) [data-testid="stTextInput"] input,
body:has(.hb-light-mode) [data-testid="stNumberInput"] input,
body:has(.hb-light-mode) [data-testid="stTextArea"] textarea,
body:has(.hb-light-mode) [data-baseweb="select"] > div {
    background:#fff !important; color:#24343b !important; border-color:#d4dfe3 !important;
}
body:has(.hb-light-mode) [data-testid="stTable"] th {
    background:#edf4f4 !important; color:#29434a !important;
}
body:has(.hb-light-mode) [data-testid="stTable"] td {
    background:#fff !important; color:#33474f !important;
}
body:has(.hb-light-mode) [data-testid="stTabs"] [role="tablist"] {
    background:rgba(255,255,255,.78); border-color:#e0e7ea;
}
body:has(.hb-light-mode) [data-testid="stTabs"] button[role="tab"] { color:#71818a !important; }
body:has(.hb-light-mode) [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color:#246d65 !important; background:#e8f4f2 !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] {
    background:#fff !important; border-right-color:#e1e8eb !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] .sidebar-brand {
    background:linear-gradient(145deg,#f0f8f7,#f9fbfb) !important;
    border-color:#dcebe9 !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] .user-card {
    background:#f7fafb !important; border-color:#e0e8eb !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] .stButton > button { color:#50626a !important; }
body:has(.hb-light-mode) [data-testid="stSidebar"] .stButton > button:hover {
    background:#eef7f5 !important; color:#246d65 !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] [class*="st-key-menu_active"] button {
    background:linear-gradient(135deg,#2f8f83,#27776f) !important; color:#fff !important;
}
body:has(.hb-light-mode) .hb-status-pill {
    color:#27776f; background:#e8f5f2; border-color:#cde7e2;
}

/* ---------- AJUSTES FINOS ---------- */
[data-testid="stTabs"] [role="tablist"] {
    gap:.85rem !important;
    padding-inline:.35rem !important;
}
[data-testid="stTabs"] button[role="tab"] {
    padding-inline:.8rem !important;
}
[data-testid="stMain"] h2 {
    padding-bottom:.35rem !important;
    border-bottom:1px solid rgba(148,163,184,.14) !important;
}
[data-testid="stMain"] button,
[data-testid="stTabs"] button[role="tab"],
[data-testid="stSidebar"] .stButton > button {
    transition:background-color 140ms ease,border-color 140ms ease,color 140ms ease,box-shadow 140ms ease !important;
}
[data-testid="stMain"] button:focus-visible,
[data-testid="stSidebar"] button:focus-visible,
[data-testid="stSidebar"] input:focus-visible,
[data-testid="stSidebar"] [role="combobox"]:focus-visible,
[data-testid="stTabs"] [role="tab"]:focus-visible,
[data-testid="stMain"] a:focus-visible,
[data-testid="stMain"] input:focus-visible,
[data-testid="stMain"] textarea:focus-visible,
[data-testid="stMain"] [role="combobox"]:focus-visible {
    outline:2px solid rgba(85,184,169,.72) !important;
    outline-offset:2px !important;
}
[data-testid="stMain"] [data-testid="stTextInput"] input,
[data-testid="stMain"] [data-testid="stNumberInput"] input,
[data-testid="stMain"] [data-testid="stTextArea"] textarea,
[data-testid="stMain"] [data-testid="stSelectbox"] [role="combobox"] {
    transition:border-color 140ms ease,box-shadow 140ms ease !important;
}
[data-testid="stMain"] [data-testid="stAlert"],
[data-testid="stMain"] [data-testid="stAlertContainer"] {
    border-radius:12px !important;
}
[data-testid="stMain"] [data-testid="stTable"] tbody tr:hover td {
    background:rgba(85,184,169,.055) !important;
}
body:has(.hb-light-mode) [data-testid="stMain"] h2 {
    border-bottom-color:rgba(71,96,105,.14) !important;
}
body:has(.hb-light-mode) [data-testid="stMain"] [data-testid="stTable"] tbody tr:hover td {
    background:#f2f8f7 !important;
}
@media (max-width:900px) {
    [data-testid="stMainBlockContainer"] { padding:1.4rem 1rem 2.5rem !important; }
    .hb-page-header { align-items:flex-start; flex-direction:column; }
}
[data-testid="stSidebar"] .sidebar-brand {
    padding:0.8rem 0 .95rem !important;
    border:0 !important;
    border-bottom:1px solid rgba(148,163,184,.14) !important;
    border-radius:0 !important;
    background:transparent !important;
}
[data-testid="stSidebar"] .sidebar-brand-kicker {
    color:#7faea8 !important;
    font-size:.64rem !important;
    letter-spacing:.13em !important;
}
[data-testid="stSidebar"] .sidebar-brand-title {
    color:#e5edef !important;
    font-family:inherit !important;
    font-size:1.05rem !important;
    font-weight:750 !important;
    letter-spacing:.01em !important;
}
[data-testid="stSidebar"] .sidebar-brand-subtitle {
    margin-top:.4rem !important;
    color:#91a0a8 !important;
    font-size:.76rem !important;
    letter-spacing:0 !important;
}
[data-testid="stSidebar"] .user-card {
    border-color:rgba(148,163,184,.13) !important;
    border-radius:10px !important;
    background:rgba(255,255,255,.025) !important;
}
[data-testid="stSidebar"] .user-status-text,
[data-testid="stSidebar"] .user-role {
    color:#91a0a8 !important;
}
[data-testid="stSidebar"] .sidebar-section-title {
    color:#84939b !important;
    font-size:.65rem !important;
    letter-spacing:.12em !important;
}
[data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_"] button {
    min-height:40px !important;
    margin-bottom:3px !important;
    border:1px solid transparent !important;
    border-radius:8px !important;
    background:transparent !important;
    color:#b8c4c9 !important;
    font-weight:550 !important;
    justify-content:flex-start !important;
    text-align:left !important;
    padding-left:.8rem !important;
    box-shadow:none !important;
}
[data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_"] button:hover {
    border-color:rgba(148,163,184,.10) !important;
    background:rgba(255,255,255,.045) !important;
    color:#edf3f4 !important;
}
[data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_active"] button,
[data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_active"] button:hover {
    border-color:transparent !important;
    background:rgba(255,255,255,.055) !important;
    color:#edf3f4 !important;
    box-shadow:none !important;
}
[data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_item_"] button:focus-visible,
[data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_active"] button:focus-visible {
    outline:2px solid rgba(148,163,184,.42) !important;
    outline-offset:2px !important;
}
[data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-cerrar_sesion"] button {
    min-height:36px !important;
    border:1px solid rgba(148,163,184,.14) !important;
    border-radius:8px !important;
    background:rgba(255,255,255,.025) !important;
    color:#b8c4c9 !important;
    font-size:.82rem !important;
    font-weight:500 !important;
    box-shadow:none !important;
}
[data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-cerrar_sesion"] button:hover {
    border-color:rgba(148,163,184,.24) !important;
    background:rgba(255,255,255,.055) !important;
    color:#edf3f4 !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] .sidebar-brand {
    border-bottom-color:#e5ebed !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] .sidebar-brand-kicker {
    color:#4f887f !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] .sidebar-brand-title {
    color:#26383e !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] .sidebar-brand-subtitle,
body:has(.hb-light-mode) [data-testid="stSidebar"] .user-status-text,
body:has(.hb-light-mode) [data-testid="stSidebar"] .user-role,
body:has(.hb-light-mode) [data-testid="stSidebar"] .sidebar-section-title {
    color:#718087 !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] .user-card {
    border-color:#e4eaec !important;
    background:#f8fafb !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_"] button {
    color:#506168 !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_"] button:hover {
    border-color:#e5ebed !important;
    background:#f4f7f8 !important;
    color:#26383e !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_active"] button,
body:has(.hb-light-mode) [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_active"] button:hover {
    border-color:transparent !important;
    background:#e9edef !important;
    color:#34464d !important;
    box-shadow:0 2px 5px rgba(38,50,56,.08) !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-cerrar_sesion"] button {
    border-color:#e1e8ea !important;
    background:#fff !important;
    color:#506168 !important;
}
</style>
""", unsafe_allow_html=True)


if st.session_state.tema_blanco:
    st.markdown('<div class="hb-light-mode" style="display:none"></div>', unsafe_allow_html=True)
    st.markdown("""
        <style>
            [data-testid="stAppViewContainer"],
            [data-testid="stHeader"],
            [data-testid="stMain"] {
                background: #ffffff;
            }
            [data-testid="stSidebar"] {
                background: #ffffff;
                border-right: 1px solid #e5e7eb;
            }
            [data-testid="stSidebar"] > div:first-child {
                padding: 4.8rem 1.875rem 1rem !important;
            }
            [data-testid="stSidebar"] .sidebar-brand {
                border-left: 3px solid var(--humbertito-teal) !important;
                background: #f7f9fa;
                padding: 0.9rem 0.95rem 1rem;
                border-radius: 0 0.45rem 0.45rem 0;
                width: 100%;
            }
            [data-testid="stSidebar"] * {
                color: #263238;
            }
            [data-testid="stAppViewContainer"] .main,
            [data-testid="stAppViewContainer"] .main h1,
            [data-testid="stAppViewContainer"] .main h2,
            [data-testid="stAppViewContainer"] .main h3,
            [data-testid="stAppViewContainer"] .main label,
            [data-testid="stAppViewContainer"] .main p,
            [data-testid="stAppViewContainer"] .main span {
                color: #263238;
            }
            [data-testid="stAppViewContainer"] [data-testid="stMain"],
            [data-testid="stAppViewContainer"] [data-testid="stMain"] * {
                color: #263238 !important;
            }
            [data-testid="stMetric"] {
                background: #f8fafc;
                border: 1px solid #e5e7eb;
                padding: 1rem;
                border-radius: 0.6rem;
            }
            [data-testid="stForm"],
            [data-testid="stDataFrame"],
            [data-testid="stArrowVegaLiteChart"],
            [data-testid="stVegaLiteChart"],
            [data-testid="stPyplotChart"] {
                background: #f8fafc !important;
                border-color: #e5e7eb !important;
            }
            [data-testid="stArrowVegaLiteChart"] svg,
            [data-testid="stVegaLiteChart"] svg,
            [data-testid="stPyplotChart"] canvas {
                background: #ffffff !important;
            }
            [data-testid="stArrowVegaLiteChart"] svg text,
            [data-testid="stVegaLiteChart"] svg text {
                fill: #263238 !important;
                color: #263238 !important;
            }
            [data-testid="stArrowVegaLiteChart"] svg line,
            [data-testid="stVegaLiteChart"] svg line {
                stroke: #cbd5e1 !important;
            }
            [data-testid="stTabs"] [role="tablist"] {
                border-bottom-color: #cbd4dc !important;
            }
            [data-testid="stTabs"] button[role="tab"] {
                color: #475569 !important;
                border-radius: 0.35rem 0.35rem 0 0 !important;
            }
            [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
                color: var(--humbertito-teal) !important;
                background: #edf0f3 !important;
                border-bottom: 2px solid var(--humbertito-teal) !important;
            }
            [data-testid="stDataFrame"],
            [data-testid="stTable"],
            [data-testid="stForm"] {
                background: #f7f9fa !important;
                border-color: #cbd4dc !important;
            }
            [data-testid="stAlert"] p {
                color: #263238 !important;
            }
            [data-testid="stTable"] {
                background: #f7f9fa !important;
                border-color: #cbd4dc !important;
            }
            [data-testid="stTable"] th {
                background: #f1f5f9 !important;
                color: #263238 !important;
                font-weight: 700 !important;
                white-space: nowrap !important;
            }
            [data-testid="stTable"] td {
                background: #ffffff !important;
                color: #263238 !important;
                border-color: #e5e7eb !important;
            }
            [data-testid="stTable"] table {
                width: 100% !important;
                border-collapse: collapse !important;
            }
            .st-key-registered_users_table [data-testid="stTable"] {
                padding: 0 !important;
                border: 0 !important;
                background: transparent !important;
                box-shadow: none !important;
                outline: none !important;
            }
            .st-key-registered_users_table [data-testid="stTable"] table {
                border-collapse: separate !important;
                border-spacing: 0 !important;
                width: 100% !important;
                box-sizing: border-box !important;
                border: 1px solid #b8cbce !important;
                border-radius: 12px !important;
                overflow: hidden !important;
                background: #dff4ef !important;
            }
            .st-key-registered_users_table [data-testid="stTable"] th {
                background: #2f8f83 !important;
                border: 0 !important;
                border-right: 1px solid #72b9b0 !important;
                border-bottom: 1px solid #72b9b0 !important;
                color: #ffffff !important;
            }
            .st-key-registered_users_table [data-testid="stTable"] td {
                background: #dff4ef !important;
                border: 0 !important;
                border-right: 1px solid #d1e1e1 !important;
                border-bottom: 1px solid #d1e1e1 !important;
                color: #203c39 !important;
            }
            .st-key-registered_users_table [data-testid="stTable"] th:last-child,
            .st-key-registered_users_table [data-testid="stTable"] td:last-child {
                border-right: 0 !important;
            }
            .st-key-registered_users_table [data-testid="stTable"] tbody tr:last-child td {
                border-bottom: 0 !important;
            }
            [data-testid="stTabs"] [role="tablist"] {
                border-bottom-color: #e5e7eb !important;
            }
            [data-testid="stAlert"] {
                background: #f8fafc !important;
                border-color: #e5e7eb !important;
            }
            [data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) [data-testid="stAlertContainer"] {
                background: #ecfdf5 !important;
                border: none !important;
            }
            [data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) [data-testid="stAlertContainer"] {
                background: #eff6ff !important;
                border: none !important;
            }
            [data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) [data-testid="stAlertContainer"] {
                background: #fffbeb !important;
                border: none !important;
            }
            [data-testid="stAlert"]:has([data-testid="stAlertContentError"]) [data-testid="stAlertContainer"] {
                background: #fef2f2 !important;
                border: none !important;
            }
            div[data-baseweb="select"] > div,
            div[data-testid="stTextInput"] input,
            div[data-testid="stNumberInput"] input,
            div[data-testid="stTextArea"] textarea {
                background: #ffffff !important;
                color: #263238 !important;
                border-color: #cbd5e1 !important;
            }
            [data-testid="stMain"] [role="group"],
            [data-testid="stForm"] [role="group"],
            [data-testid="stMain"] [data-testid="stNumberInput"] > div,
            [data-testid="stMain"] [data-testid="stTextInput"] > div,
            [data-testid="stMain"] [data-testid="stTextArea"] > div,
            [data-testid="stMain"] [data-testid="stSelectbox"] > div {
                background: #ffffff !important;
                color: #263238 !important;
                border-color: #cbd5e1 !important;
            }
            [data-testid="stForm"] label,
            [data-testid="stForm"] p,
            [data-testid="stForm"] span {
                color: #263238 !important;
            }
            [data-testid="stMain"] .alert-list {
                color: #263238 !important;
                background: rgba(45, 129, 119, 0.06) !important;
            }
            [data-testid="stForm"] button {
                background: #ffffff !important;
                color: #263238 !important;
                border-color: #cbd5e1 !important;
            }
            [data-testid="stMain"] [role="combobox"],
            [data-testid="stMain"] input,
            [data-testid="stMain"] textarea {
                background: #ffffff !important;
                color: #263238 !important;
                caret-color: #263238 !important;
            }
            [data-testid="stMain"] button {
                background: #edf0f3 !important;
                color: #263238 !important;
                border: 1px solid #cbd4dc !important;
                box-shadow: 0 2px 6px rgba(38, 50, 56, 0.08);
            }
            [data-testid="stMain"] button:hover {
                background: #e1e6ea !important;
                color: #263238 !important;
                border-color: #9aaab7 !important;
            }
            [data-testid="stMain"] [data-testid="stNumberInput"] button {
                background: #dfe5e9 !important;
                color: #263238 !important;
                border: 0 !important;
                box-shadow: none !important;
            }
            [data-testid="stMain"] [data-testid="stNumberInput"] button:hover {
                background: #cbd4dc !important;
            }
            [data-testid="stAppViewContainer"] .main button,
            [data-testid="stSidebar"] button {
                background: #ffffff !important;
                color: #263238 !important;
                border-color: #cbd5e1 !important;
            }
            [class*="st-key-quick_"] button {
                background: #edf0f3 !important;
                color: #263238 !important;
                border: 1px solid #cbd4dc !important;
                box-shadow: 0 2px 6px rgba(38, 50, 56, 0.08);
            }
            [class*="st-key-quick_"] button:hover {
                background: #e1e6ea !important;
                color: #263238 !important;
                border-color: #9aaab7 !important;
                transform: none !important;
            }
            [class*="st-key-theme_toggle"] button {
                background: #2d8177 !important;
                color: #ffffff !important;
                border-color: #2d8177 !important;
            }
            [class*="st-key-theme_toggle"] button:hover {
                background: #24665f !important;
                border-color: #24665f !important;
            }
            [data-testid="stAppViewContainer"] [data-testid="stMain"] [class*="st-key-theme_toggle"] button {
                background: #2d8177 !important;
                border-color: #2d8177 !important;
                color: #ffffff !important;
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2);
                transform: none !important;
            }
            [data-testid="stAppViewContainer"] [data-testid="stMain"] [class*="st-key-theme_toggle"] button:hover {
                background: #24665f !important;
                border-color: #24665f !important;
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2);
                transform: none !important;
            }
            [data-testid="stAppViewContainer"] [data-testid="stMain"] [class*="st-key-theme_toggle"] button,
            [data-testid="stAppViewContainer"] [data-testid="stMain"] [class*="st-key-theme_toggle"] button:hover,
            [data-testid="stAppViewContainer"] [data-testid="stMain"] [class*="st-key-theme_toggle"] button *,
            [data-testid="stAppViewContainer"] [data-testid="stMain"] [class*="st-key-theme_toggle"] button:hover * {
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
                opacity: 1 !important;
            }
            [data-testid="stSidebar"] div[data-baseweb="select"] * {
                color: #263238 !important;
            }
            [data-testid="stSidebar"] [role="group"] {
                background: #ffffff !important;
                border: 1px solid #cbd5e1 !important;
                border-radius: 0.5rem !important;
            }
            [data-testid="stSidebar"] [role="combobox"] {
                background: transparent !important;
                color: #263238 !important;
            }
            [data-testid="stSidebar"] [role="group"] button {
                background: #ffffff !important;
                color: #263238 !important;
            }
            [data-testid="stSidebar"] [data-testid="stExpander"] {
                background: #e3e8ec !important;
                border: 1px solid #aebbc6 !important;
                border-radius: 0.65rem !important;
                box-shadow: 0 2px 6px rgba(38, 50, 56, 0.08);
                transition: none !important;
                animation: none !important;
            }
            [data-testid="stSidebar"] [data-testid="stExpander"] summary,
            [data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {
                background: #e3e8ec !important;
                color: #263238 !important;
                min-height: 2.65rem;
                padding: 0.65rem 0.8rem !important;
                transition: none !important;
                transform: none !important;
            }
            [data-testid="stSidebar"] [data-testid="stExpander"] details,
            [data-testid="stSidebar"] [data-testid="stExpander"] details[open] {
                background: #e3e8ec !important;
                border: 1px solid #aebbc6 !important;
                border-radius: 0.65rem !important;
                overflow: visible !important;
                position: fixed !important;
                right: 1.25rem !important;
                bottom: 1.25rem !important;
                width: 310px !important;
                z-index: 99999 !important;
            }
            [data-testid="stSidebar"] [data-testid="stExpander"] details > div {
                background: #dce2e7 !important;
                border-top: 1px solid #aebbc6 !important;
                padding: 0.8rem !important;
                position: static !important;
                box-sizing: border-box !important;
            }
            [data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stTextInput"] input {
                background: #ffffff !important;
                color: #263238 !important;
                border-color: #b8c4ce !important;
            }
            [data-testid="stSidebar"] [data-testid="stExpander"] button {
                background: #e1e6ea !important;
                color: #263238 !important;
                border: 1px solid #b8c4ce !important;
                box-shadow: none !important;
                transform: none !important;
                transition: none !important;
            }
            [role="listbox"] {
                background: #ffffff !important;
                border: 1px solid #cbd5e1 !important;
            }
            [role="listbox"] [role="option"] {
                color: #263238 !important;
            }
            [role="listbox"] [role="option"]:hover,
            [role="listbox"] [role="option"][aria-selected="true"] {
                background: #f1f5f9 !important;
                color: #263238 !important;
            }
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4,
            [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
                color: #263238 !important;
            }
            [data-testid="stSidebar"] .sidebar-brand {
                border-left-color: var(--humbertito-teal) !important;
            }
            [data-testid="stSidebar"] .sidebar-brand-title,
            [data-testid="stSidebar"] .sidebar-brand-name {
                color: #263238 !important;
                font-family: Georgia, "Times New Roman", serif !important;
                font-size: 1.28rem !important;
                font-weight: 750 !important;
                line-height: 1.05 !important;
                letter-spacing: 0.015em !important;
            }
            [data-testid="stSidebar"] .sidebar-brand-subtitle {
                color: #64748b !important;
                font-family: "Trebuchet MS", "Segoe UI", sans-serif !important;
                font-size: 0.72rem !important;
                font-weight: 600 !important;
                letter-spacing: 0.02em !important;
                white-space: nowrap !important;
                max-width: 100% !important;
            }
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4 {
                margin-top: 1.1rem !important;
                margin-bottom: 0.85rem !important;
            }
            [data-testid="stSidebar"] [class*="st-key-menu_item_"] button {
                background: #edf0f3 !important;
                border: 1px solid #cbd4dc !important;
                border-radius: 0.65rem !important;
                color: #263238 !important;
                box-shadow: 0 2px 5px rgba(38, 50, 56, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.55);
                font-size: 0.86rem !important;
                letter-spacing: 0.01em;
            }
            [data-testid="stSidebar"] [class*="st-key-menu_item_"] button:hover {
                background: #e5e9ed !important;
                border-color: #9aaab7 !important;
                color: #a63d2d !important;
                box-shadow: 0 4px 9px rgba(38, 50, 56, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.5);
            }
            [data-testid="stSidebar"] [class*="st-key-menu_active"] button,
            [data-testid="stSidebar"] [class*="st-key-menu_active"] button:hover {
                background: #e5e9ed !important;
                border: 1px solid transparent !important;
                border-radius: 0.65rem !important;
                color: #263238 !important;
                box-shadow: 0 2px 5px rgba(38, 50, 56, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.55) !important;
            }
            [data-testid="stSidebar"] [class*="st-key-menu_active"] button:hover {
                background: #dce2e7 !important;
                border-color: transparent !important;
                color: #263238 !important;
            }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            [data-testid="stAppViewContainer"],
            [data-testid="stHeader"] {
                background: #0e1117;
            }
            [data-testid="stSidebar"] {
                background: #262730;
                border-right: 1px solid #3d3f4a;
            }
            [data-testid="stSidebar"] .sidebar-brand {
                border-left: 3px solid var(--humbertito-teal) !important;
                background: #20262d !important;
                padding: 0.85rem 1rem 1rem;
                border: 1px solid #303a43;
                border-left-width: 3px;
                border-radius: 0 0.5rem 0.5rem 0;
                box-shadow: none;
                width: 100%;
            }
            [data-testid="stSidebar"] .sidebar-brand-title,
            [data-testid="stSidebar"] .sidebar-brand-name {
                color: #8ed1c8 !important;
                font-family: Georgia, "Times New Roman", serif !important;
                font-size: 1.18rem !important;
                font-weight: 750 !important;
                line-height: 1.02 !important;
                letter-spacing: 0.01em !important;
                max-width: 100% !important;
            }
            [data-testid="stSidebar"] .sidebar-brand-subtitle {
                color: #d1d8df !important;
                font-family: "Trebuchet MS", "Segoe UI", sans-serif !important;
                font-size: 0.72rem !important;
                font-weight: 600 !important;
                letter-spacing: 0.02em !important;
                white-space: nowrap !important;
                max-width: 100% !important;
            }
            [data-testid="stMain"] h1,
            [data-testid="stMain"] h2,
            [data-testid="stMain"] h3,
            [data-testid="stMain"] p,
            [data-testid="stMain"] label,
            [data-testid="stMain"] span {
                color: #fafafa;
            }
            [data-testid="stMain"] .alert-list {
                color: #f8fafc !important;
                background: rgba(45, 129, 119, 0.14) !important;
            }
            [data-testid="stMetric"],
            [data-testid="stForm"] {
                background: #1b1d25;
                border-color: #3d3f4a;
            }
            [data-testid="stTextInput"] input,
            [data-testid="stNumberInput"] input,
            [data-testid="stTextArea"] textarea,
            [data-testid="stSelectbox"] [role="combobox"] {
                background: #0e1117 !important;
                color: #fafafa !important;
                border-color: #4a4d5a !important;
            }
            [data-testid="stMain"] button,
            [data-testid="stSidebar"] button {
                border-color: #4a4d5a;
            }
            [data-testid="stDataFrame"],
            [data-testid="stArrowVegaLiteChart"],
            [data-testid="stVegaLiteChart"],
            [data-testid="stPyplotChart"] {
                background: #1b1d25;
                border-color: #3d3f4a;
            }
            [data-testid="stTabs"] [role="tablist"] {
                border-bottom-color: #3d3f4a;
            }
            [data-testid="stSidebar"] [role="group"] {
                background: #0e1117;
                border-color: #4a4d5a;
            }
            [data-testid="stSidebar"] [data-testid="stExpander"] {
                background: #1b1d25 !important;
                border: 1px solid #4a4d5a !important;
                border-radius: 0.65rem !important;
                box-shadow: none !important;
                transition: none !important;
                animation: none !important;
            }
            [data-testid="stSidebar"] [data-testid="stExpander"] summary,
            [data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {
                background: #1b1d25 !important;
                color: #f8fafc !important;
                min-height: 2.65rem;
                padding: 0.65rem 0.8rem !important;
                transition: none !important;
                transform: none !important;
            }
            [data-testid="stSidebar"] [data-testid="stExpander"] details,
            [data-testid="stSidebar"] [data-testid="stExpander"] details[open] {
                background: #1b1d25 !important;
                border: 1px solid #667085 !important;
                border-radius: 0.65rem !important;
                overflow: visible !important;
                position: fixed !important;
                right: 1.25rem !important;
                bottom: 1.25rem !important;
                width: 310px !important;
                z-index: 99999 !important;
            }
            [data-testid="stSidebar"] [data-testid="stExpander"] details > div {
                background: #262730 !important;
                border-top: 1px solid #4a4d5a !important;
                padding: 0.8rem !important;
                position: static !important;
                box-sizing: border-box !important;
            }
            [data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stTextInput"] input {
                background: #0e1117 !important;
                color: #f8fafc !important;
                border-color: #4a4d5a !important;
            }
            [data-testid="stSidebar"] [data-testid="stExpander"] button {
                background: #262730 !important;
                color: #f8fafc !important;
                border: 1px solid #4a4d5a !important;
                box-shadow: none !important;
                transform: none !important;
                transition: none !important;
            }
            [role="listbox"] {
                background: #262730 !important;
                border-color: #4a4d5a !important;
            }
            [role="listbox"] [role="option"] {
                color: #fafafa !important;
            }
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4,
            [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
                color: #fafafa;
            }
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4 {
                margin-top: 1.45rem;
                margin-bottom: 0.85rem;
                color: #f8fafc !important;
                font-size: 1.15rem;
                letter-spacing: 0.045em;
            }
            [data-testid="stSidebar"] hr {
                border-color: #3a424b !important;
                opacity: 1 !important;
                margin: 0.85rem 0 1.25rem !important;
            }
            [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
                color: #aeb8c2 !important;
            }
            [data-testid="stSidebar"] [data-testid="stCaptionContainer"] strong {
                color: #8ed1c8 !important;
            }
            [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_item_"],
            [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_active"] {
                margin-bottom: 0.55rem !important;
            }
            [data-testid="stSidebar"] [class*="st-key-menu_item_"] button,
            [data-testid="stSidebar"] [class*="st-key-menu_active"] button,
            [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_item_"] button,
            [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_active"] button {
                background: #edf0f3 !important;
                border: 1px solid #cbd4dc !important;
                color: #263238 !important;
                box-shadow: 0 2px 6px rgba(38, 50, 56, 0.08) !important;
            }
            [data-testid="stSidebar"] [class*="st-key-menu_active"] button,
            [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_active"] button {
                border: 2px solid var(--humbertito-teal) !important;
                background: #e5e9ed !important;
                color: #263238 !important;
            }
            [data-testid="stSidebar"] [class*="st-key-menu_item_"] button:hover,
            [data-testid="stSidebar"] [class*="st-key-menu_active"] button:hover {
                background: #e1e6ea !important;
                border-color: #9aaab7 !important;
                color: #263238 !important;
            }
            [data-testid="stSidebar"] [class*="st-key-menu_item_"] button,
            [data-testid="stSidebar"] [class*="st-key-menu_active"] button {
                min-height: 3.35rem !important;
                margin-bottom: 0.3rem;
                padding: 0.85rem 0.8rem !important;
                background: #d45b45 !important;
                border: 1px solid #d45b45 !important;
                border-radius: 0.75rem !important;
                color: #ffffff !important;
                box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
                transform: none !important;
                transition: none !important;
                font-size: 0.86rem !important;
                letter-spacing: 0.01em;
            }
            [data-testid="stSidebar"] [class*="st-key-menu_item_"] button:hover,
            [data-testid="stSidebar"] [class*="st-key-menu_active"] button:hover {
                background: #c84f3b !important;
                border-color: #c84f3b !important;
                color: #ffffff !important;
                box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
                transform: none !important;
            }
            [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_item_"],
            [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_active"] {
                margin-bottom: 0.55rem !important;
                padding: 0 !important;
                transform: none !important;
                transition: none !important;
                animation: none !important;
            }
            [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_item_"] button,
            [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_active"] button {
                width: 100% !important;
                min-height: 3.1rem !important;
                background: #d45b45 !important;
                border: 1px solid #d45b45 !important;
                border-radius: 0.58rem !important;
                color: #ffffff !important;
            }
            [data-testid="stAppViewContainer"] [data-testid="stMain"] [class*="st-key-theme_toggle"] button {
                background: #d45b45 !important;
                border-color: #d45b45 !important;
                color: #ffffff !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.28);
            }
            [data-testid="stAppViewContainer"] [data-testid="stMain"] [class*="st-key-theme_toggle"] button:hover {
                background: #b94735 !important;
                border-color: #b94735 !important;
                box-shadow: 0 6px 16px rgba(0, 0, 0, 0.34);
            }
            [data-testid="stAppViewContainer"] [data-testid="stMain"] [class*="st-key-theme_toggle"] button *,
            [data-testid="stAppViewContainer"] [data-testid="stMain"] [class*="st-key-theme_toggle"] button:hover * {
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
            }
            [data-testid="stSidebar"] > div:first-child,
            [data-testid="stSidebarContent"],
            [data-testid="stSidebarUserContent"] {
                scrollbar-color: #2d8177 #151a20 !important;
            }
            [data-testid="stSidebar"] > div:first-child::-webkit-scrollbar,
            [data-testid="stSidebarContent"]::-webkit-scrollbar,
            [data-testid="stSidebarUserContent"]::-webkit-scrollbar {
                width: 6px !important;
                background: #151a20 !important;
            }
            [data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-thumb,
            [data-testid="stSidebarContent"]::-webkit-scrollbar-thumb,
            [data-testid="stSidebarUserContent"]::-webkit-scrollbar-thumb {
                background: #2d8177 !important;
                border: 1px solid #1f5d57 !important;
                border-radius: 4px !important;
            }
        </style>
    """, unsafe_allow_html=True)


st.markdown("""
<style>
/* ==========================================================
   HUMBERTITO IA — DISEÑO PREMIUM MODERNO
   ========================================================== */
:root {
    --hb-accent: #2f8f83;
    --hb-accent-2: #55b8a9;
    --hb-dark-bg: #0a1016;
    --hb-dark-surface: #121a23;
    --hb-dark-surface-2: #18232e;
    --hb-dark-border: rgba(148,163,184,.15);
    --hb-dark-text: #edf5f7;
    --hb-dark-muted: #91a3ad;
}
[data-testid="stAppViewContainer"] {
    background:
      radial-gradient(circle at 92% 0%, rgba(47,143,131,.12), transparent 25rem),
      radial-gradient(circle at 0% 100%, rgba(74,105,150,.08), transparent 23rem),
      var(--hb-dark-bg);
}
[data-testid="stMainBlockContainer"] {
    max-width: 1480px !important;
    padding: 2.25rem 2.6rem 3.5rem !important;
}
.hb-page-header {
    display:flex; align-items:flex-end; justify-content:space-between;
    gap:1rem; margin:0 0 1.45rem;
}
.hb-page-title {
    margin:0; font-family:Georgia,"Times New Roman",serif;
    font-size:clamp(1.8rem,3vw,2.55rem); font-weight:800;
    letter-spacing:-.035em; color:var(--hb-dark-text);
}
.hb-page-subtitle {
    margin:.35rem 0 0; color:var(--hb-dark-muted);
    font-size:.91rem; line-height:1.5;
}
.hb-status-pill {
    display:inline-flex; align-items:center; gap:.45rem;
    padding:.48rem .78rem; border:1px solid rgba(85,184,169,.24);
    border-radius:999px; background:rgba(47,143,131,.10);
    color:#8ed9ce; font-size:.76rem; font-weight:750; white-space:nowrap;
}
.hb-status-dot {
    width:.48rem; height:.48rem; border-radius:50%;
    background:#55b8a9; box-shadow:0 0 0 4px rgba(85,184,169,.10);
}
[data-testid="stMetric"] {
    position:relative; overflow:hidden; min-height:8.25rem !important;
    padding:1.15rem 1.2rem !important;
    border:1px solid var(--hb-dark-border) !important;
    border-radius:15px !important;
    background:linear-gradient(145deg,rgba(255,255,255,.055),rgba(255,255,255,.018)) !important;
    box-shadow:0 14px 32px rgba(0,0,0,.15) !important;
}
[data-testid="stMetric"]::after {
    content:""; position:absolute; width:7rem; height:7rem;
    right:-3rem; top:-3rem; border-radius:50%;
    background:rgba(47,143,131,.10); pointer-events:none;
}
[data-testid="stMetricLabel"] {
    color:var(--hb-dark-muted) !important; font-size:.76rem !important;
    font-weight:700 !important; text-transform:uppercase; letter-spacing:.055em;
}
[data-testid="stMetricValue"] {
    color:var(--hb-dark-text) !important;
    font-size:clamp(1.45rem,2.3vw,2rem) !important;
    font-weight:800 !important; letter-spacing:-.025em;
}
[data-testid="stForm"] {
    padding:1.3rem !important; border:1px solid var(--hb-dark-border) !important;
    border-radius:15px !important; background:rgba(18,26,35,.84) !important;
    box-shadow:0 16px 35px rgba(0,0,0,.13) !important;
}
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-baseweb="select"] > div {
    border-radius:9px !important; border-color:rgba(148,163,184,.20) !important;
    background:#101821 !important; color:var(--hb-dark-text) !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color:rgba(85,184,169,.70) !important;
    box-shadow:0 0 0 3px rgba(47,143,131,.14) !important;
}
[data-testid="stMain"] button {
    border-radius:9px !important; font-weight:700 !important;
}
[data-testid="stMain"] button[kind="primary"],
[data-testid="stMain"] button[kind="primaryFormSubmit"] {
    background:linear-gradient(135deg,#2f8f83,#26776e) !important;
    border-color:#2f8f83 !important; color:#fff !important;
    box-shadow:0 7px 18px rgba(47,143,131,.20) !important;
}
[data-testid="stMain"] button[kind="primary"]:hover,
[data-testid="stMain"] button[kind="primaryFormSubmit"]:hover {
    background:linear-gradient(135deg,#3ca193,#2f8178) !important;
    border-color:#3ca193 !important; transform:none !important; box-shadow:0 7px 18px rgba(47,143,131,.20) !important;
}
[data-testid="stTabs"] [role="tablist"] {
    gap:.3rem; padding:.25rem; border:1px solid var(--hb-dark-border);
    border-radius:11px; background:rgba(255,255,255,.025);
}
[data-testid="stTabs"] button[role="tab"] {
    border-radius:8px !important; color:var(--hb-dark-muted) !important;
    font-weight:700 !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color:#dff8f4 !important; background:rgba(47,143,131,.16) !important;
}
[data-testid="stDataFrame"], [data-testid="stTable"] {
    border:1px solid var(--hb-dark-border) !important;
    border-radius:13px !important; overflow:hidden !important;
    box-shadow:0 10px 25px rgba(0,0,0,.10);
}
[data-testid="stTable"] th {
    background:#17222c !important; color:#b9d4d1 !important;
    font-weight:750 !important; border-bottom:1px solid rgba(148,163,184,.18) !important;
}
[data-testid="stTable"] td {
    background:#111a23 !important; color:#dbe5e8 !important;
    border-bottom:1px solid rgba(148,163,184,.10) !important;
}
[data-testid="stAlertContainer"] {
    border-radius:11px !important; border:1px solid rgba(148,163,184,.12) !important;
}
[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#111820 0%,#0d141b 100%) !important;
    border-right:1px solid rgba(148,163,184,.12) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding:4.6rem .9rem 1rem !important;
}
[data-testid="stSidebar"] .sidebar-brand {
    margin-bottom:.9rem !important; padding:1rem !important;
    border:1px solid rgba(85,184,169,.16) !important;
    border-left:3px solid #3fa395 !important; border-radius:12px !important;
    background:linear-gradient(145deg,rgba(47,143,131,.09),rgba(255,255,255,.025)) !important;
}
[data-testid="stSidebar"] .user-card {
    border:1px solid rgba(148,163,184,.13) !important;
    border-radius:12px !important; background:rgba(255,255,255,.035) !important;
}
[data-testid="stSidebar"] .stButton > button {
    border:1px solid transparent !important; border-radius:9px !important;
    background:transparent !important; color:#aebdc5 !important; font-weight:650 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background:rgba(47,143,131,.09) !important;
    border-color:rgba(47,143,131,.16) !important; color:#d8f1ed !important;
}
[data-testid="stSidebar"] [class*="st-key-menu_active"] button {
    background:linear-gradient(135deg,rgba(47,143,131,.95),rgba(38,119,110,.95)) !important;
    border-color:rgba(120,215,202,.25) !important; color:#fff !important;
    box-shadow:0 7px 18px rgba(47,143,131,.18) !important;
}
::-webkit-scrollbar { width:7px; height:7px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:#3b4b56; border-radius:99px; }
::-webkit-scrollbar-thumb:hover { background:#536773; }

/* ---------- CLARO ---------- */
body:has(.hb-light-mode) [data-testid="stAppViewContainer"] {
    background:
      radial-gradient(circle at 92% 0%,rgba(47,143,131,.10),transparent 24rem),
      linear-gradient(180deg,#f9fbfc 0%,#f0f4f5 100%) !important;
}
body:has(.hb-light-mode) .hb-page-title { color:#17262d; }
body:has(.hb-light-mode) .hb-page-subtitle { color:#687980; }
body:has(.hb-light-mode) [data-testid="stMetric"] {
    border-color:#e0e8eb !important; background:rgba(255,255,255,.92) !important;
    box-shadow:0 12px 28px rgba(34,52,61,.07) !important;
}
body:has(.hb-light-mode) [data-testid="stMetricLabel"] { color:#71818a !important; }
body:has(.hb-light-mode) [data-testid="stMetricValue"] { color:#17262d !important; }
body:has(.hb-light-mode) [data-testid="stForm"] {
    background:rgba(255,255,255,.94) !important; border-color:#e0e7ea !important;
    box-shadow:0 12px 28px rgba(34,52,61,.06) !important;
}
body:has(.hb-light-mode) [data-testid="stTextInput"] input,
body:has(.hb-light-mode) [data-testid="stNumberInput"] input,
body:has(.hb-light-mode) [data-testid="stTextArea"] textarea,
body:has(.hb-light-mode) [data-baseweb="select"] > div {
    background:#fff !important; color:#24343b !important; border-color:#d4dfe3 !important;
}
body:has(.hb-light-mode) [data-testid="stTable"] th {
    background:#edf4f4 !important; color:#29434a !important;
}
body:has(.hb-light-mode) [data-testid="stTable"] td {
    background:#fff !important; color:#33474f !important;
}
body:has(.hb-light-mode) [data-testid="stTabs"] [role="tablist"] {
    background:rgba(255,255,255,.78); border-color:#e0e7ea;
}
body:has(.hb-light-mode) [data-testid="stTabs"] button[role="tab"] { color:#71818a !important; }
body:has(.hb-light-mode) [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color:#246d65 !important; background:#e8f4f2 !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] {
    background:#fff !important; border-right-color:#e1e8eb !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] .sidebar-brand {
    background:linear-gradient(145deg,#f0f8f7,#f9fbfb) !important;
    border-color:#dcebe9 !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] .user-card {
    background:#f7fafb !important; border-color:#e0e8eb !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] .stButton > button { color:#50626a !important; }
body:has(.hb-light-mode) [data-testid="stSidebar"] .stButton > button:hover {
    background:#eef7f5 !important; color:#246d65 !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] [class*="st-key-menu_active"] button {
    background:linear-gradient(135deg,#2f8f83,#27776f) !important; color:#fff !important;
}
body:has(.hb-light-mode) .hb-status-pill {
    color:#27776f; background:#e8f5f2; border-color:#cde7e2;
}
@media (max-width:900px) {
    [data-testid="stMainBlockContainer"] { padding:1.4rem 1rem 2.5rem !important; }
    .hb-page-header { align-items:flex-start; flex-direction:column; }
}
</style>
""", unsafe_allow_html=True)


if st.session_state.tema_blanco:
    st.markdown("""
        <style>
            [data-testid="stSidebar"] .sidebar-brand {
                background: #f7f9fa !important;
                border: 1px solid #cbd4dc !important;
                border-left: 3px solid #2d8177 !important;
                border-radius: 0 0.55rem 0.55rem 0 !important;
                box-sizing: border-box !important;
            }
            [data-testid="stSidebar"] .sidebar-brand-name {
                color: #263238 !important;
            }
            [data-testid="stSidebar"] .sidebar-brand-subtitle {
                color: #64748b !important;
            }
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4 {
                color: #263238 !important;
                margin-top: 1.35rem !important;
                margin-bottom: 0.9rem !important;
            }
            [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_item_"],
            [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_active"] {
                margin-bottom: 0.55rem !important;
                padding: 0 !important;
            }
            [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_item_"] button {
                background: #e5e9ed !important;
                border: 1px solid #c1ccd6 !important;
                border-radius: 0.7rem !important;
                color: #263238 !important;
                min-height: 3.15rem !important;
                box-shadow: 0 2px 6px rgba(38, 50, 56, 0.1) !important;
            }
            [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_active"] button {
                background: #dce5e8 !important;
                border: 2px solid #2d8177 !important;
                color: #263238 !important;
                min-height: 3.15rem !important;
            }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            [data-testid="stSidebar"] .sidebar-brand {
                background: #20262d !important;
                border: 1px solid #3b4650 !important;
                border-left: 3px solid #2d8177 !important;
                border-radius: 0 0.55rem 0.55rem 0 !important;
                box-sizing: border-box !important;
            }
            [data-testid="stSidebar"] .sidebar-brand-name {
                color: #8ed1c8 !important;
            }
            [data-testid="stSidebar"] .sidebar-brand-subtitle {
                color: #d1d8df !important;
            }
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4 {
                color: #f8fafc !important;
                margin-top: 1.35rem !important;
                margin-bottom: 0.9rem !important;
            }
            [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_item_"],
            [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_active"] {
                margin-bottom: 0.55rem !important;
                padding: 0 !important;
            }
            [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_item_"] button {
                background: #d45b45 !important;
                border: 1px solid #d45b45 !important;
                border-radius: 0.7rem !important;
                color: #ffffff !important;
                min-height: 3.15rem !important;
                box-shadow: 0 3px 8px rgba(0, 0, 0, 0.22) !important;
            }
            [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_active"] button {
                background: #d45b45 !important;
                border: 2px solid #8ed1c8 !important;
                color: #ffffff !important;
                min-height: 3.15rem !important;
            }
        </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
        [data-testid="stSidebar"] > div:first-child {
            padding: 0.75rem 1.875rem 1rem !important;
            overflow: hidden !important;
        }
        [data-testid="stSidebar"] .sidebar-brand {
            width: 100% !important;
            min-height: 7rem;
            box-sizing: border-box !important;
            margin: 0 !important;
            padding: 0.85rem 0.95rem 0.95rem !important;
            position: sticky !important;
            top: 0 !important;
            z-index: 30 !important;
        }
        [data-testid="stSidebar"] .sidebar-brand-title,
        [data-testid="stSidebar"] .sidebar-brand-name {
            display: block !important;
            white-space: nowrap !important;
            max-width: 100% !important;
            font-size: 1.08rem !important;
            line-height: 1.04 !important;
            letter-spacing: 0 !important;
            overflow: hidden !important;
        }
        [data-testid="stSidebar"] .sidebar-brand-subtitle {
            display: block !important;
            white-space: nowrap !important;
            margin-top: 0.55rem !important;
            max-width: 100% !important;
            font-size: 0.68rem !important;
            line-height: 1.2 !important;
            letter-spacing: 0 !important;
            overflow: hidden !important;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4 {
            margin: 1.3rem 0 0.85rem !important;
            font-size: 1rem !important;
            line-height: 1.2 !important;
            letter-spacing: 0.045em !important;
        }
        [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_item_"],
        [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_active"] {
            width: 100% !important;
            margin: 0 0 0.55rem !important;
            padding: 0 !important;
        }
        [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_item_"] button,
        [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_active"] button {
            width: 100% !important;
            min-height: 3.15rem !important;
            margin: 0 !important;
            padding: 0.7rem 0.75rem !important;
            box-sizing: border-box !important;
            font-size: 0.86rem !important;
            line-height: 1.2 !important;
            transform: none !important;
            transition: none !important;
            animation: none !important;
        }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            margin: 0.3rem 0 1.05rem !important;
            font-size: 0.78rem !important;
            line-height: 1.35 !important;
        }
        [data-testid="stSidebar"] hr {
            margin: 0.85rem 0 1.25rem !important;
        }
        @media (max-width: 640px) {
            [data-testid="stSidebarCollapseButton"],
            [data-testid="stSidebarCollapsedControl"] {
                top: 0.65rem !important;
                left: auto !important;
                right: 0.75rem !important;
                display: block !important;
                z-index: 1000000 !important;
                pointer-events: auto !important;
            }
            [data-testid="stSidebarCollapseButton"] button,
            [data-testid="stSidebarCollapsedControl"] button {
                width: 2.75rem !important;
                height: 2.25rem !important;
                min-width: 2.75rem !important;
                min-height: 2.25rem !important;
                padding: 0 !important;
                touch-action: manipulation !important;
            }
            button[aria-label*="open sidebar" i],
            button[aria-label*="close sidebar" i],
            button[aria-label*="expand sidebar" i],
            button[aria-label*="collapse sidebar" i],
            button[aria-label*="abrir barra lateral" i],
            button[aria-label*="cerrar barra lateral" i] {
                top: 0.65rem !important;
                left: auto !important;
                right: 0.75rem !important;
            }
            [data-testid="stSidebar"] {
                width: 100vw !important;
                min-width: 100vw !important;
                max-width: 100vw !important;
                height: 100dvh !important;
                overflow: hidden !important;
            }
            [data-testid="stSidebar"] > div:first-child,
            [data-testid="stSidebarContent"],
            [data-testid="stSidebarUserContent"] {
                width: 100% !important;
                padding: 1rem 1rem 1.25rem !important;
                box-sizing: border-box !important;
                height: 100dvh !important;
                max-height: 100dvh !important;
                overflow-y: auto !important;
                overflow-x: hidden !important;
                -webkit-overflow-scrolling: touch;
                overscroll-behavior-y: contain;
                scrollbar-width: thin;
                touch-action: pan-y;
            }
            [data-testid="stSidebarContent"]::-webkit-scrollbar,
            [data-testid="stSidebarUserContent"]::-webkit-scrollbar,
            [data-testid="stSidebar"] > div:first-child::-webkit-scrollbar {
                width: 5px;
            }
            [data-testid="stSidebarContent"]::-webkit-scrollbar-thumb,
            [data-testid="stSidebarUserContent"]::-webkit-scrollbar-thumb,
            [data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-thumb {
                background: rgba(100, 116, 139, 0.65);
                border-radius: 3px;
            }
            [data-testid="stSidebar"] .sidebar-brand {
                min-height: auto !important;
                padding: 0.85rem 0.9rem 0.9rem !important;
                position: sticky !important;
                top: 0 !important;
                z-index: 30 !important;
            }
            [data-testid="stSidebar"] .sidebar-brand-title,
            [data-testid="stSidebar"] .sidebar-brand-name {
                font-size: 1.02rem !important;
            }
            [data-testid="stSidebar"] .sidebar-brand-subtitle {
                font-size: 0.68rem !important;
                white-space: nowrap !important;
            }
            [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_item_"],
            [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_active"] {
                width: 100% !important;
            }
            [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_item_"] button,
            [data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-menu_active"] button {
                min-height: 2.9rem !important;
                font-size: 0.84rem !important;
            }
            [data-testid="stSidebar"] [data-testid="stExpander"] details,
            [data-testid="stSidebar"] [data-testid="stExpander"] details[open] {
                right: 1rem !important;
                bottom: 1rem !important;
                width: calc(100vw - 2rem) !important;
                max-width: 22rem !important;
            }
            [data-testid="stSidebar"] [data-testid="stExpander"] details > div {
                max-height: 70dvh !important;
                overflow-y: auto !important;
                -webkit-overflow-scrolling: touch;
            }
            [data-testid="stMainBlockContainer"] {
                padding: 1rem 0.9rem 2rem !important;
                width: 100% !important;
                box-sizing: border-box !important;
            }
            [data-testid="stMain"] h1 {
                font-size: 1.65rem !important;
            }
            [data-testid="stMain"] h2 {
                font-size: 1.35rem !important;
            }
            [data-testid="stMain"] [data-testid="stForm"] {
                padding: 0.85rem !important;
                border-radius: 0.55rem !important;
            }
            [data-testid="stMain"] input,
            [data-testid="stMain"] textarea,
            [data-testid="stMain"] [role="combobox"] {
                max-width: 100% !important;
                font-size: 1rem !important;
            }
            [data-testid="stMain"] button {
                min-height: 2.8rem !important;
                max-width: 100% !important;
                font-size: 0.9rem !important;
            }
            [data-testid="stMain"] [data-testid="stButton"] button,
            [data-testid="stMain"] [data-testid="stFormSubmitButton"] button {
                width: 100% !important;
            }
            [data-testid="stTabs"] [role="tablist"] {
                overflow-x: auto !important;
                justify-content: flex-start !important;
                scrollbar-width: none;
                -webkit-overflow-scrolling: touch;
                touch-action: pan-x;
            }
            [data-testid="stTabs"] [role="tablist"]::-webkit-scrollbar {
                display: none;
            }
            [data-testid="stTabs"] button[role="tab"] {
                flex: 0 0 auto !important;
                white-space: nowrap !important;
            }
            [data-testid="stAlertContainer"] {
                padding: 0.75rem !important;
                min-height: 2.75rem !important;
            }
            [data-testid="stMain"] [data-testid="stMetric"] {
                min-height: 5.4rem !important;
                padding: 0.75rem !important;
            }
            [data-testid="stMain"] [data-testid="stDataFrame"],
            [data-testid="stMain"] [data-testid="stTable"] {
                overflow-x: auto !important;
                -webkit-overflow-scrolling: touch;
                touch-action: pan-x pan-y;
            }
        }
    </style>
""", unsafe_allow_html=True)


# ==========================================================
# SIDEBAR FINAL - DISEÑO PROFESIONAL + SCROLL ESTABLE
# ==========================================================

st.markdown("""
<style>
    /* Contenedor: un único scroll vertical */
    [data-testid="stSidebar"] {
        width: 292px !important;
        min-width: 292px !important;
        max-width: 292px !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        height: 100dvh !important;
        max-height: 100dvh !important;
        padding: 0.85rem 0.85rem 1.2rem !important;
        box-sizing: border-box !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        overscroll-behavior-y: contain !important;
        scrollbar-width: thin !important;
        scrollbar-gutter: stable !important;
    }
    [data-testid="stSidebarContent"],
    [data-testid="stSidebarUserContent"] {
        height: auto !important;
        min-height: 0 !important;
        padding: 0 !important;
        overflow: visible !important;
    }
    [data-testid="stSidebar"] > div:first-child::-webkit-scrollbar { width: 7px !important; }
    [data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-track { background: transparent !important; }
    [data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-thumb {
        background: rgba(148,163,184,0.40) !important;
        border-radius: 999px !important;
    }
    [data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-thumb:hover {
        background: rgba(148,163,184,0.60) !important;
    }

    /* Marca */
    [data-testid="stSidebar"] .sidebar-brand {
        width: 100% !important;
        margin: 0 0 0.75rem !important;
        padding: 0.88rem 0.9rem !important;
        box-sizing: border-box !important;
        position: static !important;
        border: 1px solid rgba(148,163,184,0.18) !important;
        border-left: 3px solid #2d8177 !important;
        border-radius: 0 10px 10px 0 !important;
        background: rgba(255,255,255,0.035) !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.06) !important;
    }
    [data-testid="stSidebar"] .sidebar-brand-kicker {
        margin: 0 0 0.32rem !important;
        color: #8995a3 !important;
        font-size: 0.57rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
    }
    [data-testid="stSidebar"] .sidebar-brand-title,
    [data-testid="stSidebar"] .sidebar-brand-name {
        display: block !important;
        margin: 0 !important;
        max-width: 100% !important;
        white-space: normal !important;
        overflow: visible !important;
        font-family: Georgia, "Times New Roman", serif !important;
        font-size: 1.02rem !important;
        line-height: 1.06 !important;
        font-weight: 800 !important;
        letter-spacing: 0 !important;
    }
    [data-testid="stSidebar"] .sidebar-brand-subtitle {
        display: block !important;
        margin: 0.48rem 0 0 !important;
        max-width: 100% !important;
        white-space: normal !important;
        font-size: 0.66rem !important;
        line-height: 1.3 !important;
    }

    /* Perfil */
    [data-testid="stSidebar"] .user-card {
        width: 100% !important;
        margin: 0 0 0.62rem !important;
        padding: 0.75rem 0.8rem !important;
        box-sizing: border-box !important;
        border: 1px solid rgba(148,163,184,0.16) !important;
        border-radius: 10px !important;
        background: rgba(255,255,255,0.035) !important;
    }
    [data-testid="stSidebar"] .user-card-top {
        display: flex !important;
        align-items: center !important;
        gap: 0.35rem !important;
        margin-bottom: 0.30rem !important;
    }
    [data-testid="stSidebar"] .user-status-dot {
        width: 7px !important;
        height: 7px !important;
        flex: 0 0 7px !important;
        border-radius: 50% !important;
        background: #58b9a9 !important;
        box-shadow: 0 0 0 3px rgba(88,185,169,0.11) !important;
    }
    [data-testid="stSidebar"] .user-status-text {
        font-size: 0.57rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.10em !important;
        opacity: 0.60 !important;
    }
    [data-testid="stSidebar"] .user-name {
        margin: 0 !important;
        font-size: 0.90rem !important;
        line-height: 1.25 !important;
        font-weight: 750 !important;
        overflow-wrap: anywhere !important;
    }
    [data-testid="stSidebar"] .user-role {
        margin-top: 0.12rem !important;
        font-size: 0.69rem !important;
        line-height: 1.3 !important;
        opacity: 0.62 !important;
    }

    /* Logout */
    [data-testid="stSidebar"] [class*="st-key-cerrar_sesion"] button {
        width: 100% !important;
        min-height: 2.25rem !important;
        margin: 0 !important;
        padding: 0.48rem 0.7rem !important;
        border: 1px solid rgba(148,163,184,0.16) !important;
        border-radius: 8px !important;
        background: transparent !important;
        color: inherit !important;
        justify-content: center !important;
        font-size: 0.74rem !important;
        font-weight: 650 !important;
        box-shadow: none !important;
        transform: none !important;
    }
    [data-testid="stSidebar"] [class*="st-key-cerrar_sesion"] button:hover {
        background: rgba(212,91,69,0.09) !important;
        border-color: rgba(212,91,69,0.28) !important;
        color: #e47761 !important;
    }

    /* Encabezados de sección */
    [data-testid="stSidebar"] .sidebar-section-title {
        margin: 0.02rem 0 0.52rem !important;
        padding-left: 0.1rem !important;
        font-size: 0.63rem !important;
        line-height: 1.2 !important;
        font-weight: 800 !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        opacity: 0.50 !important;
    }

    /* BOTONES NORMALES: neutros, no rojos */
    [data-testid="stSidebar"] [class*="st-key-menu_item_"] button {
        width: 100% !important;
        min-height: 2.48rem !important;
        margin: 0 0 0.30rem !important;
        padding: 0.54rem 0.72rem !important;
        box-sizing: border-box !important;
        border: 1px solid rgba(148,163,184,0.12) !important;
        border-radius: 8px !important;
        background: rgba(255,255,255,0.022) !important;
        color: inherit !important;
        justify-content: flex-start !important;
        text-align: left !important;
        font-size: 0.78rem !important;
        font-weight: 620 !important;
        line-height: 1.2 !important;
        box-shadow: none !important;
        transform: none !important;
    }
    [data-testid="stSidebar"] [class*="st-key-menu_item_"] button:hover {
        background: rgba(45,129,119,0.10) !important;
        border-color: rgba(45,129,119,0.30) !important;
        color: inherit !important;
    }

    /* SOLO el elemento activo usa el color de énfasis */
    [data-testid="stSidebar"] [class*="st-key-menu_active"] button {
        width: 100% !important;
        min-height: 2.48rem !important;
        margin: 0 0 0.30rem !important;
        padding: 0.54rem 0.72rem !important;
        border: 1px solid #2d8177 !important;
        border-radius: 8px !important;
        background: #2d8177 !important;
        color: #ffffff !important;
        justify-content: flex-start !important;
        text-align: left !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
        box-shadow: 0 4px 11px rgba(45,129,119,0.18) !important;
        transform: none !important;
    }
    [data-testid="stSidebar"] [class*="st-key-menu_active"] button:hover {
        background: #24665f !important;
        border-color: #24665f !important;
        color: #ffffff !important;
    }

    /* Separadores */
    [data-testid="stSidebar"] hr {
        margin: 0.62rem 0 0.75rem !important;
        opacity: 0.18 !important;
    }

    /* Administración */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        width: 100% !important;
        margin: 0 !important;
        border: 1px solid rgba(148,163,184,0.15) !important;
        border-radius: 9px !important;
        overflow: hidden !important;
        background: rgba(255,255,255,0.018) !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary {
        min-height: 2.42rem !important;
        padding: 0.52rem 0.68rem !important;
        font-size: 0.74rem !important;
        font-weight: 680 !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stTextInput"] input {
        font-size: 0.75rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] .stButton > button {
        justify-content: center !important;
        text-align: center !important;
        font-size: 0.73rem !important;
    }

    /* Estabilidad: sin animaciones/transformaciones durante navegación */
    [data-testid="stSidebar"] [data-testid="stElementContainer"],
    [data-testid="stSidebar"] [data-testid="stButton"],
    [data-testid="stSidebar"] [data-testid="stButton"] button {
        animation: none !important;
        transform: none !important;
        will-change: auto !important;
    }

    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            width: 282px !important;
            min-width: 282px !important;
            max-width: 282px !important;
        }
        [data-testid="stSidebar"] > div:first-child {
            height: 100dvh !important;
            max-height: 100dvh !important;
            padding: 0.72rem 0.70rem 1rem !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
            -webkit-overflow-scrolling: touch !important;
            touch-action: pan-y !important;
        }
        [data-testid="stSidebar"] [class*="st-key-menu_item_"] button,
        [data-testid="stSidebar"] [class*="st-key-menu_active"] button {
            min-height: 2.58rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

if st.session_state.tema_blanco:
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { background: #f7f9fa !important; color: #263238 !important; }
        [data-testid="stSidebar"] .sidebar-brand { background: #ffffff !important; border-color: #dbe3e8 !important; border-left-color: #2d8177 !important; box-shadow: 0 6px 16px rgba(38,50,56,0.05) !important; }
        [data-testid="stSidebar"] .sidebar-brand-kicker { color: #718096 !important; }
        [data-testid="stSidebar"] .sidebar-brand-title, [data-testid="stSidebar"] .sidebar-brand-name { color: #263238 !important; }
        [data-testid="stSidebar"] .sidebar-brand-subtitle { color: #64748b !important; }
        [data-testid="stSidebar"] .user-card { background: #ffffff !important; border-color: #dbe3e8 !important; }
        [data-testid="stSidebar"] [class*="st-key-menu_item_"] button { background: #ffffff !important; border-color: #e0e7eb !important; color: #263238 !important; }
        [data-testid="stSidebar"] [class*="st-key-menu_item_"] button:hover { background: #edf7f5 !important; border-color: #b9d9d4 !important; color: #24665f !important; }
        [data-testid="stSidebar"] [class*="st-key-menu_active"] button { background: #2d8177 !important; border-color: #2d8177 !important; color: #ffffff !important; }
        [data-testid="stSidebar"] [data-testid="stExpander"] { background: #ffffff !important; border-color: #dbe3e8 !important; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { background: #22252e !important; color: #eef2f5 !important; }
        [data-testid="stSidebar"] .sidebar-brand { background: #1f242b !important; border-color: #35404a !important; border-left-color: #2d8177 !important; }
        [data-testid="stSidebar"] .sidebar-brand-kicker { color: #8995a3 !important; }
        [data-testid="stSidebar"] .sidebar-brand-title, [data-testid="stSidebar"] .sidebar-brand-name { color: #8ed1c8 !important; }
        [data-testid="stSidebar"] .sidebar-brand-subtitle { color: #d1d8df !important; }
        [data-testid="stSidebar"] .user-card { background: #2a2d36 !important; border-color: #3b404b !important; }
        [data-testid="stSidebar"] [class*="st-key-menu_item_"] button { background: rgba(255,255,255,0.022) !important; border-color: #353b46 !important; color: #edf1f4 !important; }
        [data-testid="stSidebar"] [class*="st-key-menu_item_"] button:hover { background: rgba(45,129,119,0.12) !important; border-color: rgba(45,129,119,0.32) !important; color: #ffffff !important; }
        [data-testid="stSidebar"] [class*="st-key-menu_active"] button { background: #2d8177 !important; border-color: #2d8177 !important; color: #ffffff !important; }
        [data-testid="stSidebar"] [data-testid="stExpander"] { background: #252931 !important; border-color: #3a414c !important; }
    </style>
    """, unsafe_allow_html=True)



# ==========================================================
# INTERFAZ PREMIUM - HUMBERTITO IA
# ==========================================================

st.markdown("""
<style>
/* ---------- ESTRUCTURA GENERAL ---------- */
[data-testid="stMainBlockContainer"] {
    max-width: 1480px !important;
    margin-top: -3rem !important;
    padding: 0 2.2rem 3rem !important;
}
[data-testid="stMain"] {
    min-width: 0;
    padding-top: 0 !important;
}
[data-testid="stAppViewContainer"] {
    background: #f4f7f8;
}
[data-testid="stHeader"] {
    background: transparent !important;
}

/* ---------- TITULOS ---------- */
[data-testid="stMain"] h1 {
    font-size: clamp(1.8rem, 2.8vw, 2.55rem) !important;
    font-weight: 800 !important;
    letter-spacing: -0.035em !important;
    margin-bottom: 0.2rem !important;
}
[data-testid="stMain"] h2 {
    font-size: clamp(1.35rem, 2vw, 1.8rem) !important;
    font-weight: 780 !important;
    letter-spacing: -0.025em !important;
    border: 0 !important;
    padding-bottom: 0.2rem !important;
}
[data-testid="stMain"] h3 {
    font-weight: 720 !important;
}

/* ---------- METRICAS ---------- */
[data-testid="stMetric"] {
    position: relative !important;
    min-height: 7.2rem !important;
    padding: 1.05rem 1.15rem !important;
    border: 1px solid rgba(45,129,119,0.16) !important;
    border-radius: 16px !important;
    background: rgba(255,255,255,0.92) !important;
    box-shadow: 0 8px 24px rgba(15,23,42,0.07) !important;
    overflow: hidden !important;
}
[data-testid="stMetric"]::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    width: 4px;
    height: 100%;
    background: #2d8177;
}
[data-testid="stMetricLabel"] {
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.055em !important;
    opacity: 0.68 !important;
}
[data-testid="stMetricValue"] {
    font-size: clamp(1.45rem, 2.5vw, 2.05rem) !important;
    font-weight: 800 !important;
}

/* ---------- TARJETAS RAPIDAS ---------- */
.quick-card {
    min-height: 10rem !important;
    padding: 1.2rem !important;
    border: 1px solid rgba(45,129,119,0.15) !important;
    border-radius: 16px !important;
    background: linear-gradient(145deg, rgba(255,255,255,0.98), rgba(244,248,248,0.96)) !important;
    box-shadow: 0 8px 24px rgba(15,23,42,0.06) !important;
}
.quick-card strong {
    font-size: 1rem !important;
    font-weight: 780 !important;
}

/* ---------- FORMULARIOS ---------- */
[data-testid="stForm"] {
    border: 1px solid rgba(148,163,184,0.25) !important;
    border-radius: 16px !important;
    background: rgba(255,255,255,0.72) !important;
    box-shadow: 0 10px 28px rgba(15,23,42,0.05) !important;
    padding: 1.25rem !important;
}
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-baseweb="select"] > div {
    border-radius: 10px !important;
}

/* ---------- BOTONES PRINCIPALES ---------- */
[data-testid="stMain"] button {
    border-radius: 10px !important;
    font-weight: 700 !important;
}
[data-testid="stMain"] button[kind="primary"],
[data-testid="stMain"] button[kind="primaryFormSubmit"] {
    background: #2d8177 !important;
    border-color: #2d8177 !important;
    color: #ffffff !important;
    box-shadow: 0 5px 14px rgba(45,129,119,0.20) !important;
}
[data-testid="stMain"] button[kind="primary"]:hover,
[data-testid="stMain"] button[kind="primaryFormSubmit"]:hover {
    background: #24665f !important;
    border-color: #24665f !important;
}

/* ---------- TABLAS ---------- */
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    border: 1px solid #dce4e7 !important;
    border-radius: 14px !important;
    overflow: hidden !important;
    box-shadow: 0 7px 20px rgba(15,23,42,0.05) !important;
}
[data-testid="stTable"] th {
    font-size: 0.76rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.045em !important;
    font-weight: 800 !important;
}
[data-testid="stTable"] td,
[data-testid="stTable"] th {
    padding: 0.72rem 0.8rem !important;
}

/* ---------- ALERTAS ---------- */
[data-testid="stAlert"] {
    border-radius: 12px !important;
}

/* ---------- EXPANDERS ---------- */
[data-testid="stExpander"] {
    border-radius: 12px !important;
    border: 1px solid rgba(148,163,184,0.25) !important;
    overflow: hidden !important;
}

/* ---------- SIDEBAR ---------- */
[data-testid="stSidebar"] {
    width: 292px !important;
    min-width: 292px !important;
    max-width: 292px !important;
    background: #182027 !important;
    border-right: 1px solid #2b3942 !important;
}
[data-testid="stSidebar"] > div:first-child {
    height: 100dvh !important;
    max-height: 100dvh !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    padding: 0.85rem 0.8rem 1rem !important;
    scrollbar-width: thin !important;
    scrollbar-color: #50616b transparent !important;
}
[data-testid="stSidebar"] .sidebar-brand {
    padding: 1rem 1rem 1.1rem !important;
    margin-bottom: 0.8rem !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-left: 3px solid #2d8177 !important;
    border-radius: 0 14px 14px 0 !important;
    background: linear-gradient(145deg, rgba(255,255,255,0.055), rgba(255,255,255,0.018)) !important;
}
[data-testid="stSidebar"] .sidebar-brand-kicker {
    font-size: 0.62rem !important;
    letter-spacing: 0.14em !important;
    font-weight: 800 !important;
    color: #7fbab4 !important;
    margin-bottom: 0.35rem !important;
}
[data-testid="stSidebar"] .sidebar-brand-name {
    font-size: 1.08rem !important;
    font-weight: 800 !important;
    line-height: 1.12 !important;
    color: #f5f8f9 !important;
}
[data-testid="stSidebar"] .sidebar-brand-subtitle {
    margin-top: 0.5rem !important;
    font-size: 0.72rem !important;
    color: #9eabb2 !important;
}
[data-testid="stSidebar"] .user-card {
    padding: 0.9rem !important;
    margin: 0.45rem 0 0.7rem !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    background: rgba(255,255,255,0.035) !important;
}
[data-testid="stSidebar"] .user-name {
    color: #f5f8f9 !important;
    font-weight: 750 !important;
}
[data-testid="stSidebar"] .user-role,
[data-testid="stSidebar"] .user-status-text {
    color: #9eabb2 !important;
}
[data-testid="stSidebar"] .user-status-dot {
    display: inline-block !important;
    width: 7px !important;
    height: 7px !important;
    border-radius: 50% !important;
    background: #35b78f !important;
    margin-right: 0.35rem !important;
}
[data-testid="stSidebar"] .sidebar-section-title {
    margin: 1rem 0 0.55rem !important;
    color: #81919a !important;
    font-size: 0.64rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.13em !important;
    text-transform: uppercase !important;
}
[data-testid="stSidebar"] .stButton > button {
    min-height: 42px !important;
    margin-bottom: 5px !important;
    padding: 0.55rem 0.75rem !important;
    border: 1px solid transparent !important;
    border-radius: 9px !important;
    background: transparent !important;
    color: #cbd5da !important;
    box-shadow: none !important;
    justify-content: flex-start !important;
    text-align: left !important;
    font-size: 0.84rem !important;
    font-weight: 650 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(45,129,119,0.12) !important;
    border-color: rgba(45,129,119,0.28) !important;
    color: #ffffff !important;
}
[data-testid="stSidebar"] [class*="st-key-menu_active"] button {
    background: #2d8177 !important;
    border-color: #2d8177 !important;
    color: #ffffff !important;
    box-shadow: 0 5px 14px rgba(45,129,119,0.18) !important;
}
[data-testid="stSidebar"] [class*="st-key-cerrar_sesion"] button {
    color: #aeb9bf !important;
    background: rgba(255,255,255,0.035) !important;
    border-color: rgba(255,255,255,0.08) !important;
    justify-content: center !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: rgba(255,255,255,0.025) !important;
    border-color: rgba(255,255,255,0.08) !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary {
    color: #d5dde1 !important;
}

/* ---------- AVISOS ---------- */
[data-testid="stMain"] [data-testid="stAlert"] {
    max-width:980px !important;
    margin:.7rem 0 !important;
    overflow:visible !important;
}
[data-testid="stMain"] [data-testid="stAlertContainer"] {
    display:flex !important;
    align-items:center !important;
    box-sizing:border-box !important;
    min-height:3rem !important;
    padding:.35rem .9rem !important;
    border:1px solid rgba(148,163,184,.18) !important;
    border-left-width:3px !important;
    border-radius:11px !important;
    box-shadow:0 5px 16px rgba(0,0,0,.12) !important;
}
[data-testid="stMain"] [data-testid="stAlertContainer"] > div {
    display:flex !important;
    align-items:center !important;
    min-height:2.2rem !important;
    width:100% !important;
}
[data-testid="stMain"] [data-testid^="stAlertContent"] {
    display:flex !important;
    align-items:center !important;
    width:100% !important;
}
[data-testid="stMain"] [data-testid^="stAlertContent"] [data-testid="stMarkdownContainer"] {
    display:flex !important;
    align-items:center !important;
    min-height:2.2rem !important;
}
[data-testid="stMain"] [data-testid^="stAlertContent"] p {
    position:relative !important;
    top:-5px !important;
    margin:0 !important;
    font-size:.88rem !important;
    font-weight:550 !important;
    line-height:1.4 !important;
    color:#e8f0f5 !important;
}
[data-testid="stMain"] [data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) [data-testid="stAlertContainer"] {
    background:#12372c !important;
    border-color:rgba(52,211,153,.32) !important;
    border-left-color:#34b889 !important;
}
[data-testid="stMain"] [data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) [data-testid="stAlertContainer"] {
    background:#152f47 !important;
    border-color:rgba(96,165,250,.34) !important;
    border-left-color:#60a5fa !important;
}
[data-testid="stMain"] [data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) [data-testid="stAlertContainer"] {
    background:#403116 !important;
    border-color:rgba(251,191,36,.34) !important;
    border-left-color:#fbbf24 !important;
}
[data-testid="stMain"] [data-testid="stAlert"]:has([data-testid="stAlertContentError"]) [data-testid="stAlertContainer"] {
    background:#43262c !important;
    border-color:rgba(248,113,113,.34) !important;
    border-left-color:#f87171 !important;
}
body:has(.hb-light-mode) [data-testid="stMain"] [data-testid="stAlertContainer"] {
    box-shadow:0 4px 12px rgba(35,52,61,.07) !important;
}
body:has(.hb-light-mode) [data-testid="stMain"] [data-testid="stAlertContainer"] p {
    color:#263840 !important;
}
body:has(.hb-light-mode) [data-testid="stMain"] [data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) [data-testid="stAlertContainer"] {
    background:#ecf8f1 !important;
    border-color:#c6e8d3 !important;
    border-left-color:#32966b !important;
}
body:has(.hb-light-mode) [data-testid="stMain"] [data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) [data-testid="stAlertContainer"] {
    background:#edf5fc !important;
    border-color:#c9dced !important;
    border-left-color:#4787c3 !important;
}
body:has(.hb-light-mode) [data-testid="stMain"] [data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) [data-testid="stAlertContainer"] {
    background:#fff8e8 !important;
    border-color:#eedda9 !important;
    border-left-color:#c28a16 !important;
}
body:has(.hb-light-mode) [data-testid="stMain"] [data-testid="stAlert"]:has([data-testid="stAlertContentError"]) [data-testid="stAlertContainer"] {
    background:#fff0ef !important;
    border-color:#efcfcc !important;
    border-left-color:#c45454 !important;
}

/* ---------- RESPONSIVE ---------- */
@media (max-width: 900px) {
    [data-testid="stMainBlockContainer"] {
        padding: 1rem 1rem 2rem !important;
    }
}
@media (max-width: 640px) {
    [data-testid="stSidebar"] {
        width: 270px !important;
        min-width: 270px !important;
        max-width: 270px !important;
    }
}
</style>
""", unsafe_allow_html=True)

if st.session_state.tema_blanco:
    st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] { background: #f4f7f8 !important; }
        [data-testid="stMain"] { color: #263238 !important; }
        [data-testid="stMetric"], [data-testid="stForm"] { background: #ffffff !important; }
        [data-testid="stSidebar"] { background: #f8fafb !important; border-right-color: #dce5e8 !important; }
        [data-testid="stSidebar"] .sidebar-brand { background: #ffffff !important; border-color: #dce5e8 !important; border-left-color: #2d8177 !important; }
        [data-testid="stSidebar"] .sidebar-brand-name { color: #263238 !important; }
        [data-testid="stSidebar"] .sidebar-brand-subtitle, [data-testid="stSidebar"] .user-role { color: #64748b !important; }
        [data-testid="stSidebar"] .user-card { background: #ffffff !important; border-color: #dce5e8 !important; }
        [data-testid="stSidebar"] .user-name { color: #263238 !important; }
        [data-testid="stSidebar"] .stButton > button { color: #334155 !important; }
        [data-testid="stSidebar"] .stButton > button:hover { background: #edf7f5 !important; color: #24665f !important; }
        [data-testid="stSidebar"] [class*="st-key-menu_active"] button { background: #2d8177 !important; color: #ffffff !important; }
        [data-testid="stSidebar"] [class*="st-key-cerrar_sesion"] button { background: #ffffff !important; border-color: #dce5e8 !important; color: #475569 !important; }
        [data-testid="stSidebar"] [data-testid="stExpander"] { background: #ffffff !important; border-color: #dce5e8 !important; }
        [data-testid="stSidebar"] [data-testid="stExpander"] summary { color: #334155 !important; }
        [data-testid="stTable"] th { background: #eef4f5 !important; color: #263238 !important; }
        [data-testid="stTable"] td { background: #ffffff !important; color: #334155 !important; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] { background: #11161b !important; }
        [data-testid="stMain"] { color: #e7edf0 !important; }
        [data-testid="stMetric"], [data-testid="stForm"] { background: #1a2228 !important; border-color: #2b3942 !important; }
        [data-testid="stMetricLabel"] { color: #aebbc2 !important; }
        [data-testid="stTable"], [data-testid="stDataFrame"] { border-color: #2b3942 !important; }
        [data-testid="stTable"] th { background: #202a31 !important; color: #e7edf0 !important; }
        [data-testid="stTable"] td { background: #171e23 !important; color: #d9e1e5 !important; border-color: #2b3942 !important; }
        [data-testid="stForm"] label { color: #d9e1e5 !important; }
        .quick-card { background: linear-gradient(145deg, #1a2228, #171e23) !important; border-color: #2b3942 !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
    html,
    body,
    [data-testid="stAppViewContainer"] {
        scroll-behavior: smooth;
        scrollbar-width: auto;
        scrollbar-color: #71818a #182027;
    }

    [data-testid="stMain"] {
        width: auto;
        min-width: 0;
        flex: 1 1 0%;
    }

    [data-testid="stSidebar"][aria-expanded="false"] {
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        flex: 0 0 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        transition:
            flex-basis 180ms ease,
            width 180ms ease,
            min-width 180ms ease,
            max-width 180ms ease !important;
    }

    [data-testid="stMainBlockContainer"] {
        width: 100% !important;
        max-width: none !important;
        align-self: stretch !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
        box-sizing: border-box !important;
    }

    [data-testid="stMainBlockContainer"] > div,
    [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"],
    [data-testid="stMainBlockContainer"] [data-testid="column"] {
        min-width: 0;
    }

    [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has([data-testid="stMarkdownContainer"] style) {
        display: none !important;
    }

    body {
        overscroll-behavior-y: none;
    }

    [data-testid="stMainBlockContainer"] {
        margin-top: 0 !important;
        padding: 0.75rem clamp(1rem, 3vw, 2.75rem) 4rem !important;
        scroll-padding-top: 0.75rem;
    }

    [data-testid="stMain"] h1 {
        margin-top: 0 !important;
        margin-bottom: 0.75rem !important;
        line-height: 1.15 !important;
        scroll-margin-top: 0.75rem;
    }

    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3 {
        line-height: 1.25 !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        height: 100dvh !important;
        max-height: 100dvh !important;
        overflow-x: hidden !important;
        overflow-y: auto !important;
        overscroll-behavior-y: contain !important;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: thin !important;
        scrollbar-color: rgba(148, 163, 184, 0.62) transparent !important;
    }

    [data-testid="stSidebar"] > div:first-child::-webkit-scrollbar {
        width: 9px;
    }

    [data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-track {
        background: transparent;
    }

    [data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-thumb {
        border: 2px solid transparent;
        background-clip: padding-box;
        border-radius: 999px;
        background-color: rgba(148, 163, 184, 0.62);
    }

    [data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-thumb:hover {
        background-color: rgba(148, 163, 184, 0.9);
    }

    [data-testid="stMain"]::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    [data-testid="stMain"]::-webkit-scrollbar-track {
        background: transparent;
    }

    [data-testid="stMain"]::-webkit-scrollbar-thumb {
        border: 2px solid transparent;
        background-clip: padding-box;
        border-radius: 999px;
        background-color: rgba(113, 129, 138, 0.68);
    }

    [data-testid="stMain"]::-webkit-scrollbar-thumb:hover {
        background-color: rgba(113, 129, 138, 0.95);
    }

    [data-testid="stSidebar"] .stButton > button,
    [data-testid="stMain"] button {
        transition:
            background-color 160ms ease,
            border-color 160ms ease,
            box-shadow 160ms ease,
            transform 160ms ease !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover,
    [data-testid="stMain"] button:hover {
        transform: translateY(-1px) !important;
    }

    [data-testid="stSidebar"] button:focus-visible,
    [data-testid="stMain"] button:focus-visible {
        outline: 3px solid rgba(85, 184, 169, 0.55) !important;
        outline-offset: 2px !important;
    }

    [data-testid="stMain"] [data-testid="stDataFrame"],
    [data-testid="stMain"] [data-testid="stTable"] {
        max-width: 100%;
        border-radius: 12px;
    }

    [class*="st-key-theme_toggle"] button {
        width: auto !important;
        min-width: 3.6rem !important;
        padding: 0 0.8rem !important;
        border-radius: 999px !important;
    }

    [class*="st-key-theme_toggle"] {
        position: fixed !important;
        top: 3rem !important;
        right: 1.25rem !important;
        z-index: 1000002 !important;
        width: fit-content !important;
        max-width: calc(100vw - 2rem) !important;
    }

    @media (max-width: 768px) {
        [data-testid="stMainBlockContainer"] {
            margin-top: 0 !important;
            padding: 1rem 1rem 3rem !important;
        }

        [data-testid="stMain"] h1 {
            font-size: clamp(1.5rem, 7vw, 2rem) !important;
        }

        [class*="st-key-theme_toggle"] {
            top: 2.75rem !important;
            right: 0.75rem !important;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        html,
        [data-testid="stAppViewContainer"] {
            scroll-behavior: auto;
        }

        [data-testid="stSidebar"] .stButton > button,
        [data-testid="stMain"] button {
            transition: none !important;
        }
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
:root {
    --hb-accent: #2f8f83;
    --hb-accent-bright: #55b8a9;
    --hb-ink: #eaf1f3;
    --hb-muted: #94a5ae;
    --hb-border: rgba(148, 163, 184, 0.16);
}
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse at 92% 0%, rgba(47, 143, 131, 0.12), transparent 30rem),
        linear-gradient(180deg, #101820 0%, #0f171e 100%) !important;
}
[data-testid="stMainBlockContainer"] {
    width: 100% !important;
    max-width: 1480px !important;
    margin: 0 auto !important;
    padding: 2rem clamp(1.1rem, 3vw, 2.8rem) 4rem !important;
}
[data-testid="stMain"] {
    color: var(--hb-ink) !important;
    font-family: Inter, "Segoe UI", sans-serif !important;
}
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3 {
    font-family: Inter, "Segoe UI", sans-serif !important;
    letter-spacing: -0.025em !important;
}
[data-testid="stMain"] h1 {
    margin-bottom: 0.9rem !important;
    font-size: clamp(1.65rem, 2.5vw, 2.25rem) !important;
    font-weight: 760 !important;
}
[data-testid="stMain"] h2 {
    margin-top: 1.6rem !important;
    font-size: clamp(1.2rem, 1.7vw, 1.45rem) !important;
    font-weight: 720 !important;
}
[data-testid="stMain"] h3 {
    font-size: 1.05rem !important;
    font-weight: 700 !important;
}
[data-testid="stMain"] p,
[data-testid="stMain"] label {
    line-height: 1.55 !important;
}
[data-testid="stMetric"] {
    min-height: 7.6rem !important;
    padding: 1.15rem 1.2rem !important;
    border: 1px solid var(--hb-border) !important;
    border-radius: 15px !important;
    background: linear-gradient(145deg, rgba(255,255,255,.055), rgba(255,255,255,.018)) !important;
    box-shadow: 0 12px 28px rgba(0,0,0,.14) !important;
    transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-color: rgba(85,184,169,.36) !important;
    box-shadow: 0 16px 34px rgba(0,0,0,.2) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--hb-muted) !important;
    font-size: .74rem !important;
    font-weight: 700 !important;
    letter-spacing: .055em !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    color: var(--hb-ink) !important;
    font-size: clamp(1.35rem, 2vw, 1.9rem) !important;
    font-weight: 780 !important;
    letter-spacing: -.025em !important;
}
[data-testid="stForm"],
[data-testid="stExpander"],
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    border-color: var(--hb-border) !important;
    border-radius: 14px !important;
}
[data-testid="stForm"] {
    padding: 1.25rem !important;
    background: rgba(24,35,44,.82) !important;
    box-shadow: 0 14px 32px rgba(0,0,0,.12) !important;
}
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-baseweb="select"] > div {
    border-radius: 9px !important;
    border-color: rgba(148,163,184,.23) !important;
}
[data-testid="stMain"] button {
    border-radius: 9px !important;
    font-weight: 650 !important;
}
[data-testid="stMain"] button[kind="primary"],
[data-testid="stMain"] button[kind="primaryFormSubmit"] {
    background: linear-gradient(135deg, #328f83, #26776e) !important;
    border-color: #328f83 !important;
    box-shadow: 0 6px 16px rgba(47,143,131,.2) !important;
}
[data-testid="stMain"] button[kind="primary"]:hover,
[data-testid="stMain"] button[kind="primaryFormSubmit"]:hover {
    background: linear-gradient(135deg, #3ca193, #2f8178) !important;
    border-color: #3ca193 !important;
}
[data-testid="stTabs"] [role="tablist"] {
    gap: .35rem;
    padding: .3rem;
    border: 1px solid var(--hb-border);
    border-radius: 12px;
    background: rgba(255,255,255,.025);
}
[data-testid="stTabs"] button[role="tab"] {
    border-radius: 9px !important;
    font-weight: 650 !important;
}
.hb-hero {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
    min-height: 12.5rem;
    overflow: hidden;
    margin: 0 0 1.6rem;
    padding: clamp(1.5rem, 3vw, 2.4rem);
    border: 1px solid rgba(95,177,166,.22);
    border-radius: 22px;
    background:
        radial-gradient(circle at 88% 18%, rgba(89,184,170,.2), transparent 17rem),
        linear-gradient(118deg, #1a3035 0%, #172a31 52%, #1b2630 100%);
    box-shadow: 0 22px 50px rgba(0,0,0,.2);
}
.hb-hero::after {
    content: "";
    position: absolute;
    width: 17rem;
    height: 17rem;
    right: -4rem;
    bottom: -12rem;
    border: 1px solid rgba(139,221,207,.18);
    border-radius: 50%;
    box-shadow: 0 0 0 1.4rem rgba(139,221,207,.035), 0 0 0 2.8rem rgba(139,221,207,.025);
    pointer-events: none;
}
.hb-hero-content {
    position: relative;
    z-index: 1;
    max-width: 46rem;
}
.hb-hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: .5rem;
    margin-bottom: .9rem;
    color: #9be0d5;
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: .14em;
    text-transform: uppercase;
}
.hb-hero-eyebrow::before {
    content: "";
    width: .45rem;
    height: .45rem;
    border-radius: 50%;
    background: #63d5b4;
    box-shadow: 0 0 0 4px rgba(99,213,180,.12);
}
.hb-hero h1 {
    margin: 0 !important;
    color: #f3f8f8 !important;
    font-size: clamp(1.8rem, 3.4vw, 2.65rem) !important;
    font-weight: 780 !important;
    line-height: 1.1 !important;
    letter-spacing: -.04em !important;
}
.hb-hero p {
    max-width: 38rem;
    margin: .75rem 0 0;
    color: #b8cbd0;
    font-size: .98rem;
    line-height: 1.55;
}
.hb-hero-date {
    position: relative;
    z-index: 1;
    flex: 0 0 auto;
    padding: .7rem .9rem;
    border: 1px solid rgba(176,219,213,.18);
    border-radius: 12px;
    background: rgba(8,18,22,.2);
    color: #d5e9e7;
    font-size: .78rem;
    font-weight: 650;
}
.quick-card {
    display: flex;
    flex-direction: column;
    min-height: 9.1rem;
    margin-bottom: .65rem;
    padding: 1.15rem;
    border: 1px solid var(--hb-border);
    border-radius: 15px;
    background: linear-gradient(145deg, rgba(255,255,255,.05), rgba(255,255,255,.018));
    box-shadow: 0 10px 24px rgba(0,0,0,.1);
    transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
}
.quick-card:hover {
    transform: translateY(-2px);
    border-color: rgba(85,184,169,.34);
    box-shadow: 0 15px 28px rgba(0,0,0,.16);
}
.quick-card strong {
    color: var(--hb-ink);
    font-size: .98rem;
    font-weight: 720;
}
.quick-card p {
    margin: .5rem 0 0;
    color: var(--hb-muted);
    font-size: .82rem;
    line-height: 1.5;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #141e26 0%, #10171e 100%) !important;
    border-right: 1px solid rgba(148,163,184,.13) !important;
}
[data-testid="stSidebar"] .sidebar-brand {
    padding: 1.05rem !important;
    border: 1px solid rgba(85,184,169,.18) !important;
    border-left: 3px solid #3fa395 !important;
    border-radius: 0 14px 14px 0 !important;
    background: linear-gradient(145deg, rgba(47,143,131,.11), rgba(255,255,255,.025)) !important;
}
[data-testid="stSidebar"] .user-card {
    border: 1px solid rgba(148,163,184,.14) !important;
    border-radius: 12px !important;
    background: rgba(255,255,255,.035) !important;
}
[data-testid="stSidebar"] [class*="st-key-menu_item_"] button {
    min-height: 2.75rem !important;
    border: 1px solid transparent !important;
    border-radius: 10px !important;
    background: transparent !important;
    color: #c3d0d5 !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] [class*="st-key-menu_item_"] button:hover {
    background: rgba(47,143,131,.12) !important;
    border-color: rgba(85,184,169,.2) !important;
    color: #f0f7f7 !important;
}
[data-testid="stSidebar"] [class*="st-key-menu_active"] button {
    min-height: 2.75rem !important;
    border: 1px solid rgba(106,207,192,.3) !important;
    border-radius: 10px !important;
    background: linear-gradient(135deg, #328f83, #26776e) !important;
    color: #fff !important;
    box-shadow: 0 8px 18px rgba(31,115,105,.22) !important;
}
[data-testid="stSidebar"] [class*="st-key-menu_active"] button:hover {
    background: linear-gradient(135deg, #3ca193, #2f8178) !important;
}
body:has(.hb-light-mode) [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse at 92% 0%, rgba(47,143,131,.1), transparent 30rem),
        linear-gradient(180deg, #f8fafb 0%, #f1f5f6 100%) !important;
}
body:has(.hb-light-mode) [data-testid="stMain"] {
    color: #25363d !important;
}
body:has(.hb-light-mode) [data-testid="stMain"] h1,
body:has(.hb-light-mode) [data-testid="stMain"] h2,
body:has(.hb-light-mode) [data-testid="stMain"] h3 {
    color: #1b2b32 !important;
}
body:has(.hb-light-mode) [data-testid="stMetric"],
body:has(.hb-light-mode) [data-testid="stForm"],
body:has(.hb-light-mode) [data-testid="stExpander"],
body:has(.hb-light-mode) [data-testid="stDataFrame"],
body:has(.hb-light-mode) [data-testid="stTable"] {
    border-color: #e0e8eb !important;
    background: rgba(255,255,255,.94) !important;
    box-shadow: 0 10px 26px rgba(34,52,61,.06) !important;
}
body:has(.hb-light-mode) [data-testid="stMetricLabel"] { color: #71818a !important; }
body:has(.hb-light-mode) [data-testid="stMetricValue"] { color: #17262d !important; }
body:has(.hb-light-mode) [data-testid="stTextInput"] input,
body:has(.hb-light-mode) [data-testid="stNumberInput"] input,
body:has(.hb-light-mode) [data-testid="stTextArea"] textarea,
body:has(.hb-light-mode) [data-baseweb="select"] > div {
    background: #fff !important;
    color: #24343b !important;
    border-color: #d4dfe3 !important;
}
body:has(.hb-light-mode) .quick-card {
    border-color: #e0e8eb;
    background: linear-gradient(145deg, #fff, #f8fbfb);
    box-shadow: 0 10px 24px rgba(34,52,61,.06);
}
body:has(.hb-light-mode) .quick-card strong { color: #25363d; }
body:has(.hb-light-mode) .quick-card p { color: #687980; }
body:has(.hb-light-mode) [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #fff 0%, #f7fafb 100%) !important;
    border-right-color: #e1e8eb !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] .sidebar-brand,
body:has(.hb-light-mode) [data-testid="stSidebar"] .user-card {
    border-color: #dce8e7 !important;
    background: linear-gradient(145deg, #f0f8f7, #fff) !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] .sidebar-brand-name,
body:has(.hb-light-mode) [data-testid="stSidebar"] .user-name {
    color: #26383e !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] .sidebar-brand-subtitle,
body:has(.hb-light-mode) [data-testid="stSidebar"] .user-role,
body:has(.hb-light-mode) [data-testid="stSidebar"] .user-status-text {
    color: #647780 !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] [class*="st-key-menu_item_"] button {
    color: #52656d !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] [class*="st-key-menu_item_"] button:hover {
    background: #edf7f5 !important;
    color: #246d65 !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] [class*="st-key-menu_active"] button {
    background: linear-gradient(135deg, #328f83, #26776e) !important;
    color: #fff !important;
}
body:has(.hb-light-mode) .hb-hero {
    border-color: rgba(47,143,131,.2);
    background:
        radial-gradient(circle at 88% 18%, rgba(89,184,170,.18), transparent 17rem),
        linear-gradient(118deg, #e8f4f2 0%, #edf5f5 55%, #eef2f5 100%);
    box-shadow: 0 18px 42px rgba(34,52,61,.08);
}
body:has(.hb-light-mode) .hb-hero h1 { color: #1b3438 !important; }
body:has(.hb-light-mode) .hb-hero p { color: #536a70; }
body:has(.hb-light-mode) .hb-hero-eyebrow { color: #27776f; }
body:has(.hb-light-mode) .hb-hero-date {
    border-color: #cfe1df;
    background: rgba(255,255,255,.65);
    color: #35565a;
}
@media (max-width: 900px) {
    [data-testid="stMainBlockContainer"] { padding: 1.35rem 1.1rem 3rem !important; }
}
@media (max-width: 640px) {
    .hb-hero {
        align-items: flex-start;
        flex-direction: column;
        gap: 1rem;
        min-height: 0;
        padding: 1.35rem;
        border-radius: 17px;
    }
    .hb-hero-date { align-self: flex-start; }
    [data-testid="stMetric"] {
        min-height: 6.3rem !important;
        padding: .9rem !important;
    }
    [data-testid="stMainBlockContainer"] { padding: 1rem .85rem 2.5rem !important; }
}
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        scroll-behavior: auto !important;
        transition-duration: .01ms !important;
        animation-duration: .01ms !important;
    }
}
#root [data-testid="stSidebar"] > div:first-child {
    padding-top:.35rem !important;
}
#root [data-testid="stSidebar"] [class*="st-key-menu_"] button,
#root [data-testid="stSidebar"] [class*="st-key-menu_"] button:hover,
#root [data-testid="stSidebar"] [class*="st-key-menu_"] button:active {
    border:1px solid rgba(226,232,240,.24) !important;
    outline:none !important;
    box-shadow:none !important;
}
#root [data-testid="stSidebar"] [class*="st-key-menu_"] button {
    background:transparent !important;
    color:#b8c4c9 !important;
}
#root [data-testid="stSidebar"] [class*="st-key-menu_"] button:hover {
    border-color:rgba(226,232,240,.24) !important;
    background:rgba(255,255,255,.055) !important;
    color:#edf3f4 !important;
}
#root [data-testid="stSidebar"] [class*="st-key-menu_active"] button,
#root [data-testid="stSidebar"] [class*="st-key-menu_active"] button:hover {
    border-color:rgba(226,232,240,.28) !important;
    background:rgba(255,255,255,.075) !important;
    color:#edf3f4 !important;
}
#root [data-testid="stSidebar"] [class*="st-key-menu_"] button:focus-visible {
    outline:2px solid #89979d !important;
    outline-offset:2px !important;
}
body:has(.hb-light-mode) #root [data-testid="stSidebar"] [class*="st-key-menu_"] button {
    border-color:rgba(71,85,91,.22) !important;
    background:transparent !important;
    color:#506168 !important;
}
body:has(.hb-light-mode) #root [data-testid="stSidebar"] [class*="st-key-menu_"] button:hover {
    border-color:rgba(71,85,91,.22) !important;
    background:#eef1f2 !important;
    color:#34464d !important;
}
body:has(.hb-light-mode) #root [data-testid="stSidebar"] [class*="st-key-menu_active"] button,
body:has(.hb-light-mode) #root [data-testid="stSidebar"] [class*="st-key-menu_active"] button:hover {
    border-color:rgba(71,85,91,.28) !important;
    background:#e7ebed !important;
    color:#34464d !important;
}
body:has(.hb-light-mode) {
    --hb-light-ink:#18363b;
    --hb-light-muted:#60777d;
    --hb-light-teal:#238b7d;
    --hb-light-teal-dark:#176b62;
    --hb-light-border:#d4e5e8;
}
body:has(.hb-light-mode) [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse at 88% 2%, rgba(67,181,162,.2), transparent 28rem),
        radial-gradient(ellipse at 4% 42%, rgba(92,165,220,.1), transparent 30rem),
        linear-gradient(145deg,#edf5f8 0%,#f4f8fa 48%,#eaf4f2 100%) !important;
}
body:has(.hb-light-mode) [data-testid="stHeader"],
body:has(.hb-light-mode) [data-testid="stMain"],
body:has(.hb-light-mode) [data-testid="stMainBlockContainer"] {
    background:transparent !important;
}
body:has(.hb-light-mode) [data-testid="stMain"] {
    color:var(--hb-light-ink) !important;
}
body:has(.hb-light-mode) [data-testid="stMain"] h1,
body:has(.hb-light-mode) [data-testid="stMain"] h2,
body:has(.hb-light-mode) [data-testid="stMain"] h3,
body:has(.hb-light-mode) [data-testid="stMain"] h4 {
    color:#1b3f43 !important;
}
body:has(.hb-light-mode) [data-testid="stMain"] p,
body:has(.hb-light-mode) [data-testid="stMain"] label,
body:has(.hb-light-mode) [data-testid="stMain"] [data-testid="stCaptionContainer"] {
    color:var(--hb-light-muted) !important;
}
body:has(.hb-light-mode) [data-testid="stMain"] a {
    color:var(--hb-light-teal-dark) !important;
}
body:has(.hb-light-mode) [data-testid="stMain"] hr {
    border-color:#cddfe2 !important;
}
body:has(.hb-light-mode) [data-testid="stMetric"] {
    border:1px solid #cfe4e5 !important;
    background:linear-gradient(145deg,#ffffff 0%,#f0faf8 100%) !important;
    box-shadow:0 12px 28px rgba(35,91,98,.09) !important;
}
body:has(.hb-light-mode) [data-testid="stMetric"]::before {
    background:linear-gradient(180deg,#31aa96,#438bd1) !important;
}
body:has(.hb-light-mode) [data-testid="stMetricLabel"] {
    color:#53727a !important;
    opacity:1 !important;
}
body:has(.hb-light-mode) [data-testid="stMetricValue"] {
    color:#173b40 !important;
}
body:has(.hb-light-mode) [data-testid="stForm"],
body:has(.hb-light-mode) [data-testid="stExpander"],
body:has(.hb-light-mode) [data-testid="stVerticalBlockBorderWrapper"] {
    border-color:var(--hb-light-border) !important;
    background:rgba(255,255,255,.9) !important;
    box-shadow:0 8px 22px rgba(35,91,98,.055) !important;
}
body:has(.hb-light-mode) [data-testid="stForm"] {
    border-radius:16px !important;
}
body:has(.hb-light-mode) [data-testid="stExpander"] summary {
    color:#294d53 !important;
    background:linear-gradient(90deg,#f0f8f8,#f8fbfc) !important;
}
body:has(.hb-light-mode) [data-testid="stTextInput"] input,
body:has(.hb-light-mode) [data-testid="stNumberInput"] input,
body:has(.hb-light-mode) [data-testid="stTextArea"] textarea,
body:has(.hb-light-mode) [data-baseweb="select"] > div {
    border-color:#c9dcdf !important;
    border-radius:10px !important;
    background:#ffffff !important;
    color:#243f45 !important;
    box-shadow:0 2px 5px rgba(35,91,98,.035) !important;
}
body:has(.hb-light-mode) [data-testid="stTextInput"] input:focus,
body:has(.hb-light-mode) [data-testid="stNumberInput"] input:focus,
body:has(.hb-light-mode) [data-testid="stTextArea"] textarea:focus {
    border-color:#39a995 !important;
    box-shadow:0 0 0 3px rgba(57,169,149,.15) !important;
}
body:has(.hb-light-mode) [data-testid="stMain"] button {
    border-color:#c8dcdf !important;
    border-radius:10px !important;
    background:linear-gradient(180deg,#ffffff,#f2f8f9) !important;
    color:#2d5057 !important;
    box-shadow:0 3px 8px rgba(35,91,98,.07) !important;
    transition:transform .16s ease,box-shadow .16s ease,background .16s ease !important;
}
body:has(.hb-light-mode) [data-testid="stMain"] button:hover {
    border-color:#8dc9bf !important;
    background:linear-gradient(180deg,#f1fbf9,#e5f5f2) !important;
    color:#176b62 !important;
    box-shadow:0 6px 14px rgba(35,139,125,.13) !important;
    transform:translateY(-1px);
}
body:has(.hb-light-mode) [data-testid="stMain"] button[kind="primary"],
body:has(.hb-light-mode) [data-testid="stMain"] button[kind="primaryFormSubmit"] {
    border-color:#238b7d !important;
    background:linear-gradient(135deg,#2fa391,#21796f) !important;
    color:#ffffff !important;
    box-shadow:0 6px 16px rgba(35,139,125,.22) !important;
}
body:has(.hb-light-mode) [data-testid="stMain"] button[kind="primary"] *,
body:has(.hb-light-mode) [data-testid="stMain"] button[kind="primaryFormSubmit"] * {
    color:#ffffff !important;
    -webkit-text-fill-color:#ffffff !important;
}
body:has(.hb-light-mode) [data-testid="stMain"] button[kind="primary"]:hover,
body:has(.hb-light-mode) [data-testid="stMain"] button[kind="primaryFormSubmit"]:hover {
    border-color:#176b62 !important;
    background:linear-gradient(135deg,#278f80,#176b62) !important;
    color:#ffffff !important;
}
body:has(.hb-light-mode) [data-testid="stMain"] [data-testid="stNumberInput"] button {
    background:#eaf5f5 !important;
    color:#28776f !important;
}
body:has(.hb-light-mode) [data-testid="stMain"] input[type="checkbox"],
body:has(.hb-light-mode) [data-testid="stMain"] input[type="radio"] {
    accent-color:#238b7d;
}
.st-key-stock_historico_checkbox [data-testid="stCheckbox"] label,
[class*="st-key-importar_ventas_descontar_stock"] [data-testid="stCheckbox"] label,
[class*="st-key-restaurar_stock_venta_antigua_"] [data-testid="stCheckbox"] label {
    align-items:center !important;
}
body:has(.hb-light-mode) [data-testid="stTabs"] [role="tablist"] {
    border-bottom:1px solid #d2e2e4 !important;
    background:rgba(255,255,255,.66) !important;
}
body:has(.hb-light-mode) [data-testid="stTabs"] button[role="tab"] {
    border-color:transparent !important;
    background:transparent !important;
    color:#5e747b !important;
    box-shadow:none !important;
}
body:has(.hb-light-mode) [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    border-color:#c7e4df !important;
    background:#e5f5f2 !important;
    color:#176b62 !important;
}
body:has(.hb-light-mode) [data-testid="stTable"],
body:has(.hb-light-mode) [data-testid="stDataFrame"],
body:has(.hb-light-mode) [data-testid="stArrowVegaLiteChart"],
body:has(.hb-light-mode) [data-testid="stVegaLiteChart"],
body:has(.hb-light-mode) [data-testid="stPyplotChart"] {
    border-color:#d1e3e5 !important;
    border-radius:14px !important;
    background:#ffffff !important;
    box-shadow:0 8px 22px rgba(35,91,98,.06) !important;
}
body:has(.hb-light-mode) [data-testid="stTable"] th {
    background:#e7f4f3 !important;
    color:#234b50 !important;
    border-color:#d0e4e3 !important;
}
body:has(.hb-light-mode) [data-testid="stTable"] td {
    background:#ffffff !important;
    color:#314e54 !important;
    border-color:#e0eaec !important;
}
body:has(.hb-light-mode) .quick-card {
    border-color:#cde4e2 !important;
    background:
        radial-gradient(circle at 100% 0%,rgba(83,183,165,.13),transparent 11rem),
        linear-gradient(145deg,#ffffff 0%,#eff8f7 100%) !important;
    box-shadow:0 10px 24px rgba(35,91,98,.08) !important;
}
body:has(.hb-light-mode) .quick-card strong {
    color:#1b4649 !important;
}
body:has(.hb-light-mode) .quick-card p {
    color:#5d777d !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] {
    background:linear-gradient(180deg,#f5fbfc 0%,#edf6f7 55%,#f3f9f8 100%) !important;
    border-right:1px solid #d6e6e8 !important;
    box-shadow:4px 0 22px rgba(40,91,98,.045) !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] .sidebar-brand {
    border-color:#bfe0db !important;
    border-left:4px solid #258e80 !important;
    background:linear-gradient(135deg,#e1f4ef 0%,#f4fbfc 100%) !important;
    box-shadow:0 8px 18px rgba(35,139,125,.1) !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] .sidebar-brand-kicker {
    color:#278274 !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] .sidebar-brand-name,
body:has(.hb-light-mode) [data-testid="stSidebar"] .sidebar-brand-title,
body:has(.hb-light-mode) [data-testid="stSidebar"] .user-name {
    color:#183f43 !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] .sidebar-brand-subtitle,
body:has(.hb-light-mode) [data-testid="stSidebar"] .user-role,
body:has(.hb-light-mode) [data-testid="stSidebar"] .user-status-text,
body:has(.hb-light-mode) [data-testid="stSidebar"] .sidebar-section-title {
    color:#607b81 !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] .user-card {
    border-color:#cfe5e4 !important;
    background:linear-gradient(135deg,#ffffff,#eaf6f5) !important;
    box-shadow:0 5px 14px rgba(35,91,98,.055) !important;
}
body:has(.hb-light-mode) #root [data-testid="stSidebar"] [class*="st-key-menu_"] button {
    border:1px solid #d5e4e6 !important;
    background:rgba(255,255,255,.78) !important;
    color:#385a60 !important;
    box-shadow:0 2px 6px rgba(35,91,98,.04) !important;
}
body:has(.hb-light-mode) #root [data-testid="stSidebar"] [class*="st-key-menu_"] button:hover {
    border-color:#a9d8cf !important;
    background:#e5f5f2 !important;
    color:#176b62 !important;
    box-shadow:0 5px 12px rgba(35,139,125,.1) !important;
}
body:has(.hb-light-mode) #root [data-testid="stSidebar"] [class*="st-key-menu_active"] button,
body:has(.hb-light-mode) #root [data-testid="stSidebar"] [class*="st-key-menu_active"] button:hover {
    border-color:#258e80 !important;
    background:linear-gradient(115deg,#2e9d8d,#24786f) !important;
    color:#ffffff !important;
    box-shadow:0 7px 16px rgba(35,139,125,.22) !important;
}
body:has(.hb-light-mode) #root [data-testid="stSidebar"] [class*="st-key-menu_"] button * {
    color:inherit !important;
    -webkit-text-fill-color:currentColor !important;
}
body:has(.hb-light-mode) #root [data-testid="stSidebar"] [class*="st-key-menu_active"] button * {
    color:#ffffff !important;
    -webkit-text-fill-color:#ffffff !important;
}
body:has(.hb-light-mode) [data-testid="stSidebar"] [data-testid="stExpander"] {
    border-color:#d4e5e7 !important;
    background:rgba(255,255,255,.75) !important;
}
body:has(.hb-light-mode) .st-key-registered_users_table [data-testid="stTable"] {
    border:0 !important;
    box-shadow:none !important;
    outline:none !important;
}
body:has(.hb-light-mode) .st-key-registered_users_table [data-testid="stTable"] table {
    border:1px solid #b8cbce !important;
    border-radius:12px !important;
    box-shadow:none !important;
}
body:has(.hb-light-mode) .st-key-registered_users_table [data-testid="stTable"] th,
body:has(.hb-light-mode) .st-key-registered_users_table [data-testid="stTable"] td {
    border-width:0 !important;
}
body:has(.hb-light-mode) .st-key-registered_users_table [data-testid="stTable"] th {
    border-right:1px solid #72b9b0 !important;
    border-bottom:1px solid #72b9b0 !important;
}
body:has(.hb-light-mode) .st-key-registered_users_table [data-testid="stTable"] td {
    border-right:1px solid #d1e1e1 !important;
    border-bottom:1px solid #d1e1e1 !important;
}
body:has(.hb-light-mode) .st-key-registered_users_table [data-testid="stTable"] th:last-child,
body:has(.hb-light-mode) .st-key-registered_users_table [data-testid="stTable"] td:last-child {
    border-right:0 !important;
}
body:has(.hb-light-mode) .st-key-registered_users_table [data-testid="stTable"] tbody tr:last-child td {
    border-bottom:0 !important;
}
body:has(.hb-light-mode) .st-key-user_transfer_panel,
body:has(.hb-light-mode) .st-key-user_delete_panel {
    box-sizing:border-box !important;
    height:100% !important;
    padding:1.15rem !important;
    border:1px solid #c8dcdf !important;
    border-radius:16px !important;
    background:linear-gradient(145deg,#ffffff 0%,#f1f8f8 100%) !important;
    box-shadow:0 8px 20px rgba(35,91,98,.065) !important;
}
body:has(.hb-light-mode) .st-key-user_transfer_panel:hover,
body:has(.hb-light-mode) .st-key-user_delete_panel:hover {
    border-color:#a8cec9 !important;
    box-shadow:0 10px 22px rgba(35,139,125,.09) !important;
}
@media (max-width:640px) {
    body:has(.hb-light-mode) [data-testid="stMetric"] {
        box-shadow:0 7px 16px rgba(35,91,98,.07) !important;
    }
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-kicker">SISTEMA DE GESTIÓN</div>
            <div class="sidebar-brand-title">
                <span class="sidebar-brand-name">LIBRERÍA BAZAR<br>“HUMBERTITO”</span>
            </div>
            <div class="sidebar-brand-subtitle">Gestión comercial inteligente</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.divider()

database.crear_base_datos()


# ==========================================================
# AUTENTICACIÓN Y CONTROL DE ACCESO
# ==========================================================

auth.inicializar()

if not database.usar_supabase():
    st.warning(
        "La app está usando SQLite local. Configura SUPABASE_DB_URL "
        "en los Secrets de Streamlit Cloud para usar la base persistente."
    )


def pantalla_acceso():
    
    st.markdown("""
        <style>
        /* Ocultar la barra lateral durante el login */
        [data-testid="stSidebar"] {
            display: none;
        }

        /* Ocultar el botón para abrir la barra lateral */
        [data-testid="collapsedControl"] {
            display: none;
        }

        /* Ocultar la barra superior */
        header[data-testid="stHeader"] {
            background: transparent;
        }

        /* Fondo y espacio de la pantalla */
        .stApp {
            background: radial-gradient(circle at 50% 0%, rgba(45,129,119,0.16), transparent 34rem), #0f1418;
        }

        /* Centrado real del acceso: horizontal + vertical */
        [data-testid="stMainBlockContainer"] {
            width: 100% !important;
            max-width: 1080px !important;
            min-height: 100vh !important;
            padding: 2.5rem clamp(1rem, 4vw, 3rem) !important;
            margin: 0 auto !important;
            box-sizing: border-box !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
        }

        body:has(.login-brand) [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
            justify-content: center !important;
        }

        @media (max-height: 640px) {
            body:has(.login-brand) [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
                justify-content: flex-start !important;
            }
        }

        [data-testid="stMainBlockContainer"] > div {
            width: 100% !important;
        }

        .login-brand {
            display: flex;
            min-height: 27rem;
            flex-direction: column;
            justify-content: center;
            box-sizing: border-box;
            padding: clamp(1.5rem, 3.5vw, 3rem);
            border: 1px solid rgba(105, 187, 175, 0.2);
            border-radius: 22px;
            background:
                radial-gradient(circle at 85% 12%, rgba(84, 184, 169, 0.2), transparent 16rem),
                linear-gradient(145deg, #19353a 0%, #172932 58%, #17232b 100%);
            box-shadow: 0 24px 60px rgba(0, 0, 0, 0.2);
        }
        .login-brand-head {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding-bottom: 1.4rem;
            border-bottom: 1px solid rgba(184, 219, 215, 0.16);
        }
        .login-brand-mark {
            display: flex;
            width: 4rem;
            height: 4rem;
            flex: 0 0 4rem;
            align-items: center;
            justify-content: center;
            border: 1px solid rgba(164, 220, 212, 0.3);
            border-radius: 17px;
            background: linear-gradient(145deg, rgba(88, 184, 170, 0.24), rgba(255, 255, 255, 0.06));
            box-shadow: 0 12px 28px rgba(5, 15, 18, 0.2);
        }
        .login-brand-mark svg {
            display: block;
            width: 2.25rem;
            height: 2.25rem;
            fill: none;
            stroke: #d8f5ef;
            stroke-linecap: round;
            stroke-linejoin: round;
            stroke-width: 1.7;
        }
        .login-brand-identity {
            min-width: 0;
        }
        .login-brand-kicker {
            margin-bottom: 0.28rem;
            color: #8ed1c8;
            font-size: 0.66rem;
            font-weight: 750;
            letter-spacing: 0.13em;
            text-transform: uppercase;
        }
        .login-brand-name {
            color: #d6e4e5;
            font-size: 0.8rem;
            font-weight: 650;
            letter-spacing: 0.09em;
            line-height: 1.35;
            text-transform: uppercase;
        }
        .login-brand-name-strong {
            color: #f6fbfb;
            font-size: 1.48rem;
            font-weight: 820;
            letter-spacing: -0.035em;
            line-height: 1.05;
            text-transform: uppercase;
        }
        .login-brand-title {
            max-width: 13ch;
            margin-top: 1.45rem;
            color: #f5f9f9;
            font-size: clamp(2rem, 3.4vw, 3rem);
            font-weight: 680;
            line-height: 1.08;
            letter-spacing: -0.035em;
            text-wrap: balance;
        }
        .login-brand-subtitle {
            max-width: 34rem;
            margin-top: 0.85rem;
            color: #b5c9cc;
            font-size: 0.98rem;
            line-height: 1.6;
        }
        .login-brand-features {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.45rem;
            margin-top: 1.8rem;
        }
        .login-brand-feature {
            display: flex;
            align-items: center;
            gap: 0.38rem;
            min-width: 0;
            padding-top: 0.75rem;
            border-top: 1px solid rgba(184, 219, 215, 0.18);
            color: #c9d9db;
            font-size: 0.68rem;
            font-weight: 650;
            line-height: 1.2;
            white-space: nowrap;
        }
        .login-brand-feature::before {
            content: "";
            width: 0.34rem;
            height: 0.34rem;
            flex: 0 0 0.34rem;
            border-radius: 50%;
            background: #68cbb5;
            box-shadow: 0 0 0 3px rgba(104, 203, 181, 0.11);
        }
        .login-form-intro {
            max-width: 28rem;
            margin: 0 auto 1.15rem;
            text-align: center;
        }
        .login-form-intro h2 {
            margin: 0;
            color: #edf4f5;
            font-size: 1.55rem;
            font-weight: 750;
            letter-spacing: -0.03em;
        }
        .login-form-intro p {
            margin: 0.45rem 0 0;
            color: #9eabb2;
            font-size: 0.88rem;
            line-height: 1.5;
        }
        [data-testid="stForm"] {
            background: rgba(26,34,40,0.94) !important;
            border: 1px solid #2b3942 !important;
            border-radius: 18px !important;
            padding: 1.35rem 1.45rem !important;
            box-shadow: 0 24px 60px rgba(0,0,0,0.30) !important;
        }
        [data-testid="stForm"] label {
            color: #d9e1e5 !important;
            font-weight: 650 !important;
        }
        [data-testid="stForm"] input {
            background: #11181d !important;
            color: #ffffff !important;
            border-color: #34434c !important;
        }
        [data-testid="stForm"] button[kind="primaryFormSubmit"] {
            min-height: 2.9rem !important;
            font-size: 0.92rem !important;
        }
        body:has(.hb-light-mode) .login-brand {
            border-color: rgba(47, 143, 131, 0.18);
            background:
                radial-gradient(circle at 85% 12%, rgba(84, 184, 169, 0.17), transparent 16rem),
                linear-gradient(145deg, #e8f4f2 0%, #edf5f5 58%, #f2f5f7 100%);
            box-shadow: 0 20px 48px rgba(34, 52, 61, 0.08);
        }
        body:has(.hb-light-mode) .login-brand-title,
        body:has(.hb-light-mode) .login-form-intro h2 {
            color: #1b3438;
        }
        body:has(.hb-light-mode) .login-brand-subtitle,
        body:has(.hb-light-mode) .login-brand-feature,
        body:has(.hb-light-mode) .login-form-intro p {
            color: #536a70;
        }
        body:has(.hb-light-mode) .login-brand-head {
            border-bottom-color: rgba(47, 143, 131, 0.16);
        }
        body:has(.hb-light-mode) .login-brand-mark {
            border-color: #c7e3df;
            background: linear-gradient(145deg, #d8eeea, #f6fbfa);
        }
        body:has(.hb-light-mode) .login-brand-mark svg {
            stroke: #27776f;
        }
        body:has(.hb-light-mode) .login-brand-kicker {
            color: #27776f;
        }
        body:has(.hb-light-mode) .login-brand-name {
            color: #536a70;
        }
        body:has(.hb-light-mode) .login-brand-name-strong {
            color: #1b3438;
        }
        @media (max-width: 760px) {
            [data-testid="stMainBlockContainer"] {
                max-width: 620px !important;
                padding: 1.4rem 1rem 2rem !important;
            }
            .login-brand {
                min-height: auto;
                padding: 1.5rem;
                border-radius: 17px;
            }
            .login-brand-mark {
                width: 3.35rem;
                height: 3.35rem;
                flex-basis: 3.35rem;
                border-radius: 14px;
            }
            .login-brand-mark svg { width: 1.9rem; height: 1.9rem; }
            .login-brand-name-strong { font-size: 1.28rem; }
            .login-brand-title { max-width: 16ch; font-size: 2rem; }
            .login-brand-features { margin-top: 1.5rem; }
            [data-testid="stForm"] { padding: 1.1rem !important; }
        }
        @media (max-width: 440px) {
            .login-brand-head { gap: 0.75rem; padding-bottom: 1.1rem; }
            .login-brand-features { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.3rem; }
            .login-brand-feature {
                gap: 0.25rem;
                padding-top: 0.5rem;
                font-size: 0.55rem;
                letter-spacing: -0.02em;
            }
            .login-brand-feature::before {
                width: 0.28rem;
                height: 0.28rem;
                flex-basis: 0.28rem;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    brand_column, access_column = st.columns(
        [1.08, 0.92],
        vertical_alignment="center",
        gap="large",
    )
    with brand_column:
        st.markdown(
            """
            <section class="login-brand">
                <div class="login-brand-head">
                    <div class="login-brand-mark" aria-hidden="true">
                        <svg viewBox="0 0 32 32" focusable="false">
                            <path d="M16 8.2c-3.6-2.1-7.3-2.1-11-.8v16.8c3.7-1.3 7.4-1.3 11 .8m0-16.8c3.6-2.1 7.3-2.1 11-.8v16.8c-3.7-1.3-7.4-1.3-11 .8m0-16.8v16.8"/>
                            <path d="M8.5 12.1c1.7-.3 3.3 0 4.8.7m-4.8 3c1.7-.3 3.3 0 4.8.7m8.2-3.7c1.4-.7 3.1-1 4.8-.7m-4.8 3.7c1.4-.7 3.1-1 4.8-.7"/>
                        </svg>
                    </div>
                    <div class="login-brand-identity">
                        <div class="login-brand-kicker">Sistema de gestión</div>
                        <div class="login-brand-name">Librería Bazar</div>
                        <div class="login-brand-name-strong">Humbertito</div>
                    </div>
                </div>
                <div class="login-brand-title">Tu negocio, en buenas manos.</div>
                <div class="login-brand-subtitle">
                    Gestiona ventas, inventario y compras desde una plataforma
                    diseñada para que tengas el control de tu librería.
                </div>
                <div class="login-brand-features">
                    <div class="login-brand-feature">Stock al día</div>
                    <div class="login-brand-feature">Ventas ágiles</div>
                    <div class="login-brand-feature">Control integral</div>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )

    with access_column:
        if auth.cantidad_usuarios() == 0:
            st.markdown(
                """
                <div class="login-form-intro">
                    <h2>Configuración inicial</h2>
                    <p>Crea una cuenta de administrador para comenzar a usar el sistema.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("crear_primer_admin"):
                nombre = st.text_input("Nombre completo")
                username = st.text_input("Usuario")
                password = st.text_input(
                    "Contraseña",
                    type="password"
                )
                confirmar = st.text_input(
                    "Confirmar contraseña",
                    type="password"
                )

                enviar = st.form_submit_button(
                    "Crear administrador",
                    type="primary",
                    width="stretch"
                )

                if enviar:
                    if password != confirmar:
                        st.error("Las contraseñas no coinciden.")
                    else:
                        try:
                            auth.crear_usuario(
                                username,
                                nombre,
                                password,
                                "admin"
                            )
                            notificar_exito(
                                "Administrador creado. Inicia sesión."
                            )
                            st.rerun()
                        except ValueError as error:
                            st.error(str(error))

        else:
            st.markdown(
                """
                <div class="login-form-intro">
                    <h2>Bienvenido de nuevo</h2>
                    <p>Ingresa tus datos para acceder a tu espacio de trabajo.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("form_login"):
                username = st.text_input("Usuario")
                password = st.text_input(
                    "Contraseña",
                    type="password"
                )

                entrar = st.form_submit_button(
                    "Iniciar sesión",
                    type="primary",
                    width="stretch"
                )

                if entrar:
                    usuario = auth.verificar_usuario(
                        username,
                        password
                    )

                    if usuario:
                        st.session_state["usuario"] = usuario
                        st.session_state["menu"] = "Inicio"
                        st.rerun()
                    else:
                        st.error(
                            "Usuario o contraseña incorrectos."
                        )

if "usuario" not in st.session_state:
    pantalla_acceso()
    st.stop()


def normalizar_usuario(usuario):
    """Convierte el usuario de autenticación a un diccionario compatible."""
    if usuario is None:
        return None

    if isinstance(usuario, dict):
        return {
            "id": usuario.get("id"),
            "username": usuario.get("username", ""),
            "nombre": usuario.get("nombre", ""),
            "rol": usuario.get("rol", "empleado"),
            "activo": usuario.get("activo", 1),
        }

    if isinstance(usuario, (tuple, list)):
        datos = list(usuario)

        # Formato habitual: id, username, nombre, rol, activo
        if len(datos) >= 5 and str(datos[3]).lower() in ("admin", "empleado"):
            return {
                "id": datos[0],
                "username": datos[1],
                "nombre": datos[2],
                "rol": str(datos[3]).lower(),
                "activo": datos[4],
            }

        # Formato alternativo: id, username, nombre, password, rol, activo
        if len(datos) >= 6 and str(datos[4]).lower() in ("admin", "empleado"):
            return {
                "id": datos[0],
                "username": datos[1],
                "nombre": datos[2],
                "rol": str(datos[4]).lower(),
                "activo": datos[5],
            }

        # Último recurso: localizar el rol dentro de la fila.
        for indice, valor in enumerate(datos):
            if str(valor).lower() in ("admin", "empleado"):
                return {
                    "id": datos[0] if len(datos) > 0 else None,
                    "username": datos[1] if len(datos) > 1 else "",
                    "nombre": datos[2] if len(datos) > 2 else "",
                    "rol": str(valor).lower(),
                    "activo": 1,
                }

    return None


# Normalizar también sesiones antiguas que hayan guardado una tupla.
usuario_actual = normalizar_usuario(st.session_state.get("usuario"))

if usuario_actual is None:
    st.session_state.pop("usuario", None)
    st.session_state.pop("menu", None)
    pantalla_acceso()
    st.stop()

st.session_state["usuario"] = usuario_actual
es_admin = usuario_actual.get("rol", "empleado") == "admin"


# ==========================================================
# CONEXIÓN A LA BASE DE DATOS
# ==========================================================

def conectar():
    return database.conectar()


# ==========================================================
# CONSULTAS GENERALES
# ==========================================================

def contar_productos():
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM productos")
    resultado = cur.fetchone()[0]
    con.close()
    return resultado


def obtener_stock():
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT COALESCE(SUM(stock), 0) FROM productos")
    resultado = cur.fetchone()[0]
    con.close()
    return resultado


def obtener_productos():
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT
            id,
            codigo,
            nombre,
            categoria,
            precio_compra,
            precio_venta,
            stock,
            stock_minimo
        FROM productos
        ORDER BY id ASC
    """)
    resultado = cur.fetchall()
    con.close()
    return resultado


def generar_excel_productos(productos):
    columnas = [
        "ID",
        "Código",
        "Producto",
        "Categoría",
        "Precio compra (S/)",
        "Precio venta (S/)",
        "Stock",
        "Stock mínimo",
    ]
    filas = [
        {
            "ID": p[0],
            "Código": p[1],
            "Producto": p[2],
            "Categoría": p[3] or "",
            "Precio compra (S/)": p[4],
            "Precio venta (S/)": p[5],
            "Stock": p[6],
            "Stock mínimo": p[7],
        }
        for p in productos
    ]

    archivo = io.BytesIO()
    with pd.ExcelWriter(archivo, engine="openpyxl") as escritor:
        pd.DataFrame(filas, columns=columnas).to_excel(
            escritor,
            index=False,
            sheet_name="Productos",
        )
        hoja = escritor.sheets["Productos"]
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = hoja.dimensions

        anchos = {
            "A": 10,
            "B": 18,
            "C": 34,
            "D": 24,
            "E": 20,
            "F": 20,
            "G": 12,
            "H": 16,
        }
        for columna, ancho in anchos.items():
            hoja.column_dimensions[columna].width = ancho

        if filas:
            from openpyxl.worksheet.table import Table, TableStyleInfo

            tabla = Table(
                displayName="TablaProductos",
                ref=hoja.dimensions,
            )
            tabla.tableStyleInfo = TableStyleInfo(
                name="TableStyleMedium2",
                showFirstColumn=False,
                showLastColumn=False,
                showRowStripes=True,
                showColumnStripes=False,
            )
            hoja.add_table(tabla)

    archivo.seek(0)
    return archivo.getvalue()


def crear_plantilla_productos_excel():
    """Genera una plantilla para registrar productos desde Excel."""
    columnas = [
        "ID",
        "Código",
        "Producto",
        "Categoría",
        "Precio compra (S/)",
        "Precio venta (S/)",
        "Stock",
        "Stock mínimo",
    ]
    archivo = io.BytesIO()
    with pd.ExcelWriter(archivo, engine="openpyxl") as escritor:
        pd.DataFrame(columns=columnas).to_excel(
            escritor,
            index=False,
            sheet_name="Productos",
        )
        hoja = escritor.sheets["Productos"]
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = "A1:H1"
        for columna, ancho in {
            "A": 10,
            "B": 20,
            "C": 34,
            "D": 26,
            "E": 20,
            "F": 20,
            "G": 12,
            "H": 16,
        }.items():
            hoja.column_dimensions[columna].width = ancho

        pd.DataFrame({
            "Instrucciones": [
                "Una fila por producto; no cambies los encabezados.",
                "ID es opcional: conserva el ID exportado para actualizar el mismo producto; déjalo vacío para uno nuevo.",
                "Código y Producto son obligatorios y el código debe ser único.",
                "Precio compra y Precio venta deben ser números no negativos; la venta debe ser mayor que cero.",
                "Stock y Stock mínimo deben ser números enteros no negativos.",
                "Categoría puede quedar vacía. Si Stock mínimo queda vacío, se usará 5.",
                "No incluyas filas de totales ni resúmenes debajo de los productos.",
            ]
        }).to_excel(escritor, index=False, sheet_name="Instrucciones")
        escritor.sheets["Instrucciones"].column_dimensions["A"].width = 105

    archivo.seek(0)
    return archivo.getvalue()


def validar_productos_excel(contenido):
    """Valida el catálogo de productos de Excel sin modificar la base de datos."""
    try:
        original = pd.read_excel(io.BytesIO(contenido), sheet_name=0)
    except Exception as e:
        return [], [f"No se pudo leer el archivo Excel: {e}"]

    if original.empty:
        return [], ["La primera hoja no contiene productos."]

    alias = {
        "id": {"id", "id producto", "identificador"},
        "codigo": {"codigo", "codigo producto", "codigo del producto", "sku"},
        "nombre": {"producto", "nombre", "nombre producto", "nombre del producto"},
        "categoria": {"categoria", "category"},
        "precio_compra": {
            "precio compra", "precio compra s", "precio de compra", "costo",
            "costo unitario", "precio costo",
        },
        "precio_venta": {
            "precio venta", "precio venta s", "precio de venta",
            "precio de venta s", "precio",
        },
        "stock": {"stock", "stock inicial", "existencias"},
        "stock_minimo": {
            "stock minimo", "stock min", "minimo", "stock minimo recomendado",
        },
    }
    columnas = {}
    for columna in original.columns:
        encabezado = _normalizar_encabezado_excel(columna)
        for campo, nombres in alias.items():
            if encabezado in nombres:
                columnas[campo] = columna

    requeridos = [
        "codigo", "nombre", "precio_compra", "precio_venta", "stock",
    ]
    faltantes = [campo for campo in requeridos if campo not in columnas]
    if faltantes:
        nombres = {
            "codigo": "Código",
            "nombre": "Producto",
            "precio_compra": "Precio compra",
            "precio_venta": "Precio venta",
            "stock": "Stock",
        }
        return [], [
            "Faltan columnas requeridas: "
            + ", ".join(nombres[campo] for campo in faltantes)
            + ". Descarga la plantilla para ver los encabezados aceptados."
        ]

    productos_existentes = obtener_productos()
    existentes_por_id = {producto[0]: producto for producto in productos_existentes}
    existentes_por_codigo = {
        str(producto[1]).strip().casefold(): producto
        for producto in productos_existentes
    }
    codigos_archivo = set()
    ids_archivo = set()
    filas_validas = []
    errores = []

    for indice, fila in original.iterrows():
        if all(pd.isna(valor) or str(valor).strip() == "" for valor in fila):
            continue

        numero_fila = int(indice) + 2
        errores_fila = []

        id_producto = None
        if "id" in columnas:
            valor_id = fila[columnas["id"]]
            if not pd.isna(valor_id) and str(valor_id).strip():
                numero_id = _numero_excel(valor_id)
                if (
                    numero_id is None
                    or numero_id <= 0
                    or not numero_id.is_integer()
                ):
                    errores_fila.append("ID debe ser un entero positivo")
                else:
                    id_producto = int(numero_id)
                    if id_producto in ids_archivo:
                        errores_fila.append(
                            f"el ID {id_producto} está repetido en el Excel"
                        )
                    ids_archivo.add(id_producto)

        valor_codigo = fila[columnas["codigo"]]
        if pd.isna(valor_codigo) or not str(valor_codigo).strip():
            codigo = ""
            errores_fila.append("falta el código")
        elif isinstance(valor_codigo, float) and valor_codigo.is_integer():
            codigo = str(int(valor_codigo))
        else:
            codigo = str(valor_codigo).strip()

        clave_codigo = codigo.casefold()
        if clave_codigo:
            if clave_codigo in codigos_archivo:
                errores_fila.append(f"el código {codigo} está repetido en el Excel")
            codigos_archivo.add(clave_codigo)

            producto_por_codigo = existentes_por_codigo.get(clave_codigo)
            producto_por_id = existentes_por_id.get(id_producto)
            if id_producto is None and producto_por_codigo:
                errores_fila.append(
                    f"el código {codigo} ya está registrado con ID "
                    f"{producto_por_codigo[0]}; conserva ese ID en el Excel para actualizarlo"
                )
            elif id_producto is not None and producto_por_id:
                if str(producto_por_id[1]).strip().casefold() != clave_codigo:
                    errores_fila.append(
                        f"el ID {id_producto} ya pertenece al código "
                        f"{producto_por_id[1]}"
                    )
            elif producto_por_codigo and producto_por_codigo[0] != id_producto:
                errores_fila.append(
                    f"el código {codigo} ya pertenece al ID "
                    f"{producto_por_codigo[0]}"
                )

        valor_nombre = fila[columnas["nombre"]]
        nombre = "" if pd.isna(valor_nombre) else str(valor_nombre).strip()
        if not nombre:
            errores_fila.append("falta el nombre del producto")

        def valor_numerico(campo, etiqueta, predicado, mensaje):
            numero = _numero_excel(fila[columnas[campo]])
            if numero is None or not predicado(numero):
                errores_fila.append(f"{etiqueta} {mensaje}")
                return None
            return numero

        precio_compra = valor_numerico(
            "precio_compra", "Precio compra", lambda n: n >= 0,
            "debe ser un número mayor o igual a cero",
        )
        precio_venta = valor_numerico(
            "precio_venta", "Precio venta", lambda n: n > 0,
            "debe ser mayor que cero",
        )
        stock = valor_numerico(
            "stock", "Stock", lambda n: n >= 0 and n.is_integer(),
            "debe ser un entero no negativo",
        )

        valor_stock_minimo = (
            fila[columnas["stock_minimo"]]
            if "stock_minimo" in columnas
            else None
        )
        stock_minimo = (
            5.0 if pd.isna(valor_stock_minimo) or str(valor_stock_minimo).strip() == ""
            else _numero_excel(valor_stock_minimo)
        )
        if (
            stock_minimo is None
            or stock_minimo < 0
            or not stock_minimo.is_integer()
        ):
            errores_fila.append("Stock mínimo debe ser un entero no negativo")
            stock_minimo = None

        valor_categoria = (
            fila[columnas["categoria"]]
            if "categoria" in columnas
            else ""
        )
        categoria = (
            "" if pd.isna(valor_categoria) else str(valor_categoria).strip()
        )

        if errores_fila:
            errores.extend(
                f"Fila {numero_fila}: {error}." for error in errores_fila
            )
            continue

        filas_validas.append({
            "id": id_producto,
            "codigo": codigo,
            "nombre": nombre,
            "categoria": categoria,
            "precio_compra": round(precio_compra, 2),
            "precio_venta": round(precio_venta, 2),
            "stock": int(stock),
            "stock_minimo": int(stock_minimo),
            "fila_excel": numero_fila,
        })

    if not filas_validas and not errores:
        errores.append("No se encontraron filas de productos para importar.")
    return filas_validas, errores


# ==========================================================
# PRODUCTOS
# ==========================================================

def registrar_producto(
    codigo,
    nombre,
    categoria,
    precio_compra,
    precio_venta,
    stock,
    stock_minimo
):
    con = conectar()

    try:
        con.execute("""
            INSERT INTO productos (
                codigo,
                nombre,
                categoria,
                precio_compra,
                precio_venta,
                stock,
                stock_minimo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            codigo,
            nombre,
            categoria,
            precio_compra,
            precio_venta,
            stock,
            stock_minimo
        ))

        con.commit()
        return True, "Producto registrado correctamente."

    except Exception as e:
        if database.es_error_integridad(e):
            return False, "El código del producto ya existe."
        return False, f"Error: {e}"

    finally:
        con.close()


def actualizar_producto(
    producto_id,
    codigo,
    nombre,
    categoria,
    precio_compra,
    precio_venta,
    stock,
    stock_minimo,
):
    con = conectar()

    try:
        cursor = con.execute("""
            UPDATE productos
            SET codigo = ?,
                nombre = ?,
                categoria = ?,
                precio_compra = ?,
                precio_venta = ?,
                stock = ?,
                stock_minimo = ?
            WHERE id = ?
        """, (
            codigo,
            nombre,
            categoria,
            precio_compra,
            precio_venta,
            stock,
            stock_minimo,
            producto_id,
        ))
        con.commit()

        if cursor.rowcount == 0:
            return False, "No se encontró el producto seleccionado."

        return True, "Producto actualizado correctamente."

    except Exception as e:
        if database.es_error_integridad(e):
            return False, "Ese código ya está asignado a otro producto."
        return False, f"No se pudo actualizar el producto: {e}"

    finally:
        con.close()


def eliminar_producto(producto_id):
    con = conectar()

    try:
        ventas_asociadas = con.execute(
            "SELECT COUNT(*) FROM detalle_ventas WHERE producto_id = ?",
            (producto_id,),
        ).fetchone()[0]
        compras_asociadas = con.execute(
            "SELECT COUNT(*) FROM detalle_compras WHERE producto_id = ?",
            (producto_id,),
        ).fetchone()[0]

        if ventas_asociadas or compras_asociadas:
            return (
                False,
                "No se puede eliminar porque el producto tiene movimientos "
                "de venta o compra. Puedes editar sus datos y conservar el historial.",
            )

        cursor = con.execute(
            "DELETE FROM productos WHERE id = ?",
            (producto_id,),
        )
        con.commit()

        if cursor.rowcount == 0:
            return False, "No se encontró el producto seleccionado."

        return True, "Producto eliminado correctamente."

    except Exception as e:
        return False, f"No se pudo eliminar el producto: {e}"

    finally:
        con.close()


def importar_productos_excel(filas):
    """Importa o actualiza por ID todos los productos en una transacción."""
    con = conectar()
    try:
        for fila in filas:
            valores = (
                fila["codigo"],
                fila["nombre"],
                fila["categoria"],
                fila["precio_compra"],
                fila["precio_venta"],
                fila["stock"],
                fila["stock_minimo"],
            )
            id_producto = fila.get("id")
            if id_producto is not None:
                existente = con.execute(
                    "SELECT codigo FROM productos WHERE id = ?",
                    (id_producto,),
                ).fetchone()
                if existente:
                    if str(existente[0]).strip().casefold() != fila["codigo"].casefold():
                        raise ValueError(
                            f"El ID {id_producto} ya pertenece a "
                            f"{existente[0]}; no se modificó ningún producto."
                        )
                    con.execute(
                        """
                        UPDATE productos SET
                            codigo = ?, nombre = ?, categoria = ?,
                            precio_compra = ?, precio_venta = ?, stock = ?,
                            stock_minimo = ?
                        WHERE id = ?
                        """,
                        (*valores, id_producto),
                    )
                else:
                    codigo_existente = con.execute(
                        "SELECT id FROM productos WHERE LOWER(codigo) = LOWER(?)",
                        (fila["codigo"],),
                    ).fetchone()
                    if codigo_existente:
                        raise ValueError(
                            f"El código {fila['codigo']} ya pertenece al ID "
                            f"{codigo_existente[0]}; no se modificó ningún producto."
                        )
                    con.execute(
                        """
                        INSERT INTO productos (
                            id, codigo, nombre, categoria, precio_compra,
                            precio_venta, stock, stock_minimo
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (id_producto, *valores),
                    )
            else:
                codigo_existente = con.execute(
                    "SELECT id FROM productos WHERE LOWER(codigo) = LOWER(?)",
                    (fila["codigo"],),
                ).fetchone()
                if codigo_existente:
                    raise ValueError(
                        f"El código {fila['codigo']} ya existe con ID "
                        f"{codigo_existente[0]}; no se modificó ningún producto."
                    )
                con.execute(
                    """
                    INSERT INTO productos (
                        codigo, nombre, categoria, precio_compra, precio_venta,
                        stock, stock_minimo
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    valores,
                )

        if database.usar_supabase():
            con.execute(
                """
                SELECT setval(
                    pg_get_serial_sequence('productos', 'id'),
                    COALESCE((SELECT MAX(id) FROM productos), 1),
                    EXISTS(SELECT 1 FROM productos)
                )
                """
            )
        con.commit()
        return True, (
            f"Se procesaron {len(filas)} productos. Los IDs incluidos en el "
            "Excel se conservaron; los vacíos se asignaron automáticamente."
        )
    except Exception as e:
        con.rollback()
        if database.es_error_integridad(e):
            return False, "No se importó ningún producto porque hay códigos repetidos."
        return False, f"No se pudieron importar los productos: {e}"
    finally:
        con.close()


def eliminar_todos_productos():
    """Elimina el catálogo solo si no tiene ventas ni compras asociadas."""
    con = conectar()
    try:
        cantidad_productos = con.execute(
            "SELECT COUNT(*) FROM productos"
        ).fetchone()[0]
        if not cantidad_productos:
            return False, "No hay productos registrados para eliminar."

        ventas_asociadas = con.execute(
            "SELECT COUNT(*) FROM detalle_ventas"
        ).fetchone()[0]
        compras_asociadas = con.execute(
            "SELECT COUNT(*) FROM detalle_compras"
        ).fetchone()[0]
        if ventas_asociadas or compras_asociadas:
            return False, (
                "No se eliminó ningún producto para proteger el historial. "
                f"Hay {ventas_asociadas} detalle(s) de venta y "
                f"{compras_asociadas} detalle(s) de compra asociados. "
                "Elimina o conserva esos movimientos antes de borrar el catálogo."
            )

        con.execute("DELETE FROM productos")
        if database.usar_supabase():
            con.execute(
                "SELECT setval(pg_get_serial_sequence('productos', 'id'), 1, false)"
            )
        else:
            con.execute(
                "DELETE FROM sqlite_sequence WHERE name = 'productos'"
            )
        con.commit()
        return True, f"Se eliminaron {cantidad_productos} productos."
    except Exception as e:
        con.rollback()
        return False, f"No se pudieron eliminar los productos: {e}"
    finally:
        con.close()


# ==========================================================
# VENTAS
# ==========================================================

def crear_plantilla_ventas_excel():
    """Genera una plantilla vacía para importar ventas históricas."""
    archivo = io.BytesIO()
    columnas = [
        "Fecha",
        "Código del producto",
        "Cantidad",
        "Precio unitario (S/)",
        "N° Boleta",
    ]

    with pd.ExcelWriter(archivo, engine="openpyxl") as escritor:
        pd.DataFrame(columns=columnas).to_excel(
            escritor,
            index=False,
            sheet_name="Ventas",
        )
        hoja = escritor.sheets["Ventas"]
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = "A1:E1"
        for columna, ancho in {"A": 18, "B": 24, "C": 12, "D": 22, "E": 18}.items():
            hoja.column_dimensions[columna].width = ancho

        pd.DataFrame({
            "Instrucciones": [
                "Registra una fila por cada producto vendido.",
                "Usa la fecha impresa en la boleta; no se aceptan fechas futuras.",
                "El código debe coincidir con el catálogo de productos del sistema.",
                "Cantidad debe ser un entero mayor que cero.",
                "Usa el precio unitario que figura en la boleta.",
                "N° Boleta es opcional; repite el mismo número para agrupar sus productos.",
                "No agregues totales ni filas de resumen debajo de las ventas.",
            ]
        }).to_excel(escritor, index=False, sheet_name="Instrucciones")
        escritor.sheets["Instrucciones"].column_dimensions["A"].width = 100

    archivo.seek(0)
    return archivo.getvalue()


def _normalizar_encabezado_excel(valor):
    texto = unicodedata.normalize("NFKD", str(valor))
    texto = "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
    return re.sub(r"[^a-z0-9]+", " ", texto.lower()).strip()


def _numero_excel(valor):
    if pd.isna(valor):
        return None
    if isinstance(valor, (int, float)):
        return float(valor)

    texto = re.sub(r"[^0-9,.-]", "", str(valor).strip())
    if not texto:
        return None
    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif "," in texto:
        texto = texto.replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return None


def validar_ventas_excel(contenido):
    """Lee y valida el Excel sin modificar la base de datos."""
    try:
        original = pd.read_excel(io.BytesIO(contenido), sheet_name=0)
    except Exception as e:
        return [], [f"No se pudo leer el archivo Excel: {e}"], pd.DataFrame()

    if original.empty:
        return [], ["La primera hoja no contiene filas de ventas."], original

    encabezados = {
        "fecha": {"fecha", "fecha de venta", "fecha boleta"},
        "codigo": {"codigo", "codigo producto", "codigo del producto", "sku"},
        "producto": {"producto", "nombre producto", "nombre del producto"},
        "cantidad": {"cantidad", "unidades"},
        "precio": {
            "precio unitario", "precio unitario s", "precio de venta", "precio venta", "precio"
        },
        "boleta": {
            "boleta", "numero boleta", "numero de boleta", "n boleta",
            "nro boleta", "ticket", "comprobante", "referencia"
        },
    }
    columnas = {}
    for columna in original.columns:
        normalizado = _normalizar_encabezado_excel(columna)
        for campo, alias in encabezados.items():
            if normalizado in alias:
                columnas[campo] = columna

    requeridos = ["fecha", "cantidad", "precio"]
    faltantes = [campo for campo in requeridos if campo not in columnas]
    if "codigo" not in columnas and "producto" not in columnas:
        faltantes.append("Código del producto o Producto")
    if faltantes:
        return [], [
            "Faltan columnas requeridas: " + ", ".join(faltantes) + ". "
            "Descarga la plantilla para ver los encabezados aceptados."
        ], original

    productos = obtener_productos()
    por_codigo = {str(producto[1]).strip().casefold(): producto for producto in productos}
    por_nombre = {}
    for producto in productos:
        por_nombre.setdefault(str(producto[2]).strip().casefold(), []).append(producto)

    filas_validas = []
    errores = []
    hoy = datetime.now().date()

    for indice, fila in original.iterrows():
        valores = [fila[columna] for columna in original.columns]
        if all(pd.isna(valor) or str(valor).strip() == "" for valor in valores):
            continue

        numero_fila = int(indice) + 2
        errores_fila = []
        producto = None

        valor_codigo = fila[columnas["codigo"]] if "codigo" in columnas else None
        valor_nombre = fila[columnas["producto"]] if "producto" in columnas else None
        if not pd.isna(valor_codigo) and str(valor_codigo).strip():
            producto = por_codigo.get(str(valor_codigo).strip().casefold())
            if producto is None:
                errores_fila.append(f"código de producto no registrado: {valor_codigo}")
        elif not pd.isna(valor_nombre) and str(valor_nombre).strip():
            coincidencias = por_nombre.get(str(valor_nombre).strip().casefold(), [])
            if len(coincidencias) == 1:
                producto = coincidencias[0]
            elif len(coincidencias) > 1:
                errores_fila.append(f"nombre ambiguo; usa su código: {valor_nombre}")
            else:
                errores_fila.append(f"producto no registrado: {valor_nombre}")
        else:
            errores_fila.append("falta el código o nombre del producto")

        valor_fecha = fila[columnas["fecha"]]
        fecha_parseada = None
        if pd.isna(valor_fecha):
            errores_fila.append("falta la fecha")
        else:
            try:
                if isinstance(valor_fecha, (int, float)) and not isinstance(valor_fecha, bool):
                    fecha_parseada = (
                        pd.Timestamp("1899-12-30")
                        + pd.to_timedelta(float(valor_fecha), unit="D")
                    ).date()
                else:
                    fecha_convertida = pd.to_datetime(
                        valor_fecha,
                        dayfirst=True,
                        format="mixed",
                        errors="coerce",
                    )
                    if not pd.isna(fecha_convertida):
                        fecha_parseada = fecha_convertida.date()
            except (TypeError, ValueError, OverflowError):
                fecha_parseada = None
            if fecha_parseada is None:
                errores_fila.append("fecha inválida")
            elif fecha_parseada > hoy:
                errores_fila.append("la fecha no puede ser futura")

        cantidad_numero = _numero_excel(fila[columnas["cantidad"]])
        if cantidad_numero is None or cantidad_numero <= 0 or not cantidad_numero.is_integer():
            errores_fila.append("la cantidad debe ser un entero mayor que cero")

        precio = _numero_excel(fila[columnas["precio"]])
        if precio is None or precio <= 0:
            errores_fila.append("el precio unitario debe ser mayor que cero")

        referencia = ""
        if "boleta" in columnas:
            valor_referencia = fila[columnas["boleta"]]
            if not pd.isna(valor_referencia):
                referencia = str(valor_referencia).strip()
                if referencia.endswith(".0") and referencia[:-2].isdigit():
                    referencia = referencia[:-2]

        if errores_fila:
            errores.extend([f"Fila {numero_fila}: {error}" for error in errores_fila])
            continue

        filas_validas.append({
            "fila_excel": numero_fila,
            "fecha": fecha_parseada.isoformat() + " 12:00:00",
            "producto_id": producto[0],
            "codigo": producto[1],
            "producto": producto[2],
            "cantidad": int(cantidad_numero),
            "precio_unitario": round(precio, 2),
            "subtotal": round(precio * cantidad_numero, 2),
            "referencia": referencia,
        })

    if not filas_validas and not errores:
        errores.append("No se encontraron filas de ventas para importar.")
    return filas_validas, errores, original


def hash_importacion_registrada(hash_archivo):
    con = conectar()
    try:
        return con.execute(
            "SELECT nombre_archivo, fecha_importacion FROM importaciones_ventas "
            "WHERE hash_archivo = ?",
            (hash_archivo,),
        ).fetchone()
    finally:
        con.close()


def importar_ventas_excel(filas, hash_archivo, nombre_archivo, descontar_stock=False):
    """Importa todo el archivo en una transacción o no importa ninguna fila."""
    con = conectar()
    try:
        existente = con.execute(
            "SELECT 1 FROM importaciones_ventas WHERE hash_archivo = ?",
            (hash_archivo,),
        ).fetchone()
        if existente:
            return False, "Este mismo archivo ya fue importado."

        cantidades = {}
        for fila in filas:
            cantidades[fila["producto_id"]] = (
                cantidades.get(fila["producto_id"], 0) + fila["cantidad"]
            )

        descontar_stock_aplicado = bool(descontar_stock)
        aviso_stock = ""
        if descontar_stock_aplicado:
            ids_productos = list(cantidades)
            marcadores = ", ".join("?" for _ in ids_productos)
            stocks = con.execute(
                f"SELECT id, stock FROM productos WHERE id IN ({marcadores})",
                tuple(ids_productos),
            ).fetchall()
            stock_por_producto = {producto_id: stock for producto_id, stock in stocks}
            nombres_producto = {
                fila["producto_id"]: fila["producto"] for fila in filas
            }
            productos_sin_stock = [
                f"{nombres_producto[producto_id]} (se necesitan {cantidad}, "
                f"hay {stock_por_producto.get(producto_id, 0)})"
                for producto_id, cantidad in cantidades.items()
                if producto_id not in stock_por_producto
                or cantidad > stock_por_producto[producto_id]
            ]
            if productos_sin_stock:
                # El historial debe poder cargarse aunque el inventario actual ya
                # refleje esas ventas o no alcance para volver a descontarlas.
                # No descontamos ningún producto para evitar una actualización parcial.
                descontar_stock_aplicado = False
                lista_productos = "; ".join(productos_sin_stock[:3])
                if len(productos_sin_stock) > 3:
                    lista_productos += f" y {len(productos_sin_stock) - 3} más"
                aviso_stock = (
                    " No se descontó stock porque no alcanza para: "
                    f"{lista_productos}."
                )

        grupos = {}
        for fila in filas:
            clave = (
                (fila["fecha"], fila["referencia"])
                if fila["referencia"]
                else (fila["fecha"], f"__fila_{fila['fila_excel']}")
            )
            grupos.setdefault(clave, []).append(fila)

        grupos_lista = list(grupos.items())
        detalles_para_insertar = []
        for inicio in range(0, len(grupos_lista), 250):
            lote_grupos = grupos_lista[inicio:inicio + 250]
            valores_ventas = []
            for (fecha, referencia), detalles in lote_grupos:
                total = round(sum(detalle["subtotal"] for detalle in detalles), 2)
                valores_ventas.append(
                    (fecha, total, int(descontar_stock_aplicado), referencia or None)
                )

            marcadores = ", ".join("(?, ?, ?, ?)" for _ in valores_ventas)
            ventas_insertadas = con.execute(
                "INSERT INTO ventas (fecha, total, stock_descontado, referencia) "
                f"VALUES {marcadores} RETURNING id, fecha, referencia",
                tuple(valor for venta in valores_ventas for valor in venta),
            ).fetchall()
            ids_por_clave = {
                (str(fecha), referencia): venta_id
                for venta_id, fecha, referencia in ventas_insertadas
            }

            for (fecha, referencia), detalles in lote_grupos:
                venta_id = ids_por_clave[(fecha, referencia or None)]
                detalles_para_insertar.extend(
                    (
                        venta_id,
                        detalle["producto_id"],
                        detalle["cantidad"],
                        detalle["precio_unitario"],
                        detalle["subtotal"],
                    )
                    for detalle in detalles
                )

        for inicio in range(0, len(detalles_para_insertar), 150):
            lote_detalles = detalles_para_insertar[inicio:inicio + 150]
            marcadores = ", ".join("(?, ?, ?, ?, ?)" for _ in lote_detalles)
            con.execute(
                "INSERT INTO detalle_ventas "
                "(venta_id, producto_id, cantidad, precio_unitario, subtotal) "
                f"VALUES {marcadores}",
                tuple(valor for detalle in lote_detalles for valor in detalle),
            )

        if descontar_stock_aplicado:
            productos_lote = list(cantidades.items())
            for inicio in range(0, len(productos_lote), 250):
                lote_productos = productos_lote[inicio:inicio + 250]
                casos = " ".join("WHEN ? THEN ?" for _ in lote_productos)
                ids_sql = ", ".join("?" for _ in lote_productos)
                parametros = tuple(
                    valor
                    for producto_id, cantidad in lote_productos
                    for valor in (producto_id, cantidad)
                ) + tuple(producto_id for producto_id, _ in lote_productos)
                con.execute(
                    "UPDATE productos SET stock = stock - CASE id "
                    f"{casos} ELSE 0 END WHERE id IN ({ids_sql})",
                    parametros,
                )

        con.execute(
            "INSERT INTO importaciones_ventas "
            "(hash_archivo, nombre_archivo, fecha_importacion, filas_importadas) "
            "VALUES (?, ?, ?, ?)",
            (
                hash_archivo,
                nombre_archivo,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                len(filas),
            ),
        )
        con.commit()
        return True, (
            f"Se importaron {len(filas)} filas de venta correctamente.{aviso_stock}"
        )
    except Exception as e:
        con.rollback()
        return False, f"No se pudo importar el archivo: {e}"
    finally:
        con.close()

def obtener_ventas():
    con = conectar()

    resultado = con.execute("""
        SELECT
            v.id,
            v.fecha,
            v.total,
            p.nombre,
            dv.cantidad,
            dv.precio_unitario,
            dv.subtotal,
            v.stock_descontado,
            v.referencia,
            dv.id
        FROM ventas v
        JOIN detalle_ventas dv
            ON v.id = dv.venta_id
        JOIN productos p
            ON dv.producto_id = p.id
        ORDER BY dv.id ASC
    """).fetchall()

    con.close()
    return resultado


def eliminar_venta(venta_id, restaurar_stock_venta_antigua=False):
    """Elimina una venta y restaura el stock si esa venta lo había descontado."""
    con = conectar()

    try:
        venta = con.execute(
            "SELECT stock_descontado FROM ventas WHERE id = ?",
            (venta_id,),
        ).fetchone()

        if venta is None:
            return False, "No se encontró la venta seleccionada."

        detalles = con.execute(
            "SELECT producto_id, cantidad FROM detalle_ventas WHERE venta_id = ?",
            (venta_id,),
        ).fetchall()

        stock_descontado = venta[0]
        reponer_stock = (
            stock_descontado == 1
            or (stock_descontado is None and restaurar_stock_venta_antigua)
        )

        if reponer_stock:
            for producto_id, cantidad in detalles:
                con.execute(
                    "UPDATE productos SET stock = stock + ? WHERE id = ?",
                    (cantidad, producto_id),
                )

        con.execute("DELETE FROM detalle_ventas WHERE venta_id = ?", (venta_id,))
        con.execute("DELETE FROM ventas WHERE id = ?", (venta_id,))
        con.commit()

        if reponer_stock:
            return True, "Venta eliminada y stock restaurado."
        return True, "Venta eliminada. El stock actual no se modificó."

    except Exception as e:
        con.rollback()
        return False, f"No se pudo eliminar la venta: {e}"

    finally:
        con.close()


def eliminar_todas_ventas():
    """Elimina todas las ventas y sus detalles, reponiendo el stock descontado."""
    con = conectar()

    try:
        cantidad_ventas = con.execute(
            "SELECT COUNT(*) FROM ventas"
        ).fetchone()[0]
        if not cantidad_ventas:
            return False, "No hay ventas registradas para eliminar."

        stock_a_reponer = con.execute("""
            SELECT dv.producto_id, SUM(dv.cantidad)
            FROM detalle_ventas dv
            JOIN ventas v ON v.id = dv.venta_id
            WHERE v.stock_descontado = 1
            GROUP BY dv.producto_id
        """).fetchall()

        for producto_id, cantidad in stock_a_reponer:
            con.execute(
                "UPDATE productos SET stock = stock + ? WHERE id = ?",
                (cantidad, producto_id),
            )

        con.execute("DELETE FROM detalle_ventas")
        con.execute("DELETE FROM ventas")
        # Permite volver a importar los mismos archivos después de vaciar ventas.
        con.execute("DELETE FROM importaciones_ventas")
        if database.usar_supabase():
            con.execute(
                "SELECT setval(pg_get_serial_sequence('ventas', 'id'), 1, false)"
            )
            con.execute(
                "SELECT setval(pg_get_serial_sequence('detalle_ventas', 'id'), 1, false)"
            )
        else:
            con.execute(
                "DELETE FROM sqlite_sequence "
                "WHERE name IN ('ventas', 'detalle_ventas')"
            )
        con.commit()
        return True, (
            f"Se eliminaron {cantidad_ventas} ventas. El stock se restauró "
            "para las ventas que estaban marcadas como descontadas."
        )

    except Exception as e:
        con.rollback()
        return False, f"No se pudieron eliminar todas las ventas: {e}"

    finally:
        con.close()


def registrar_venta(
    producto_id,
    cantidad,
    fecha_venta=None,
    precio_unitario=None,
    descontar_stock=True,
):
    con = conectar()

    try:
        producto = con.execute("""
            SELECT nombre, precio_venta, stock
            FROM productos
            WHERE id = ?
        """, (producto_id,)).fetchone()

        if producto is None:
            return False, "Producto no encontrado."

        nombre, precio_venta, stock_actual = producto

        if precio_unitario is None:
            precio_unitario = precio_venta

        if cantidad <= 0:
            return False, "La cantidad debe ser mayor que 0."

        if precio_unitario <= 0:
            return False, "El precio unitario debe ser mayor que 0."

        if descontar_stock and cantidad > stock_actual:
            return False, f"Stock insuficiente. Stock disponible: {stock_actual}"

        subtotal = precio_unitario * cantidad
        if fecha_venta is None:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif fecha_venta == datetime.now().date():
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            # Las boletas antiguas suelen tener solo fecha, sin hora. El mediodía
            # evita que la fecha cambie al convertirla en zonas horarias distintas.
            fecha = f"{fecha_venta.isoformat()} 12:00:00"

        cur = con.execute("""
            INSERT INTO ventas (fecha, total, stock_descontado)
            VALUES (?, ?, ?)
            RETURNING id
        """, (fecha, subtotal, int(bool(descontar_stock))))

        venta_id = cur.fetchone()[0]

        con.execute("""
            INSERT INTO detalle_ventas (
                venta_id,
                producto_id,
                cantidad,
                precio_unitario,
                subtotal
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            venta_id,
            producto_id,
            cantidad,
            precio_unitario,
            subtotal
        ))

        nuevo_stock = stock_actual
        if descontar_stock:
            nuevo_stock = stock_actual - cantidad
            con.execute("""
                UPDATE productos
                SET stock = ?
                WHERE id = ?
            """, (nuevo_stock, producto_id))

        con.commit()

        return True, (
            f"Venta registrada correctamente. "
            f"Producto: {nombre}. "
            f"Total: S/ {subtotal:.2f}. "
            + (f"Stock restante: {nuevo_stock}." if descontar_stock else
               " El stock actual no se modificó.")
        )

    except Exception as e:
        con.rollback()
        return False, f"Error al registrar venta: {e}"

    finally:
        con.close()


# ==========================================================
# COMPRAS
# ==========================================================

def obtener_compras():
    con = conectar()

    try:
        return con.execute("""
            SELECT
                c.id,
                c.fecha,
                c.total,
                c.referencia,
                p.nombre,
                dc.cantidad,
                dc.precio_unitario,
                dc.subtotal
            FROM compras c
            JOIN detalle_compras dc
                ON c.id = dc.compra_id
            JOIN productos p
                ON dc.producto_id = p.id
            ORDER BY c.id DESC
        """).fetchall()
    except Exception:
        # Permite consultar compras existentes si aún no se aplicó la migración
        # que añade el número de comprobante al esquema remoto.
        con.close()
        con = conectar()
        return con.execute("""
            SELECT
                c.id,
                c.fecha,
                c.total,
                NULL,
                p.nombre,
                dc.cantidad,
                dc.precio_unitario,
                dc.subtotal
            FROM compras c
            JOIN detalle_compras dc
                ON c.id = dc.compra_id
            JOIN productos p
                ON dc.producto_id = p.id
            ORDER BY c.id DESC
        """).fetchall()
    finally:
        con.close()


def registrar_compra(producto_id, cantidad, precio_compra):
    con = conectar()

    try:
        producto = con.execute("""
            SELECT nombre, stock
            FROM productos
            WHERE id = ?
        """, (producto_id,)).fetchone()

        if producto is None:
            return False, "Producto no encontrado."

        nombre, stock_actual = producto

        if cantidad <= 0:
            return False, "La cantidad debe ser mayor que 0."

        if precio_compra <= 0:
            return False, "El precio de compra debe ser mayor que 0."

        subtotal = precio_compra * cantidad
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cur = con.execute("""
            INSERT INTO compras (fecha, total)
            VALUES (?, ?)
            RETURNING id
        """, (fecha, subtotal))

        compra_id = cur.fetchone()[0]

        con.execute("""
            INSERT INTO detalle_compras (
                compra_id,
                producto_id,
                cantidad,
                precio_unitario,
                subtotal
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            compra_id,
            producto_id,
            cantidad,
            precio_compra,
            subtotal
        ))

        nuevo_stock = stock_actual + cantidad

        con.execute("""
            UPDATE productos
            SET stock = ?,
                precio_compra = ?
            WHERE id = ?
        """, (
            nuevo_stock,
            precio_compra,
            producto_id
        ))

        con.commit()

        return True, (
            f"Compra registrada correctamente. "
            f"Producto: {nombre}. "
            f"Total: S/ {subtotal:.2f}. "
            f"Stock actualizado: {nuevo_stock}."
        )

    except Exception as e:
        con.rollback()
        return False, f"Error al registrar compra: {e}"

    finally:
        con.close()


def crear_plantilla_compras_excel():
    """Crea una plantilla vacía y una hoja separada con filas de demostración."""
    archivo = io.BytesIO()
    columnas = [
        "Fecha",
        "Código del producto",
        "Cantidad",
        "Precio de compra unitario (S/)",
        "Comprobante",
    ]

    with pd.ExcelWriter(archivo, engine="openpyxl") as escritor:
        pd.DataFrame(columns=columnas).to_excel(
            escritor,
            index=False,
            sheet_name="Compras",
        )
        hoja = escritor.sheets["Compras"]
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = "A1:E1"
        for columna, ancho in {
            "A": 18, "B": 24, "C": 12, "D": 32, "E": 24
        }.items():
            hoja.column_dimensions[columna].width = ancho

        pd.DataFrame({
            "Fecha": ["2026-10-01", "2026-10-01", "2026-10-02", "2026-10-03"],
            "Código del producto": [
                "ESC-001", "DEMO-ESC-002", "DEMO-CUA-001", "DEMO-PAP-001"
            ],
            "Cantidad": [24, 24, 12, 30],
            "Precio de compra unitario (S/)": [0.50, 0.70, 2.50, 0.50],
            "Comprobante": [
                "COMP-DEMO-001", "COMP-DEMO-001", "COMP-DEMO-002", "COMP-DEMO-003"
            ],
        }).to_excel(escritor, index=False, sheet_name="Ejemplo DEMO - NO IMPORTAR")
        ejemplo = escritor.sheets["Ejemplo DEMO - NO IMPORTAR"]
        ejemplo.freeze_panes = "A2"
        ejemplo.auto_filter.ref = "A1:E5"
        for columna, ancho in {
            "A": 18, "B": 24, "C": 12, "D": 32, "E": 24
        }.items():
            ejemplo.column_dimensions[columna].width = ancho

        pd.DataFrame({
            "Instrucciones": [
                "La hoja Compras está vacía y es la que lee el sistema.",
                "La hoja Ejemplo DEMO - NO IMPORTAR contiene valores ficticios para reemplazar.",
                "Copia las filas necesarias del ejemplo a Compras y reemplaza todos los valores por los del comprobante real.",
                "Cada fila representa un producto comprado; una misma factura puede ocupar varias filas.",
                "Repite el mismo Comprobante y Fecha en las filas de productos de una misma compra.",
                "Usa la fecha del comprobante, el código registrado en el sistema, cantidad entera y costo unitario real.",
                "No subas filas de demostración: los códigos DEMO y precios son solo ilustrativos.",
            ]
        }).to_excel(escritor, index=False, sheet_name="Instrucciones")
        escritor.sheets["Instrucciones"].column_dimensions["A"].width = 110

    archivo.seek(0)
    return archivo.getvalue()


def validar_compras_excel(contenido):
    """Valida las compras del Excel antes de insertar o modificar el inventario."""
    try:
        original = pd.read_excel(io.BytesIO(contenido), sheet_name="Compras")
    except ValueError:
        try:
            original = pd.read_excel(io.BytesIO(contenido), sheet_name=0)
        except Exception as e:
            return [], [f"No se pudo leer la hoja Compras: {e}"], pd.DataFrame()
    except Exception as e:
        return [], [f"No se pudo leer el archivo Excel: {e}"], pd.DataFrame()

    if original.empty:
        return [], ["La hoja Compras no contiene filas para importar."], original

    encabezados = {
        "fecha": {"fecha", "fecha de compra", "fecha comprobante"},
        "codigo": {"codigo", "codigo producto", "codigo del producto", "sku"},
        "producto": {"producto", "nombre producto", "nombre del producto"},
        "cantidad": {"cantidad", "unidades", "cantidad comprada"},
        "precio": {
            "precio unitario", "precio de compra", "precio de compra unitario",
            "precio de compra unitario s", "precio unitario s", "costo unitario",
            "costo", "precio",
        },
        "referencia": {
            "comprobante", "numero comprobante", "n comprobante", "nro comprobante",
            "factura", "numero factura", "boleta", "referencia",
        },
    }
    columnas = {}
    for columna in original.columns:
        normalizado = _normalizar_encabezado_excel(columna)
        for campo, alias in encabezados.items():
            if normalizado in alias:
                columnas[campo] = columna

    faltantes = [campo for campo in ("fecha", "cantidad", "precio") if campo not in columnas]
    if "codigo" not in columnas and "producto" not in columnas:
        faltantes.append("Código del producto o Producto")
    if faltantes:
        return [], [
            "Faltan columnas requeridas: " + ", ".join(faltantes) + ". "
            "Descarga la plantilla para ver el formato aceptado."
        ], original

    productos = obtener_productos()
    por_codigo = {str(producto[1]).strip().casefold(): producto for producto in productos}
    por_nombre = {}
    for producto in productos:
        por_nombre.setdefault(str(producto[2]).strip().casefold(), []).append(producto)

    filas_validas = []
    errores = []
    hoy = datetime.now().date()

    for indice, fila in original.iterrows():
        if all(pd.isna(valor) or str(valor).strip() == "" for valor in fila.tolist()):
            continue

        numero_fila = int(indice) + 2
        errores_fila = []
        producto = None
        valor_codigo = fila[columnas["codigo"]] if "codigo" in columnas else None
        valor_nombre = fila[columnas["producto"]] if "producto" in columnas else None
        if not pd.isna(valor_codigo) and str(valor_codigo).strip():
            producto = por_codigo.get(str(valor_codigo).strip().casefold())
            if producto is None:
                errores_fila.append(f"código de producto no registrado: {valor_codigo}")
        elif not pd.isna(valor_nombre) and str(valor_nombre).strip():
            coincidencias = por_nombre.get(str(valor_nombre).strip().casefold(), [])
            if len(coincidencias) == 1:
                producto = coincidencias[0]
            elif len(coincidencias) > 1:
                errores_fila.append(f"nombre ambiguo; usa su código: {valor_nombre}")
            else:
                errores_fila.append(f"producto no registrado: {valor_nombre}")
        else:
            errores_fila.append("falta el código o nombre del producto")

        valor_fecha = fila[columnas["fecha"]]
        fecha_parseada = None
        if pd.isna(valor_fecha):
            errores_fila.append("falta la fecha")
        else:
            try:
                if isinstance(valor_fecha, (int, float)) and not isinstance(valor_fecha, bool):
                    fecha_parseada = (
                        pd.Timestamp("1899-12-30")
                        + pd.to_timedelta(float(valor_fecha), unit="D")
                    ).date()
                else:
                    fecha_convertida = pd.to_datetime(
                        valor_fecha,
                        dayfirst=True,
                        format="mixed",
                        errors="coerce",
                    )
                    if not pd.isna(fecha_convertida):
                        fecha_parseada = fecha_convertida.date()
            except (TypeError, ValueError, OverflowError):
                fecha_parseada = None
            if fecha_parseada is None:
                errores_fila.append("fecha inválida")
            elif fecha_parseada > hoy:
                errores_fila.append("la fecha no puede ser futura")

        cantidad_numero = _numero_excel(fila[columnas["cantidad"]])
        if cantidad_numero is None or cantidad_numero <= 0 or not cantidad_numero.is_integer():
            errores_fila.append("la cantidad debe ser un entero mayor que cero")

        precio = _numero_excel(fila[columnas["precio"]])
        if precio is None or precio <= 0:
            errores_fila.append("el precio de compra unitario debe ser mayor que cero")

        referencia = ""
        if "referencia" in columnas:
            valor_referencia = fila[columnas["referencia"]]
            if not pd.isna(valor_referencia):
                referencia = str(valor_referencia).strip()
                if referencia.endswith(".0") and referencia[:-2].isdigit():
                    referencia = referencia[:-2]

        if errores_fila:
            errores.extend([f"Fila {numero_fila}: {error}" for error in errores_fila])
            continue

        filas_validas.append({
            "fila_excel": numero_fila,
            "fecha": fecha_parseada.isoformat() + " 12:00:00",
            "producto_id": producto[0],
            "codigo": producto[1],
            "producto": producto[2],
            "cantidad": int(cantidad_numero),
            "precio_unitario": round(precio, 2),
            "subtotal": round(precio * cantidad_numero, 2),
            "referencia": referencia,
        })

    if not filas_validas and not errores:
        errores.append("No se encontraron filas de compras para importar.")
    return filas_validas, errores, original


def hash_importacion_compras_registrada(hash_archivo):
    con = conectar()
    try:
        return con.execute(
            "SELECT nombre_archivo, fecha_importacion FROM importaciones_compras "
            "WHERE hash_archivo = ?",
            (hash_archivo,),
        ).fetchone()
    except Exception as error:
        return {"error": str(error)}
    finally:
        con.close()


def obtener_auditoria_compras():
    """Resume consistencia interna de compras; no sustituye cotejar comprobantes."""
    con = conectar()
    try:
        resumen = con.execute("""
            SELECT
                COUNT(*) AS compras,
                COALESCE(SUM(c.total), 0) AS total_encabezados,
                COALESCE(SUM(COALESCE(d.suma_detalles, 0)), 0) AS total_detalles,
                COALESCE(SUM(COALESCE(d.lineas, 0)), 0) AS lineas,
                MIN(c.fecha) AS primera_fecha,
                MAX(c.fecha) AS ultima_fecha,
                SUM(CASE WHEN d.compra_id IS NULL THEN 1 ELSE 0 END) AS sin_detalles
            FROM compras c
            LEFT JOIN (
                SELECT compra_id, SUM(subtotal) AS suma_detalles, COUNT(*) AS lineas
                FROM detalle_compras
                GROUP BY compra_id
            ) d ON d.compra_id = c.id
        """).fetchone()
        diferencias = con.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT c.id
                FROM compras c
                LEFT JOIN detalle_compras dc ON dc.compra_id = c.id
                GROUP BY c.id, c.total
                HAVING COUNT(dc.id) = 0
                    OR ABS(c.total - COALESCE(SUM(dc.subtotal), 0)) > 0.01
            ) inconsistentes
        """).fetchone()[0]
        return {
            "compras": resumen[0] or 0,
            "total_encabezados": float(resumen[1] or 0),
            "total_detalles": float(resumen[2] or 0),
            "lineas": resumen[3] or 0,
            "primera_fecha": resumen[4],
            "ultima_fecha": resumen[5],
            "sin_detalles": resumen[6] or 0,
            "diferencias": diferencias,
        }
    finally:
        con.close()


def obtener_historial_importaciones_compras():
    """Devuelve auditoría de cargas; NULL indica que la versión antigua no guardó el dato."""
    con = conectar()
    try:
        return con.execute("""
            SELECT nombre_archivo, fecha_importacion, filas_importadas, stock_actualizado
            FROM importaciones_compras
            ORDER BY fecha_importacion DESC
        """).fetchall()
    finally:
        con.close()


def importar_compras_excel(filas, hash_archivo, nombre_archivo, actualizar_stock=False):
    """Importa el archivo completo o no importa filas; opcionalmente suma al stock."""
    con = conectar()
    try:
        existente = con.execute(
            "SELECT 1 FROM importaciones_compras WHERE hash_archivo = ?",
            (hash_archivo,),
        ).fetchone()
        if existente:
            return False, "Este mismo archivo de compras ya fue importado."

        cantidades = {}
        precios_recientes = {}
        for fila in filas:
            producto_id = fila["producto_id"]
            cantidades[producto_id] = cantidades.get(producto_id, 0) + fila["cantidad"]
            precios_recientes[producto_id] = fila["precio_unitario"]

        grupos = {}
        for fila in filas:
            clave = (
                (fila["fecha"], fila["referencia"])
                if fila["referencia"]
                else (fila["fecha"], f"__fila_{fila['fila_excel']}")
            )
            grupos.setdefault(clave, []).append(fila)

        grupos_lista = list(grupos.items())
        ids_por_grupo = {}
        for inicio in range(0, len(grupos_lista), 250):
            lote = grupos_lista[inicio:inicio + 250]
            valores = [
                (
                    detalles_grupo[0]["fecha"],
                    round(sum(detalle["subtotal"] for detalle in detalles_grupo), 2),
                    referencia or None,
                )
                for (_, referencia), detalles_grupo in lote
            ]
            marcadores = ", ".join("(?, ?, ?)" for _ in valores)
            compras_insertadas = con.execute(
                "INSERT INTO compras (fecha, total, referencia) VALUES "
                f"{marcadores} RETURNING id, fecha, referencia",
                tuple(valor for compra in valores for valor in compra),
            ).fetchall()
            ids_por_clave = {
                (str(fecha), referencia): compra_id
                for compra_id, fecha, referencia in compras_insertadas
            }
            for clave, detalles_grupo in lote:
                fecha, referencia = clave
                compra_id = ids_por_clave[(str(fecha), referencia or None)]
                ids_por_grupo[clave] = compra_id

        detalles = [
            (
                ids_por_grupo[
                    (fila["fecha"], fila["referencia"])
                    if fila["referencia"]
                    else (fila["fecha"], f"__fila_{fila['fila_excel']}")
                ],
                fila["producto_id"],
                fila["cantidad"],
                fila["precio_unitario"],
                fila["subtotal"],
            )
            for fila in filas
        ]
        for inicio in range(0, len(detalles), 150):
            lote = detalles[inicio:inicio + 150]
            marcadores = ", ".join("(?, ?, ?, ?, ?)" for _ in lote)
            con.execute(
                "INSERT INTO detalle_compras "
                "(compra_id, producto_id, cantidad, precio_unitario, subtotal) "
                f"VALUES {marcadores}",
                tuple(valor for detalle in lote for valor in detalle),
            )

        if actualizar_stock:
            for producto_id, cantidad in cantidades.items():
                con.execute(
                    "UPDATE productos SET stock = stock + ?, precio_compra = ? "
                    "WHERE id = ?",
                    (cantidad, precios_recientes[producto_id], producto_id),
                )

        con.execute(
            "INSERT INTO importaciones_compras "
            "(hash_archivo, nombre_archivo, fecha_importacion, filas_importadas, stock_actualizado) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                hash_archivo,
                nombre_archivo,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                len(filas),
                actualizar_stock,
            ),
        )
        con.commit()
        mensaje_stock = (
            " Se sumaron las unidades al stock y se actualizó el último costo."
            if actualizar_stock
            else " El stock actual y los costos de catálogo no se modificaron."
        )
        return True, (
            f"Se importaron {len(filas)} líneas en {len(grupos_lista)} compras."
            f"{mensaje_stock}"
        )
    except Exception as e:
        con.rollback()
        return False, f"No se pudo importar el archivo de compras: {e}"
    finally:
        con.close()


# ==========================================================
# DASHBOARD
# ==========================================================

def resumen_dashboard():
    con = conectar()

    ventas, cantidad_ventas = con.execute("""
        SELECT COALESCE(SUM(total), 0), COUNT(*)
        FROM ventas
    """).fetchone()

    cantidad_lineas_venta = con.execute("""
        SELECT COUNT(*)
        FROM detalle_ventas
    """).fetchone()[0]

    compras = con.execute("""
        SELECT COALESCE(SUM(total), 0)
        FROM compras
    """).fetchone()[0]

    stock_bajo = con.execute("""
        SELECT COUNT(*)
        FROM productos
        WHERE stock <= stock_minimo
    """).fetchone()[0]

    con.close()

    return ventas, cantidad_ventas, cantidad_lineas_venta, compras, stock_bajo


def resumen_operativo():
    ventas, cantidad_ventas, cantidad_lineas_venta, compras, stock_bajo = (
        resumen_dashboard()
    )
    return {
        "ventas": ventas,
        "cantidad_ventas": cantidad_ventas,
        "cantidad_lineas_venta": cantidad_lineas_venta,
        "compras": compras,
        "stock_bajo": stock_bajo,
    }


def obtener_alertas_stock(limit=5):
    con = conectar()
    alertas = con.execute("""
        SELECT codigo, nombre, stock, stock_minimo
        FROM productos
        WHERE stock <= stock_minimo
        ORDER BY stock ASC, nombre ASC
        LIMIT ?
    """, (limit,)).fetchall()
    con.close()
    return alertas


# ==========================================================
# MENÚ
# ==========================================================

with st.sidebar:

    rol_texto = "Administrador" if es_admin else "Empleado"

    # PERFIL / SESIÓN
    st.markdown(
        f"""
        <div class="user-card">
            <div class="user-card-top">
                <span class="user-status-dot"></span>
                <span class="user-status-text">Sesión activa</span>
            </div>
            <div class="user-name">{usuario_actual['nombre']}</div>
            <div class="user-role">{rol_texto}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Cerrar sesión", key="cerrar_sesion"):
        st.session_state.pop("usuario", None)
        st.session_state.pop("menu", None)
        st.rerun()

    st.divider()

    # MENÚ PRINCIPAL
    st.markdown(
        '<div class="sidebar-section-title">Menú principal</div>',
        unsafe_allow_html=True
    )

    opciones_menu = [
        "Inicio",
        "Dashboard gerencial",
        "Productos",
        "Ventas",
        "Compras",
        "Análisis inteligente",
        "Predicción de demanda"
    ]

    if es_admin:
        opciones_menu.append("Administrar usuarios")

    if "menu" not in st.session_state:
        st.session_state.menu = "Inicio"

    iconos_menu = {
        "Inicio": ":material/home:",
        "Dashboard gerencial": ":material/dashboard:",
        "Productos": ":material/inventory_2:",
        "Ventas": ":material/point_of_sale:",
        "Compras": ":material/shopping_cart:",
        "Análisis inteligente": ":material/query_stats:",
        "Predicción de demanda": ":material/trending_up:",
        "Administrar usuarios": ":material/manage_accounts:",
    }

    for indice, opcion in enumerate(opciones_menu):
        clave = "menu_active" if opcion == st.session_state.menu else f"menu_item_{indice}"
        if st.button(opcion, key=clave, icon=iconos_menu[opcion]):
            st.session_state.menu = opcion
            st.rerun()

    menu = st.session_state.menu

    st.divider()

    # ADMINISTRACIÓN
    st.markdown(
        '<div class="sidebar-section-title">Administración</div>',
        unsafe_allow_html=True
    )

    with st.expander("Administración de datos"):
        st.caption(
            "El reinicio elimina productos, compras, ventas y sus historiales. "
            "Esta acción no se puede deshacer."
        )

        confirmacion = st.text_input(
            "Escriba REINICIAR para continuar",
            key="confirmar_reinicio",
            max_chars=9,
        )

        if st.button(
            "Eliminar todo y empezar de cero",
            key="reiniciar_datos",
            type="secondary",
            disabled=confirmacion.strip().upper() != "REINICIAR",
        ):
            try:
                database.reiniciar_datos()
                st.session_state.pop("confirmar_reinicio", None)
                notificar_exito(
                    "Sistema reiniciado correctamente. Ya puedes comenzar un nuevo registro."
                )
                st.rerun()
            except Exception as error:
                st.error(f"No se pudo reiniciar el sistema: {error}")

# ==========================================================
# INICIO
# ==========================================================

if menu == "Inicio":

    operacion = resumen_operativo()
    alertas = obtener_alertas_stock(3)

    st.markdown(
        f"""
        <section class="hb-hero">
            <div class="hb-hero-content">
                <div class="hb-hero-eyebrow">Gestión comercial · Librería Bazar Humbertito</div>
                <h1>Todo tu negocio, en un solo lugar</h1>
                <p>
                    Consulta el rendimiento de tu negocio, controla el inventario
                    y registra tus operaciones desde un solo panel.
                </p>
            </div>
            <div class="hb-hero-date">{datetime.now().strftime("%d/%m/%Y")}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.caption(":material/database: Resumen operativo")

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Ingresos totales", formatear_soles(operacion["ventas"]), border=True)
    with k2:
        st.metric(
            "Boletas / transacciones",
            formatear_numero_es(operacion["cantidad_ventas"]),
            border=True,
        )
    with k3:
        st.metric(
            "Líneas de productos vendidos",
            formatear_numero_es(operacion["cantidad_lineas_venta"]),
            border=True,
        )
    with k4:
        st.metric("Compras registradas", formatear_soles(operacion["compras"]), border=True)
    with k5:
        st.metric(
            "Productos con stock crítico",
            formatear_numero_es(operacion["stock_bajo"]),
            border=True,
        )

    st.caption(
        "Una transacción agrupa una venta o boleta; las líneas cuentan cada "
        "producto registrado dentro de esas ventas. "
        "Por eso pueden ser valores distintos."
    )
    st.caption(
        "El sistema no muestra margen neto: aún no guarda el costo histórico "
        "de cada producto vendido ni los gastos operativos."
    )

    st.subheader("Accesos rápidos", icon=":material/bolt:")
    a1, a2, a3, a4 = st.columns(4)

    with a1:
        st.markdown(
            """
            <div class="quick-card">
                <strong>Registrar producto</strong>
                <p>Agrega artículos nuevos para mantener la información comercial actualizada.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "Ir a productos",
            key="quick_productos",
            icon=":material/inventory_2:",
        ):
            st.session_state.menu = "Productos"
            st.rerun()

    with a2:
        st.markdown(
            """
            <div class="quick-card">
                <strong>Registrar venta</strong>
                <p>Controla las salidas del inventario y actualiza ventas en tiempo real.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "Ir a ventas",
            key="quick_ventas",
            icon=":material/point_of_sale:",
        ):
            st.session_state.menu = "Ventas"
            st.rerun()

    with a3:
        st.markdown(
            """
            <div class="quick-card">
                <strong>Registrar compra</strong>
                <p>Actualiza el stock y el costo de adquisición para cada producto.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "Ir a compras",
            key="quick_compras",
            icon=":material/shopping_cart:",
        ):
            st.session_state.menu = "Compras"
            st.rerun()

    with a4:
        st.markdown(
            """
            <div class="quick-card">
                <strong>Ver análisis</strong>
                <p>Revisa la tendencia, rotación y recomendaciones de reposición.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "Ver dashboard",
            key="quick_dashboard",
            icon=":material/dashboard:",
        ):
            st.session_state.menu = "Dashboard gerencial"
            st.rerun()

    with st.container(border=True):
        st.subheader("Estado del inventario", icon=":material/inventory_2:")

        if alertas:
            alert_column, action_column = st.columns([3, 1], vertical_alignment="center")
            with alert_column:
                st.warning(
                    f"{operacion['stock_bajo']} producto(s) requieren revisión."
                )
            with action_column:
                if st.button(
                    "Revisar inventario",
                    key="quick_stock_review",
                    icon=":material/arrow_forward:",
                    type="primary",
                    width="stretch",
                ):
                    st.session_state.menu = "Productos"
                    st.rerun()

            st.dataframe(
                [
                    {
                        "Código": codigo,
                        "Producto": nombre,
                        "Stock actual": stock,
                        "Stock mínimo": stock_minimo,
                    }
                    for codigo, nombre, stock, stock_minimo in alertas
                ],
                width="stretch",
                hide_index=True,
            )
        else:
            st.success("El inventario está saludable y no requiere reposición urgente.")
            st.caption(
                "Cuando un artículo alcance su nivel mínimo, aparecerá aquí para que puedas actuar a tiempo."
            )
# ==========================================================
# ADMINISTRACIÓN DE USUARIOS
# ==========================================================

elif menu == "Administrar usuarios":

    if not es_admin:
        st.error("No tienes permisos para administrar usuarios.")
        st.stop()

    st.header("Administración de usuarios", icon=":material/manage_accounts:")

    st.subheader("Crear una cuenta")

    with st.form("crear_usuario"):
        nombre = st.text_input("Nombre completo")
        username = st.text_input("Nombre de usuario")

        password = st.text_input(
            "Contraseña",
            type="password"
        )

        confirmar = st.text_input(
            "Confirmar contraseña",
            type="password"
        )

        rol = st.selectbox(
            "Rol del usuario",
            ["empleado", "admin"],
            format_func=lambda x: (
                "Empleado" if x == "empleado"
                else "Administrador"
            )
        )

        guardar = st.form_submit_button(
            "Crear usuario",
            type="primary"
        )

        if guardar:
            if password != confirmar:
                st.error("Las contraseñas no coinciden.")
            else:
                try:
                    auth.crear_usuario(
                        username,
                        nombre,
                        password,
                        rol
                    )
                    notificar_exito(
                        f"Usuario {username} creado correctamente."
                    )
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))

    st.divider()
    st.subheader("Usuarios registrados")

    usuarios = auth.listar_usuarios()

    if usuarios:
        # La tabla estática mantiene visibles los datos sin depender
        # del canvas del dataframe interactivo.
        tabla_usuarios = [
            {
                "ID": str(u[0]),
                "Usuario": u[1],
                "Nombre": u[2],
                "Rol": (
                    "Administrador"
                    if u[3] == "admin"
                    else "Empleado"
                ),
                "Estado": (
                    "Activo" if u[4] else "Inactivo"
                ),
                "Creado": u[5]
            }
            for u in usuarios
        ]

        with st.container(key="registered_users_table"):
            st.table(
                pd.DataFrame(tabla_usuarios).style.hide(axis="index"),
                width="stretch",
            )

        usuarios_eliminables = [
            usuario for usuario in usuarios
            if str(usuario[0]) != str(usuario_actual.get("id"))
        ]

        st.divider()
        transferencia_column, eliminacion_column = st.columns(2, gap="large")

        with transferencia_column:
            with st.container(key="user_transfer_panel"):
                st.subheader(
                    "Transferir administración",
                    icon=":material/swap_horiz:",
                )
                st.caption(
                    "Asigna el control a otra cuenta. Tu cuenta se eliminará "
                    "y se cerrará tu sesión; el historial se conservará."
                )

                if usuarios_eliminables:
                    usuarios_por_id = {
                        usuario[0]: usuario for usuario in usuarios_eliminables
                    }
                    nuevo_admin_id = st.selectbox(
                        "Nuevo administrador",
                        options=list(usuarios_por_id),
                        format_func=lambda user_id: (
                            f"{usuarios_por_id[user_id][2]} "
                            f"(@{usuarios_por_id[user_id][1]})"
                        ),
                        key="nuevo_administrador",
                    )
                    nuevo_admin = usuarios_por_id[nuevo_admin_id]
                    st.markdown(
                        f"**Se transferirá a:** {nuevo_admin[2]} "
                        f"· @{nuevo_admin[1]}"
                    )
                    st.caption(
                        "Recibirá permisos de administrador al confirmar."
                    )

                    confirmar_traspaso_checkbox = st.checkbox(
                        "Confirmo el traspaso y la eliminación de mi cuenta",
                        key="confirmar_traspaso_checkbox",
                    )
                    confirmar_traspaso = st.button(
                        "Transferir y salir",
                        key="ejecutar_traspaso_administracion",
                        icon=":material/swap_horiz:",
                        type="primary",
                        disabled=not confirmar_traspaso_checkbox,
                        width="stretch",
                    )

                    if confirmar_traspaso:
                        try:
                            auth.transferir_administracion_y_eliminar_usuario(
                                usuario_actual.get("id"),
                                nuevo_admin_id,
                            )
                            notificar_exito(
                                f"Administración transferida a @{nuevo_admin[1]}. "
                                "Tu cuenta fue eliminada; inicia sesión con la nueva cuenta."
                            )
                            st.session_state.pop("usuario", None)
                            st.session_state.pop("menu", None)
                            st.session_state.pop(
                                "usuario_pendiente_eliminar_id",
                                None,
                            )
                            st.rerun()
                        except ValueError as error:
                            st.error(str(error))
                else:
                    st.info(
                        "Crea otra cuenta primero. Después podrás transferirle "
                        "la administración y eliminar tu cuenta actual."
                    )

        with eliminacion_column:
            with st.container(key="user_delete_panel"):
                st.subheader(
                    "Eliminar una cuenta",
                    icon=":material/person_remove:",
                )
                st.caption(
                    "La eliminación es permanente. Las ventas y compras "
                    "registradas se conservarán."
                )

                if usuarios_eliminables:
                    for usuario in usuarios_eliminables:
                        usuario_id, username, nombre, rol_usuario = usuario[:4]
                        with st.container(border=True):
                            datos_usuario, accion_usuario = st.columns([3, 1])
                            with datos_usuario:
                                st.write(f"**{nombre}** · @{username}")
                                st.caption(
                                    "Administrador"
                                    if rol_usuario == "admin"
                                    else "Empleado"
                                )
                            with accion_usuario:
                                if st.button(
                                    "Eliminar",
                                    key=f"preparar_eliminar_usuario_{usuario_id}",
                                    icon=":material/delete_outline:",
                                    type="secondary",
                                    width="stretch",
                                ):
                                    st.session_state[
                                        "usuario_pendiente_eliminar_id"
                                    ] = usuario_id
                                    st.rerun()

                    usuario_pendiente_id = st.session_state.get(
                        "usuario_pendiente_eliminar_id"
                    )
                    usuario_pendiente = next(
                        (
                            usuario for usuario in usuarios_eliminables
                            if str(usuario[0]) == str(usuario_pendiente_id)
                        ),
                        None,
                    )

                    if usuario_pendiente_id is not None and usuario_pendiente is None:
                        st.session_state.pop(
                            "usuario_pendiente_eliminar_id", None
                        )
                        st.info("La cuenta seleccionada ya no está disponible.")
                    elif usuario_pendiente is not None:
                        usuario_id, username, nombre = usuario_pendiente[:3]
                        st.warning(
                            f"Vas a eliminar la cuenta de {nombre} (@{username}). "
                            "Esta acción no se puede deshacer."
                        )

                        with st.form(f"confirmar_eliminar_usuario_{usuario_id}"):
                            confirmacion_eliminar = st.text_input(
                                f"Escribe {username} para confirmar",
                                key=f"confirmacion_eliminar_usuario_{usuario_id}",
                            )
                            confirmar_eliminar = st.form_submit_button(
                                "Confirmar eliminación",
                                type="secondary",
                                disabled=confirmacion_eliminar.strip() != username,
                            )

                        cancelar_eliminar = st.button(
                            "Cancelar",
                            key=f"cancelar_eliminar_usuario_{usuario_id}",
                        )

                        if cancelar_eliminar:
                            st.session_state.pop(
                                "usuario_pendiente_eliminar_id", None
                            )
                            st.rerun()

                        if confirmar_eliminar:
                            try:
                                auth.eliminar_usuario(
                                    usuario_id,
                                    usuario_actual.get("id"),
                                )
                                st.session_state.pop(
                                    "usuario_pendiente_eliminar_id", None
                                )
                                notificar_exito(
                                    f"La cuenta @{username} se eliminó correctamente."
                                )
                                st.rerun()
                            except ValueError as error:
                                st.error(str(error))
                else:
                    st.info(
                        "No hay otras cuentas para eliminar. Crea otra cuenta "
                        "arriba para que aparezca aquí. La cuenta que estás "
                        "usando no se puede eliminar."
                    )
    else:
        st.info("Todavía no hay usuarios registrados.")


# ==========================================================
# DASHBOARD
# ==========================================================

elif menu == "Dashboard gerencial":

    st.header("Dashboard gerencial", icon=":material/dashboard:")

    ventas, cantidad_ventas, cantidad_lineas_venta, compras, stock_bajo = (
        resumen_dashboard()
    )

    d1, d2, d3, d4, d5 = st.columns(5)

    with d1:
        st.metric("Ingresos por ventas", formatear_soles(ventas))

    with d2:
        st.metric(
            "Boletas / transacciones",
            formatear_numero_es(cantidad_ventas),
        )

    with d3:
        st.metric(
            "Líneas de productos vendidos",
            formatear_numero_es(cantidad_lineas_venta),
        )

    with d4:
        st.metric("Compras acumuladas", formatear_soles(compras))

    with d5:
        st.metric("Productos con stock bajo", formatear_numero_es(stock_bajo))

    st.caption(
        "Las transacciones agrupan las ventas por boleta cuando el Excel la "
        "incluye. Las líneas cuentan cada producto de esas boletas; no equivalen "
        "a las unidades vendidas."
    )

    st.divider()

    resumen = analysis.resumen_ventas()
    tendencia = analysis.tendencia_ventas()

    s1, s2, s3 = st.columns(3)

    with s1:
        st.metric(
            "Unidades vendidas",
            formatear_numero_es(resumen["unidades_vendidas"])
        )

    with s2:
        st.metric(
            "Días con ventas",
            formatear_numero_es(resumen["dias_con_ventas"])
        )

    with s3:
        st.metric(
            "Promedio diario",
            formatear_soles(resumen["promedio_diario"])
        )

    st.subheader("Evolución de las ventas")

    datos_dia = analysis.obtener_datos_ventas()
    top = pd.DataFrame()
    selector_periodo, detalle_periodo = st.columns([1, 2], vertical_alignment="bottom")
    with selector_periodo:
        periodo_grafico = st.segmented_control(
            "Periodo del gráfico",
            ["30 días", "60 días", "90 días"],
            default="90 días",
            key="dashboard_periodo_ventas",
            width="stretch",
        )
    with detalle_periodo:
        st.caption(
            "El periodo seleccionado se aplica a los dos gráficos. Las tarjetas "
            "del resumen conservan los totales de todo el historial."
        )

    dias_por_periodo = {
        "30 días": 30,
        "60 días": 60,
        "90 días": 90,
    }
    if not datos_dia.empty and periodo_grafico in dias_por_periodo:
        fechas_ventas = pd.to_datetime(datos_dia["fecha"])
        fecha_limite = fechas_ventas.max() - pd.Timedelta(
            days=dias_por_periodo[periodo_grafico] - 1
        )
        datos_dia = datos_dia.loc[fechas_ventas >= fecha_limite].copy()
        top = (
            datos_dia.groupby(
                ["producto_id", "codigo", "nombre", "categoria"],
                as_index=False,
            )["cantidad"]
            .sum()
            .sort_values("cantidad", ascending=False)
            .rename(columns={"cantidad": "unidades_vendidas"})
        )

    panel_ventas, panel_productos = st.columns([1.2, 1], gap="large")

    with panel_ventas:
        with st.container(border=True):
            st.markdown("#### Ventas diarias")
            st.caption("Importe vendido por fecha · soles")

            if not datos_dia.empty:
                diario = (
                    datos_dia.groupby(
                        datos_dia["fecha"].dt.date
                    )["subtotal"]
                    .sum()
                    .rename("Ventas")
                )

                grafico_ventas_diarias = go.Figure(
                    go.Scatter(
                        x=pd.to_datetime(diario.index),
                        y=diario.values,
                        mode="lines+markers",
                        line={"color": "#2a9d8f", "width": 2.5},
                        marker={
                            "size": 5,
                            "color": "#2a9d8f",
                            "line": {"width": 1, "color": "#101820"},
                        },
                        fill="tozeroy",
                        fillcolor="rgba(42, 157, 143, 0.10)",
                        hovertemplate="%{x|%d/%m/%Y}<br>Ventas: S/ %{y:,.2f}<extra></extra>",
                    )
                )
                grafico_ventas_diarias.update_layout(
                    height=430,
                    margin={"l": 8, "r": 12, "t": 12, "b": 12},
                    showlegend=False,
                    hovermode="x unified",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis={
                        "title": None,
                        "tickformat": "%d/%m",
                        "nticks": 8,
                        "fixedrange": True,
                        "showgrid": False,
                        "automargin": True,
                    },
                    yaxis={
                        "title": None,
                        "tickprefix": "S/ ",
                        "tickformat": ",.0f",
                        "fixedrange": True,
                        "rangemode": "tozero",
                        "gridcolor": "rgba(145, 160, 174, 0.16)",
                        "zeroline": False,
                    },
                    separators=",.",
                    uirevision="dashboard-ventas",
                )
                mostrar_grafico_fijo(
                    grafico_ventas_diarias,
                    "grafico_ventas_diarias",
                )
            else:
                st.info("Aún no hay ventas para mostrar en este periodo.")

    with panel_productos:
        with st.container(border=True):
            st.markdown("#### Productos más vendidos")
            if not top.empty:
                top_12 = top.head(12).iloc[::-1]
                st.caption(f"Top {len(top_12)} · {periodo_grafico.lower()}")
                max_unidades = max(float(top_12["unidades_vendidas"].max()), 1)

                grafico_productos_mas_vendidos = go.Figure(
                    go.Bar(
                        x=top_12["unidades_vendidas"],
                        y=top_12["nombre"],
                        orientation="h",
                        marker={
                            "color": "#2a9d8f",
                            "line": {"width": 0},
                        },
                        text=top_12["unidades_vendidas"],
                        textposition="outside",
                        cliponaxis=False,
                        hovertemplate="%{y}<br>Unidades: %{x}<extra></extra>",
                    )
                )
                grafico_productos_mas_vendidos.update_layout(
                    height=430,
                    margin={"l": 8, "r": 34, "t": 12, "b": 12},
                    showlegend=False,
                    hovermode="closest",
                    bargap=0.32,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis={
                        "title": None,
                        "range": [0, max_unidades * 1.18],
                        "fixedrange": True,
                        "showgrid": True,
                        "gridcolor": "rgba(145, 160, 174, 0.16)",
                        "zeroline": False,
                    },
                    yaxis={
                        "title": None,
                        "fixedrange": True,
                        "automargin": True,
                    },
                    separators=",.",
                    uirevision="dashboard-productos",
                )
                mostrar_grafico_fijo(
                    grafico_productos_mas_vendidos,
                    "grafico_productos_mas_vendidos",
                )
            else:
                st.info("Aún no hay productos vendidos para comparar.")


# ==========================================================
# PRODUCTOS
# ==========================================================

elif menu == "Productos":

    st.header("Gestión de productos", icon=":material/inventory_2:")

    tab1, tab2 = st.tabs([
        "Registrar producto",
        "Productos registrados"
    ])

    with tab1:

        with st.form("form_producto"):

            c1, c2 = st.columns(2)

            with c1:
                codigo = st.text_input("Código del producto")
                nombre = st.text_input("Nombre del producto")
                categoria = st.text_input("Categoría")
                precio_compra = st.number_input(
                    "Precio de compra",
                    min_value=0.0,
                    step=0.10,
                    format="%.2f"
                )

            with c2:
                precio_venta = st.number_input(
                    "Precio de venta",
                    min_value=0.0,
                    step=0.10,
                    format="%.2f"
                )
                stock = st.number_input(
                    "Stock inicial",
                    min_value=0,
                    step=1
                )
                stock_minimo = st.number_input(
                    "Stock mínimo",
                    min_value=0,
                    step=1,
                    value=5
                )

            guardar = st.form_submit_button(
                "Registrar producto"
            )

            if guardar:

                if not codigo.strip():
                    st.error("Ingrese el código.")

                elif not nombre.strip():
                    st.error("Ingrese el nombre.")

                elif precio_venta <= 0:
                    st.error("El precio de venta debe ser mayor que 0.")

                else:

                    ok, mensaje = registrar_producto(
                        codigo.strip(),
                        nombre.strip(),
                        categoria.strip(),
                        precio_compra,
                        precio_venta,
                        stock,
                        stock_minimo
                    )

                    if ok:
                        notificar_exito(mensaje)
                        st.rerun()
                    else:
                        st.error(mensaje)

    with tab2:

        st.subheader("Cargar productos desde Excel")
        col_plantilla, col_archivo = st.columns([1, 2])
        with col_plantilla:
            st.download_button(
                "Descargar plantilla de productos",
                data=crear_plantilla_productos_excel(),
                file_name="plantilla_productos_humbertito.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                key="descargar_plantilla_productos_excel",
            )
        with col_archivo:
            version_carga_productos = st.session_state.setdefault(
                "version_carga_productos_excel", 0
            )
            archivo_productos_excel = st.file_uploader(
                "Seleccionar archivo Excel de productos (.xlsx)",
                type=["xlsx"],
                key=f"carga_productos_excel_{version_carga_productos}",
            )

        if archivo_productos_excel is not None:
            contenido_productos_excel = archivo_productos_excel.getvalue()
            hash_productos_excel = hashlib.sha256(
                contenido_productos_excel
            ).hexdigest()[:12]
            filas_productos_excel, errores_productos_excel = (
                validar_productos_excel(contenido_productos_excel)
            )

            if filas_productos_excel:
                vista_productos_excel = pd.DataFrame([
                    {
                        "ID": (
                            fila["id"] if fila["id"] is not None else "Automático"
                        ),
                        "Código": fila["codigo"],
                        "Producto": fila["nombre"],
                        "Categoría": fila["categoria"],
                        "Precio compra": f"S/ {fila['precio_compra']:.2f}",
                        "Precio venta": f"S/ {fila['precio_venta']:.2f}",
                        "Stock": fila["stock"],
                        "Stock mínimo": fila["stock_minimo"],
                    }
                    for fila in filas_productos_excel
                ])
                st.dataframe(
                    vista_productos_excel,
                    width="stretch",
                    hide_index=True,
                    height=420,
                    key=f"vista_productos_excel_{hash_productos_excel}",
                    column_config={
                        "ID": st.column_config.TextColumn("ID", width=85),
                        "Código": st.column_config.TextColumn(
                            "Código", width=125
                        ),
                        "Producto": st.column_config.TextColumn(
                            "Producto", width=220
                        ),
                        "Categoría": st.column_config.TextColumn(
                            "Categoría", width=170
                        ),
                        "Precio compra": st.column_config.TextColumn(
                            "Precio compra", width=130
                        ),
                        "Precio venta": st.column_config.TextColumn(
                            "Precio venta", width=130
                        ),
                        "Stock": st.column_config.NumberColumn(
                            "Stock", width=80
                        ),
                        "Stock mínimo": st.column_config.NumberColumn(
                            "Stock mínimo", width=100
                        ),
                    },
                )
                st.caption(
                    f"Productos válidos: {len(filas_productos_excel)}. "
                    "La importación se realizará completa, sin omitir filas."
                )

            if errores_productos_excel:
                st.error(
                    f"Se encontraron {len(errores_productos_excel)} errores. "
                    "Corrige el archivo; no se importará parcialmente."
                )
                for error_producto_excel in errores_productos_excel[:20]:
                    st.write(f"• {error_producto_excel}")
                if len(errores_productos_excel) > 20:
                    st.caption("Se muestran los primeros 20 errores.")

            if filas_productos_excel and not errores_productos_excel:
                if st.button(
                    "Importar productos validados",
                    key="confirmar_importacion_productos_excel",
                    type="primary",
                ):
                    ok, mensaje = importar_productos_excel(
                        filas_productos_excel
                    )
                    if ok:
                        st.session_state[
                            "version_carga_productos_excel"
                        ] += 1
                        notificar_exito(mensaje)
                        st.rerun()
                    else:
                        st.error(mensaje)

        st.divider()

        productos = obtener_productos()

        if productos:

            tabla = []

            productos_por_id = {p[0]: p for p in productos}

            for p in productos:
                tabla.append({
                    "ID": p[0],
                    "Código": p[1],
                    "Producto": p[2],
                    "Categoría": p[3],
                    "Precio compra": p[4],
                    "Precio venta": p[5],
                    "Stock": p[6],
                    "Stock mínimo": p[7]
                })

            st.dataframe(
                tabla,
                width="stretch",
                hide_index=True,
                height=420,
                key="productos_registrados_orden_id_asc",
            )

            st.download_button(
                "Descargar productos en Excel",
                data=generar_excel_productos(productos),
                file_name=(
                    f"productos_humbertito_{datetime.now():%Y%m%d_%H%M}.xlsx"
                ),
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                key="descargar_productos_excel",
            )

            st.divider()
            st.subheader("Editar o eliminar un producto")
            producto_id = st.selectbox(
                "Selecciona el producto",
                options=list(productos_por_id),
                format_func=lambda identificador: (
                    f"{productos_por_id[identificador][1]} — "
                    f"{productos_por_id[identificador][2]}"
                ),
                key="producto_seleccionado_edicion",
            )
            producto = productos_por_id[producto_id]

            with st.expander("Editar datos del producto"):
                with st.form(f"form_editar_producto_{producto_id}"):
                    edit_c1, edit_c2 = st.columns(2)

                    with edit_c1:
                        nuevo_codigo = st.text_input(
                            "Código del producto",
                            value=producto[1],
                        )
                        nuevo_nombre = st.text_input(
                            "Nombre del producto",
                            value=producto[2],
                        )
                        nueva_categoria = st.text_input(
                            "Categoría",
                            value=producto[3] or "",
                        )
                        nuevo_precio_compra = st.number_input(
                            "Precio de compra",
                            min_value=0.0,
                            step=0.10,
                            format="%.2f",
                            value=float(producto[4] or 0),
                        )

                    with edit_c2:
                        nuevo_precio_venta = st.number_input(
                            "Precio de venta",
                            min_value=0.0,
                            step=0.10,
                            format="%.2f",
                            value=float(producto[5] or 0),
                        )
                        nuevo_stock = st.number_input(
                            "Stock",
                            min_value=0,
                            step=1,
                            value=int(producto[6] or 0),
                        )
                        nuevo_stock_minimo = st.number_input(
                            "Stock mínimo",
                            min_value=0,
                            step=1,
                            value=int(producto[7] or 0),
                        )

                    guardar_cambios = st.form_submit_button(
                        "Guardar cambios",
                        type="primary",
                    )

                    if guardar_cambios:
                        if not nuevo_codigo.strip():
                            st.error("Ingrese el código del producto.")
                        elif not nuevo_nombre.strip():
                            st.error("Ingrese el nombre del producto.")
                        elif nuevo_precio_venta <= 0:
                            st.error("El precio de venta debe ser mayor que 0.")
                        else:
                            ok, mensaje = actualizar_producto(
                                producto_id,
                                nuevo_codigo.strip(),
                                nuevo_nombre.strip(),
                                nueva_categoria.strip(),
                                nuevo_precio_compra,
                                nuevo_precio_venta,
                                nuevo_stock,
                                nuevo_stock_minimo,
                            )

                            if ok:
                                notificar_exito(mensaje)
                                st.rerun()
                            else:
                                st.error(mensaje)

            with st.expander("Eliminar producto"):
                st.warning(
                    "La eliminación es permanente. Si el producto ya tiene "
                    "ventas o compras registradas, se conservará para no "
                    "alterar ese historial."
                )

                with st.form(f"form_eliminar_producto_{producto_id}"):
                    confirmar_eliminacion = st.checkbox(
                        f"Confirmo que deseo eliminar “{producto[2]}”."
                    )
                    eliminar = st.form_submit_button(
                        "Eliminar producto",
                        type="secondary",
                    )

                    if eliminar:
                        if not confirmar_eliminacion:
                            st.error("Marca la confirmación para continuar.")
                        else:
                            ok, mensaje = eliminar_producto(producto_id)

                            if ok:
                                notificar_exito(mensaje)
                                st.session_state.pop(
                                    "producto_seleccionado_edicion",
                                    None,
                                )
                                st.rerun()
                            else:
                                st.error(mensaje)

            with st.expander("Eliminar todos los productos"):
                st.warning(
                    "Esto elimina el catálogo completo. Si existen ventas o "
                    "compras asociadas, el sistema conservará los productos para "
                    "proteger ese historial."
                )
                with st.form("form_eliminar_todos_productos"):
                    confirmar_eliminacion_total = st.checkbox(
                        "Confirmo que deseo eliminar todos los productos registrados."
                    )
                    eliminar_todos = st.form_submit_button(
                        "Eliminar todos los productos",
                        type="secondary",
                    )

                    if eliminar_todos:
                        if not confirmar_eliminacion_total:
                            st.error(
                                "Marca la confirmación para eliminar el catálogo."
                            )
                        else:
                            ok, mensaje = eliminar_todos_productos()
                            if ok:
                                notificar_exito(mensaje)
                                st.session_state.pop(
                                    "producto_seleccionado_edicion",
                                    None,
                                )
                                st.rerun()
                            else:
                                st.error(mensaje)

        else:

            st.info("Todavía no hay productos registrados.")


# ==========================================================
# VENTAS
# ==========================================================

elif menu == "Ventas":

    st.header("Gestión de ventas", icon=":material/point_of_sale:")

    productos = obtener_productos()

    if not productos:

        st.warning("Primero registre un producto.")

    else:

        opciones = [
            f"{p[1]} - {p[2]} | Stock: {p[6]} | S/ {p[5]:.2f}"
            for p in productos
        ]

        with st.form("form_venta"):

            indice = st.selectbox(
                "Seleccionar producto",
                range(len(opciones)),
                format_func=lambda i: opciones[i]
            )

            cantidad = st.number_input(
                "Cantidad",
                min_value=1,
                step=1,
                value=1
            )

            precio_unitario = st.number_input(
                "Precio unitario de la boleta (S/)",
                min_value=0.01,
                value=float(productos[indice][5]),
                step=0.10,
                help="Si el precio de la boleta antigua difiere del actual, ingresa el que figura en ella."
            )

            fecha_venta = st.date_input(
                "Fecha de la boleta",
                value=datetime.now().date(),
                max_value=datetime.now().date(),
                help="Para boletas antiguas, selecciona la fecha impresa en el documento."
            )

            descontar_stock_historico = st.checkbox(
                "También descontar esta venta histórica del stock actual",
                value=False,
                key="stock_historico_checkbox",
                help=(
                    "Déjalo desmarcado si el stock actual ya refleja las ventas que "
                    "ocurrieron. Márcalo solo si todavía necesitas descontar esta cantidad."
                )
            )

            vender = st.form_submit_button(
                "Registrar venta"
            )

            if vender:

                ok, mensaje = registrar_venta(
                    productos[indice][0],
                    cantidad,
                    fecha_venta,
                    precio_unitario,
                    descontar_stock=(
                        fecha_venta == datetime.now().date()
                        or descontar_stock_historico
                    )
                )

                if ok:
                    notificar_exito(mensaje)
                    st.rerun()
                else:
                    st.error(mensaje)

        st.divider()
        st.subheader("Importar ventas desde Excel")
        st.caption(
            "Carga las ventas de tus boletas en bloque. Puedes usar la plantilla "
            "o un archivo con columnas equivalentes."
        )
        st.download_button(
            "Descargar plantilla de ventas",
            data=crear_plantilla_ventas_excel(),
            file_name="plantilla_ventas_humbertito.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="descargar_plantilla_ventas",
        )

        archivo_ventas_excel = st.file_uploader(
            "Seleccionar archivo Excel de ventas (.xlsx)",
            type=["xlsx"],
            key="carga_masiva_ventas_excel",
            help=(
                "Cada fila representa un producto vendido. Comparte el mismo "
                "N° Boleta entre filas para agruparlas en una venta."
            ),
        )

        if archivo_ventas_excel is not None:
            contenido_excel = archivo_ventas_excel.getvalue()
            hash_archivo_excel = hashlib.sha256(contenido_excel).hexdigest()
            importacion_existente = hash_importacion_registrada(hash_archivo_excel)
            filas_excel, errores_excel, _ = validar_ventas_excel(contenido_excel)

            if importacion_existente:
                st.warning(
                    "Este archivo ya fue importado el "
                    f"{importacion_existente[1]} como "
                    f"{importacion_existente[0]}. No se volverá a registrar."
                )

            if filas_excel:
                vista_previa = pd.DataFrame([
                    {
                        "Fila Excel": fila["fila_excel"],
                        "Fecha": fila["fecha"].split()[0],
                        "Código": fila["codigo"],
                        "Producto": fila["producto"],
                        "Cantidad": fila["cantidad"],
                        "Precio unitario": f"S/ {fila['precio_unitario']:.2f}",
                        "Boleta": fila["referencia"],
                    }
                    for fila in filas_excel
                ])
                st.dataframe(
                    vista_previa,
                    width="stretch",
                    hide_index=True,
                    height=520,
                    key=f"previsualizacion_ventas_{hash_archivo_excel[:12]}",
                    column_config={
                        "Fila Excel": st.column_config.NumberColumn(
                            "Fila Excel", width=85
                        ),
                        "Fecha": st.column_config.TextColumn(
                            "Fecha", width=125
                        ),
                        "Código": st.column_config.TextColumn(
                            "Código", width=135
                        ),
                        "Producto": st.column_config.TextColumn(
                            "Producto", width=250
                        ),
                        "Cantidad": st.column_config.NumberColumn(
                            "Cantidad", width=85
                        ),
                        "Precio unitario": st.column_config.TextColumn(
                            "Precio unitario", width=125
                        ),
                        "Boleta": st.column_config.TextColumn(
                            "Boleta", width=230
                        ),
                    },
                )
                st.caption(
                    f"Filas válidas: {len(filas_excel)} · "
                    f"Importe total: S/ {sum(fila['subtotal'] for fila in filas_excel):.2f}"
                )
                st.caption(
                    "La vista previa incluye todas las filas válidas. "
                    "Desplázate hacia abajo dentro del recuadro para revisarlas."
                )

            if errores_excel:
                st.error(
                    f"Se encontraron {len(errores_excel)} errores. Corrige el Excel "
                    "para importar el archivo completo."
                )
                for error_excel in errores_excel[:20]:
                    st.write(f"• {error_excel}")
                if len(errores_excel) > 20:
                    st.caption("Se muestran solo los primeros 20 errores.")

            descontar_stock_importacion = st.checkbox(
                "Descontar estas unidades del stock actual al importar",
                value=False,
                key="importar_ventas_descontar_stock",
                help=(
                    "Marca esta opción solo si estas ventas todavía deben restarse "
                    "del inventario actual. Si el stock no alcanza, las ventas se "
                    "registrarán igualmente y no se modificará ningún stock."
                ),
            )

            if not errores_excel and filas_excel and not importacion_existente:
                if st.button(
                    "Importar ventas validadas",
                    key="confirmar_importacion_ventas_excel",
                    type="primary",
                ):
                    ok, mensaje = importar_ventas_excel(
                        filas_excel,
                        hash_archivo_excel,
                        archivo_ventas_excel.name,
                        descontar_stock_importacion,
                    )
                    if ok:
                        notificar_exito(mensaje)
                        st.rerun()
                    else:
                        st.error(mensaje)

        st.subheader("Historial de ventas")

        ventas = obtener_ventas()

        if ventas:

            tabla = []

            for numero_fila, venta in enumerate(ventas, start=1):
                tabla.append({
                    "N.º": numero_fila,
                    "Boleta": venta[8] or "",
                    "Fecha": venta[1],
                    "Total": f"S/ {venta[2]:.2f}",
                    "Producto": venta[3],
                    "Cantidad": venta[4],
                    "Precio unitario": f"S/ {venta[5]:.2f}",
                    "Subtotal": f"S/ {venta[6]:.2f}"
                })

            st.caption(
                "Numeración consecutiva desde 1, en el orden del historial. "
                "Desliza hacia abajo dentro del recuadro para ver las demás filas."
            )
            st.dataframe(
                tabla,
                width="stretch",
                hide_index=True,
                height=600,
                key="historial_ventas_id_asc",
                column_config={
                    "N.º": st.column_config.NumberColumn(
                        "N.º", width=65
                    ),
                    "Boleta": st.column_config.TextColumn(
                        "Boleta", width=205
                    ),
                    "Fecha": st.column_config.TextColumn(
                        "Fecha", width=145
                    ),
                    "Total": st.column_config.TextColumn(
                        "Total", width=85
                    ),
                    "Producto": st.column_config.TextColumn(
                        "Producto", width=230
                    ),
                    "Cantidad": st.column_config.NumberColumn(
                        "Cantidad", width=85
                    ),
                    "Precio unitario": st.column_config.TextColumn(
                        "Precio unitario", width=120
                    ),
                    "Subtotal": st.column_config.TextColumn(
                        "Subtotal", width=90
                    ),
                },
            )

            with st.expander("Eliminar una venta registrada por error"):
                ventas_por_id = {venta[0]: venta for venta in ventas}
                venta_id_seleccionada = st.selectbox(
                    "Selecciona la venta",
                    options=list(ventas_por_id),
                    format_func=lambda venta_id: (
                        f"Venta {venta_id} · {ventas_por_id[venta_id][1]} · "
                        f"{ventas_por_id[venta_id][3]} · "
                        f"{ventas_por_id[venta_id][4]} u. · "
                        f"S/ {ventas_por_id[venta_id][2]:.2f}"
                        + (
                            f" · Boleta {ventas_por_id[venta_id][8]}"
                            if ventas_por_id[venta_id][8]
                            else ""
                        )
                    ),
                    key="venta_a_eliminar",
                )
                venta_seleccionada = ventas_por_id[venta_id_seleccionada]

                restaurar_stock_venta_antigua = False
                if venta_seleccionada[7] is None:
                    st.info(
                        "Esta venta es anterior al control de stock por venta. "
                        "No se puede saber si descontó inventario."
                    )
                    restaurar_stock_venta_antigua = st.checkbox(
                        "Restaurar al stock las unidades de esta venta",
                        value=False,
                        key=f"restaurar_stock_venta_antigua_{venta_id_seleccionada}",
                        help=(
                            "Márcalo solo si el stock actual ya incluye el descuento "
                            "de esta venta."
                        ),
                    )
                elif venta_seleccionada[7] == 1:
                    st.caption("Al eliminarla, se devolverán sus unidades al stock.")
                else:
                    st.caption("Esta venta no modificó el stock al registrarse.")

                confirmar_eliminacion = st.checkbox(
                    f"Confirmo que deseo eliminar la venta {venta_id_seleccionada}",
                    value=False,
                    key=f"confirmar_eliminar_venta_{venta_id_seleccionada}",
                )

                if st.button(
                    "Eliminar venta seleccionada",
                    key=f"eliminar_venta_{venta_id_seleccionada}",
                    type="secondary",
                ):
                    if not confirmar_eliminacion:
                        st.warning("Marca la confirmación antes de eliminar la venta.")
                    else:
                        ok, mensaje = eliminar_venta(
                            venta_id_seleccionada,
                            restaurar_stock_venta_antigua,
                        )
                        if ok:
                            notificar_exito(mensaje)
                            st.rerun()
                        else:
                            st.error(mensaje)

            cantidad_ventas_total = len({venta[0] for venta in ventas})
            estados_stock_ventas = {venta[0]: venta[7] for venta in ventas}
            ventas_stock_desconocido = sum(
                estado is None for estado in estados_stock_ventas.values()
            )

            with st.expander("Eliminar todas las ventas"):
                st.warning(
                    f"Se eliminarán permanentemente las {cantidad_ventas_total} "
                    "ventas y sus detalles. Se restaurará el stock solo de las "
                    "ventas que el sistema marcó como descontadas."
                )
                if ventas_stock_desconocido:
                    st.info(
                        f"{ventas_stock_desconocido} ventas antiguas no tienen "
                        "registro de si descontaron stock; su eliminación no cambiará "
                        "el inventario."
                    )
                st.caption(
                    "También se borrará el registro de archivos importados para "
                    "que puedas importarlos nuevamente."
                )
                confirmar_eliminar_todas = st.checkbox(
                    f"Confirmo que deseo eliminar todas las "
                    f"{cantidad_ventas_total} ventas",
                    key=f"confirmar_eliminar_todas_ventas_{cantidad_ventas_total}",
                )
                if st.button(
                    "Eliminar todas las ventas",
                    key="eliminar_todas_ventas",
                    type="secondary",
                ):
                    if not confirmar_eliminar_todas:
                        st.warning(
                            "Marca la confirmación antes de eliminar todas las ventas."
                        )
                    else:
                        ok, mensaje = eliminar_todas_ventas()
                        if ok:
                            notificar_exito(mensaje)
                            st.rerun()
                        else:
                            st.error(mensaje)

        else:

            st.info("Todavía no hay ventas registradas.")


# ==========================================================
# COMPRAS
# ==========================================================

elif menu == "Compras":

    st.header("Gestión de compras", icon=":material/shopping_cart:")

    productos = obtener_productos()

    if not productos:

        st.warning("Primero registre un producto.")

    else:

        opciones = [
            f"{p[1]} - {p[2]} | Stock actual: {p[6]}"
            for p in productos
        ]

        with st.form("form_compra"):

            indice = st.selectbox(
                "Seleccionar producto",
                range(len(opciones)),
                format_func=lambda i: opciones[i]
            )

            cantidad = st.number_input(
                "Cantidad comprada",
                min_value=1,
                step=1,
                value=1
            )

            precio_compra = st.number_input(
                "Precio de compra por unidad",
                min_value=0.01,
                step=0.10,
                format="%.2f"
            )

            comprar = st.form_submit_button(
                "Registrar compra"
            )

            if comprar:

                ok, mensaje = registrar_compra(
                    productos[indice][0],
                    cantidad,
                    precio_compra
                )

                if ok:
                    notificar_exito(mensaje)
                    st.rerun()
                else:
                    st.error(mensaje)

        st.divider()
        st.subheader("Importar compras desde Excel")
        st.caption(
            "La plantilla trae una hoja vacía para tus datos y otra con filas "
            "ficticias marcadas como DEMO. Reemplaza el ejemplo por los datos "
            "de tus comprobantes reales antes de importarlo."
        )
        st.download_button(
            "Descargar plantilla de compras",
            data=crear_plantilla_compras_excel(),
            file_name="plantilla_compras_humbertito.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="descargar_plantilla_compras",
        )

        archivo_compras_excel = st.file_uploader(
            "Seleccionar archivo Excel de compras (.xlsx)",
            type=["xlsx"],
            key="carga_masiva_compras_excel",
            help=(
                "Cada fila representa una línea de compra. El sistema guarda "
                "la fecha, producto, cantidad y costo unitario del archivo."
            ),
        )

        if archivo_compras_excel is not None:
            contenido_compras = archivo_compras_excel.getvalue()
            hash_archivo_compras = hashlib.sha256(contenido_compras).hexdigest()
            importacion_existente = hash_importacion_compras_registrada(
                hash_archivo_compras
            )

            if isinstance(importacion_existente, dict) and "error" in importacion_existente:
                st.error(
                    "La importación de compras todavía no está habilitada en la "
                    "base de datos. Ejecuta una vez "
                    "migracion_importar_compras.sql en Supabase SQL Editor."
                )
            elif importacion_existente:
                st.warning(
                    "Este mismo archivo ya se importó el "
                    f"{importacion_existente[1]}. No se volverá a cargar para "
                    "evitar duplicar compras y stock."
                )
            else:
                filas_compras, errores_compras, _ = validar_compras_excel(
                    contenido_compras
                )
                if errores_compras:
                    st.error(
                        f"Se encontraron {len(errores_compras)} errores. "
                        "Corrige el Excel para importar el archivo completo."
                    )
                    for error_excel in errores_compras[:20]:
                        st.write(f"• {error_excel}")
                    if len(errores_compras) > 20:
                        st.caption("Se muestran solo los primeros 20 errores.")

                if filas_compras:
                    tabla_compras_excel = [
                        {
                            "Fila Excel": fila["fila_excel"],
                            "Fecha": fila["fecha"][:10],
                            "Código": fila["codigo"],
                            "Producto": fila["producto"],
                            "Comprobante": fila["referencia"],
                            "Cantidad": fila["cantidad"],
                            "Precio compra unitario": f"S/ {fila['precio_unitario']:.2f}",
                            "Subtotal": f"S/ {fila['subtotal']:.2f}",
                        }
                        for fila in filas_compras
                    ]
                    st.dataframe(
                        tabla_compras_excel,
                        width="stretch",
                        hide_index=True,
                        height=min(420, 40 + 35 * min(len(filas_compras), 10)),
                    )
                    total_compras_excel = sum(
                        fila["subtotal"] for fila in filas_compras
                    )
                    st.caption(
                        f"Filas válidas: {len(filas_compras)} · "
                        f"Total de compras: S/ {total_compras_excel:.2f}"
                    )

                    actualizar_stock_compras = st.checkbox(
                        "Sumar estas unidades al stock actual",
                        value=False,
                        key="importar_compras_actualizar_stock",
                        help=(
                            "Déjalo desmarcado al importar compras históricas si el "
                            "stock actual ya refleja esos ingresos. Márcalo solo si "
                            "esas unidades todavía no están incluidas en el stock."
                        ),
                    )
                    if not actualizar_stock_compras:
                        st.caption(
                            "El archivo se guardará como historial sin cambiar el "
                            "stock ni el costo actual del catálogo."
                        )

                    if not errores_compras and st.button(
                        "Importar compras validadas",
                        key="confirmar_importacion_compras_excel",
                        type="primary",
                    ):
                        ok, mensaje = importar_compras_excel(
                            filas_compras,
                            hash_archivo_compras,
                            archivo_compras_excel.name,
                            actualizar_stock_compras,
                        )
                        if ok:
                            notificar_exito(mensaje)
                            st.rerun()
                        else:
                            st.error(mensaje)

        st.subheader("Historial de compras")

        try:
            auditoria = obtener_auditoria_compras()
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Comprobantes", auditoria["compras"])
            m2.metric("Total registrado", f"S/ {auditoria['total_encabezados']:.2f}")
            m3.metric("Líneas de compra", auditoria["lineas"])
            m4.metric("Total en detalle", f"S/ {auditoria['total_detalles']:.2f}")
            st.caption(
                "Fechas registradas: "
                f"{auditoria['primera_fecha'] or '—'} a {auditoria['ultima_fecha'] or '—'}. "
                "La conciliación verifica que los encabezados coincidan con sus líneas; "
                "no confirma por sí sola que importes y fechas coincidan con los comprobantes."
            )
            if auditoria["diferencias"]:
                st.error(
                    f"Hay {auditoria['diferencias']} comprobantes cuyo total no coincide "
                    "con sus líneas o que no tienen detalle. Revisa el historial antes "
                    "de usarlo en el informe."
                )
            elif auditoria["compras"]:
                st.success("Los totales registrados coinciden con las líneas de compra.")
            if auditoria["sin_detalles"]:
                st.error(
                    f"Hay {auditoria['sin_detalles']} compras sin líneas de detalle."
                )
        except Exception as error:
            st.warning(
                f"No se pudo mostrar la auditoría de compras. Detalle: {error}"
            )

        compras = obtener_compras()

        if compras:

            tabla = []

            for compra in compras:
                tabla.append({
                    "Compra": compra[0],
                    "Fecha": compra[1],
                    "Total": f"S/ {compra[2]:.2f}",
                    "Comprobante": compra[3] or "",
                    "Producto": compra[4],
                    "Cantidad": compra[5],
                    "Precio unitario": f"S/ {compra[6]:.2f}",
                    "Subtotal": f"S/ {compra[7]:.2f}"
                })

            st.dataframe(
                tabla,
                width="stretch",
                hide_index=True,
                height=420,
            )

            salida_compras = io.BytesIO()
            with pd.ExcelWriter(salida_compras, engine="openpyxl") as escritor:
                pd.DataFrame(tabla).to_excel(
                    escritor, index=False, sheet_name="Historial de compras"
                )
            st.download_button(
                "Descargar historial de compras en Excel",
                data=salida_compras.getvalue(),
                file_name="historial_compras_humbertito.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="descargar_historial_compras",
            )

        else:

            st.info("Todavía no hay compras registradas.")

        try:
            historial_importaciones = obtener_historial_importaciones_compras()
            if historial_importaciones:
                with st.expander("Auditoría de archivos importados"):
                    filas_importaciones = []
                    for nombre, fecha, filas, stock_actualizado in historial_importaciones:
                        if stock_actualizado is None:
                            estado_stock = "No registrado en esa versión"
                        else:
                            estado_stock = "Sí" if stock_actualizado else "No"
                        filas_importaciones.append({
                            "Archivo": nombre,
                            "Fecha de importación": fecha,
                            "Filas": filas,
                            "Sumó al stock": estado_stock,
                        })
                    st.dataframe(
                        filas_importaciones,
                        width="stretch",
                        hide_index=True,
                    )
        except Exception as error:
            st.caption(
                f"No se pudo cargar el historial de archivos importados. Detalle: {error}"
            )


# ==========================================================
# ANÁLISIS INTELIGENTE
# ==========================================================

elif menu == "Análisis inteligente":

    st.header("Análisis inteligente", icon=":material/query_stats:")

    resumen = analysis.resumen_ventas()
    tendencia = analysis.tendencia_ventas()

    st.subheader("Resumen comercial")

    a1, a2, a3, a4 = st.columns(4)

    with a1:
        st.metric(
            "Ventas",
            formatear_soles(resumen["total_ventas"])
        )

    with a2:
        st.metric(
            "Unidades vendidas",
            formatear_numero_es(resumen["unidades_vendidas"])
        )

    with a3:
        st.metric(
            "Días con ventas",
            formatear_numero_es(resumen["dias_con_ventas"])
        )

    with a4:
        st.metric(
            "Promedio diario",
            formatear_soles(resumen["promedio_diario"])
        )

    st.caption(
        "Las unidades suman las cantidades vendidas; pueden ser más que las "
        "líneas de productos registradas. El promedio diario se calcula sobre "
        "los días que sí tuvieron ventas."
    )

    st.divider()

    st.subheader("Tendencia de ventas")

    st.info(
        f"Tendencia identificada: {tendencia['tipo']}"
    )

    st.subheader("Productos más vendidos")

    top = analysis.productos_mas_vendidos()

    if not top.empty:
        st.dataframe(top, width="stretch", hide_index=True, height=360)

    else:

        st.info(
            "Todavía no existen ventas suficientes para realizar este análisis."
        )

    st.subheader("Productos con stock bajo")

    bajo = analysis.productos_stock_bajo()

    if not bajo.empty:
        st.dataframe(bajo, width="stretch", hide_index=True, height=360)

    else:

        st.success(
            "No existen productos con stock bajo."
        )

    st.subheader("Clasificación del comportamiento de productos")

    comportamiento = analysis.analisis_productos()

    if not comportamiento.empty:
        st.dataframe(
            comportamiento[
                [
                    "codigo",
                    "nombre",
                    "categoria",
                    "stock",
                    "stock_minimo",
                    "unidades_vendidas",
                    "analisis"
                ]
            ],
            width="stretch",
            hide_index=True,
            height=420,
        )

    else:

        st.info(
            "No existen productos para analizar."
        )

# ==========================================================
# PREDICCIÓN DE DEMANDA
# ==========================================================

elif menu == "Predicción de demanda":

    st.header("Predicción de demanda", icon=":material/trending_up:")

    st.write(
        "Modelo de aprendizaje automático que aprende patrones de demanda "
        "del historial de ventas registrado en el sistema."
    )

    st.info(
        "El entrenamiento evalúa las fechas más recientes y activa el modelo "
        "solo si supera el error de una referencia basada en las ventas de hace 7 días."
    )

    st.warning(
        "Los días sin ventas registradas se interpretan como cero ventas. "
        "Si el producto estuvo agotado, la demanda real podría ser mayor."
    )

    estado_actual = prediction.estado_modelo()
    if estado_actual["estado"] == "ok":
        st.success(
            f"Modelo activo: {estado_actual['algoritmo']}. "
            f"Entrenado el {estado_actual['fecha_entrenamiento']}; "
            f"historial hasta {estado_actual['fecha_fin_historial']}."
        )
        if (
            estado_actual.get("almacenamiento") == "archivo local"
            and database.usar_supabase()
        ):
            st.warning(
                "Este modelo solo está guardado en el almacenamiento temporal del "
                "servidor. Al entrenar, la aplicación intenta crear la tabla de "
                "Supabase automáticamente. Si la conexión no tiene permiso, ejecute "
                "migracion_modelo_demanda.sql en Supabase y vuelva a entrenarlo."
            )
        st.caption(
            "Las ventas nuevas se usan como contexto para pronosticar. "
            "Vuelve a entrenar para que el modelo aprenda también de esos registros."
        )
        evaluacion_actual = estado_actual.get("evaluacion", {})
        if evaluacion_actual:
            st.caption(
                f"Evaluación temporal: MAE {evaluacion_actual['mae']:.2f} unidades; "
                f"baseline de 7 días {evaluacion_actual['mae_baseline_7_dias']:.2f}."
            )
    else:
        st.info(estado_actual.get("mensaje", "Entrene el modelo para habilitar predicciones."))

    if st.button("Entrenar y evaluar modelo", key="entrenar_modelo_demanda"):
        with st.spinner("Preparando historial y evaluando Random Forest..."):
            resultado_entrenamiento = prediction.entrenar_modelo()
        evaluacion = resultado_entrenamiento.get("evaluacion", {})
        if resultado_entrenamiento["estado"] == "ok":
            st.success(resultado_entrenamiento["mensaje"])
        elif resultado_entrenamiento["estado"] == "no_supera_baseline":
            st.warning(resultado_entrenamiento["mensaje"])
        else:
            st.warning(resultado_entrenamiento["mensaje"])
        if evaluacion:
            m1, m2, m3 = st.columns(3)
            m1.metric("MAE del modelo", f"{evaluacion['mae']:.2f} unidades")
            m2.metric("MAE de referencia", f"{evaluacion['mae_baseline_7_dias']:.2f} unidades")
            m3.metric("WAPE del modelo", f"{evaluacion['wape_porcentaje']:.1f}%")
            st.caption(
                f"Prueba cronológica: {evaluacion['fecha_inicio_prueba']} a "
                f"{evaluacion['fecha_fin_prueba']}; "
                f"{evaluacion['observaciones_prueba']} observaciones en "
                f"{evaluacion['ventanas_prueba_7_dias']} ventanas de 7 días."
            )

    productos = prediction.obtener_productos()

    if productos.empty:

        st.warning(
            "No existen productos registrados."
        )

    else:

        opciones = {
            int(fila["id"]): (
                f"{fila['codigo']} - {fila['nombre']} | "
                f"Stock: {fila['stock']}"
            )
            for _, fila in productos.iterrows()
        }

        producto_id = st.selectbox(
            "Seleccionar producto",
            list(opciones.keys()),
            format_func=lambda valor: opciones[valor]
        )

        dias = st.number_input(
            "Días a predecir",
            min_value=1,
            max_value=30,
            value=7,
            step=1
        )

        if st.button("Generar predicción"):

            resultado = prediction.predecir_demanda(
                producto_id,
                int(dias)
            )

            if resultado["estado"] == "ok":

                c1, c2, c3 = st.columns(3)

                with c1:
                    st.metric(
                        "Días históricos",
                        resultado["dias_historicos"]
                    )

                with c2:
                    st.metric(
                        "Demanda estimada",
                        f"{resultado['demanda_predicha']:.2f} unidades"
                    )

                with c3:
                    st.metric(
                        "Modelo",
                        resultado["algoritmo"]
                    )

                evaluacion = resultado.get("evaluacion", {})
                if evaluacion:
                    st.caption(
                        f"Error MAE en evaluación temporal: "
                        f"{evaluacion['mae']:.2f} unidades por producto y día."
                    )

                st.divider()

                st.subheader(
                    f"Demanda estimada del "
                    f"{pd.to_datetime(resultado['fechas_prediccion'][0]).strftime('%d/%m/%Y')} "
                    f"al {pd.to_datetime(resultado['fechas_prediccion'][-1]).strftime('%d/%m/%Y')}"
                )

                st.caption(
                    "Última venta registrada del producto: "
                    f"{pd.to_datetime(resultado['fecha_ultima_venta_producto']).strftime('%d/%m/%Y')}. "
                    "La predicción parte del día posterior a la fecha de corte "
                    f"{pd.to_datetime(resultado['fecha_base_prediccion']).strftime('%d/%m/%Y')}; "
                    "los días sin registros se interpretan como cero ventas."
                )

                fechas_grafico_pred = pd.to_datetime(
                    resultado["fechas_prediccion"]
                )
                valores_grafico_pred = [
                    round(valor, 2)
                    for valor in resultado["predicciones"]
                ]
                datos_tabla_pred = {
                    "Fecha": [
                        pd.to_datetime(fecha).strftime("%d/%m/%Y")
                        for fecha in resultado["fechas_prediccion"]
                    ],
                    "Unidades estimadas": [
                        formatear_numero_es(valor, 2)
                        for valor in resultado["predicciones"]
                    ]
                }

                grafico_prediccion = go.Figure(
                    go.Scatter(
                        x=fechas_grafico_pred,
                        y=valores_grafico_pred,
                        mode="lines+markers",
                        line={"color": "#2a9d8f", "width": 3},
                        marker={"size": 7, "color": "#2a9d8f"},
                        hovertemplate=(
                            "%{x|%d/%m/%Y}<br>"
                            "Unidades estimadas: %{y:.2f}<extra></extra>"
                        ),
                    )
                )
                grafico_prediccion.update_layout(
                    height=430,
                    margin={"l": 20, "r": 20, "t": 20, "b": 20},
                    hovermode="x unified",
                    xaxis={
                        "title": None,
                        "tickmode": "array",
                        "tickvals": fechas_grafico_pred,
                        "tickformat": "%d/%m",
                        "fixedrange": True,
                    },
                    yaxis={
                        "title": "Unidades estimadas",
                        "rangemode": "tozero",
                        "fixedrange": True,
                    },
                    separators=",.",
                    uirevision="prediccion-demanda",
                )
                mostrar_grafico_fijo(
                    grafico_prediccion,
                    "grafico_prediccion_demanda",
                )

                st.subheader("Detalle de la predicción")

                st.dataframe(
                    datos_tabla_pred,
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "Unidades estimadas": st.column_config.TextColumn(
                            "Unidades estimadas",
                            alignment="right",
                        ),
                    },
                )

                st.subheader("Necesidad de reposición")

                producto = productos[
                    productos["id"] == producto_id
                ].iloc[0]

                stock_actual = float(producto["stock"])
                stock_minimo = float(producto["stock_minimo"])

                cantidad_sugerida = max(
                    0,
                    math.ceil(
                        resultado["demanda_predicha"]
                        + stock_minimo
                        - stock_actual
                    )
                )

                if cantidad_sugerida > 0:

                    st.warning(
                        f"Se estima una necesidad de reposición "
                        f"de aproximadamente {cantidad_sugerida} unidad(es), "
                        f"considerando la demanda proyectada y el stock mínimo."
                    )

                else:

                    st.success(
                        "El stock actual cubre la demanda estimada "
                        "y el stock mínimo configurado."
                    )

            else:

                st.warning(resultado["mensaje"])


with st.container(key="theme_toggle"):
    st.button(
        "Tema",
        key="darkModeBtn",
        icon=(
            ":material/dark_mode:"
            if st.session_state.tema_blanco
            else ":material/light_mode:"
        ),
        on_click=alternar_tema,
        help="Cambiar entre modo claro y modo oscuro"
    )

# ==========================================================
# Este bloque va al final para prevalecer sobre estilos anteriores.
# ==========================================================

st.markdown("""
<style>
/* El contenedor externo no dibuja un segundo borde. */
.st-key-registered_users_table [data-testid="stTable"] {
    padding: 0 !important;
    margin: 0 !important;
    border: 0 !important;
    border-radius: 14px !important;
    overflow: hidden !important;
    background: transparent !important;
    box-shadow: none !important;
    box-sizing: border-box !important;
}

/* Un único marco continuo alrededor de toda la tabla. */
.st-key-registered_users_table [data-testid="stTable"] table {
    display: table !important;
    width: 100% !important;
    margin: 0 !important;
    border: 1px solid #b8cbce !important;
    border-collapse: separate !important;
    border-spacing: 0 !important;
    border-radius: 14px !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
    background: #dff4ef !important;
}

/* Líneas internas continuas, sin bordes duplicados. */
.st-key-registered_users_table [data-testid="stTable"] th,
.st-key-registered_users_table [data-testid="stTable"] td {
    box-sizing: border-box !important;
    border: 0 !important;
    border-right: 1px solid #cbdde0 !important;
    border-bottom: 1px solid #cbdde0 !important;
    text-align: left !important;
    vertical-align: middle !important;
}

/* Encabezado. */
.st-key-registered_users_table [data-testid="stTable"] th {
    background: #edf4f4 !important;
    color: #29434a !important;
    font-weight: 750 !important;
    white-space: nowrap !important;
}

/* Celdas del cuerpo. */
.st-key-registered_users_table [data-testid="stTable"] td {
    background: #ffffff !important;
    color: #33474f !important;
}

/* No dibujar líneas extra en los extremos. */
.st-key-registered_users_table [data-testid="stTable"] th:last-child,
.st-key-registered_users_table [data-testid="stTable"] td:last-child {
    border-right: 0 !important;
}
.st-key-registered_users_table [data-testid="stTable"] tbody tr:last-child td {
    border-bottom: 0 !important;
}

/* Evitar que estilos globales alteren las esquinas. */
.st-key-registered_users_table [data-testid="stTable"] thead tr:first-child th:first-child {
    border-top-left-radius: 12px !important;
}
.st-key-registered_users_table [data-testid="stTable"] thead tr:first-child th:last-child {
    border-top-right-radius: 12px !important;
}
.st-key-registered_users_table [data-testid="stTable"] tbody tr:last-child td:first-child {
    border-bottom-left-radius: 12px !important;
}
.st-key-registered_users_table [data-testid="stTable"] tbody tr:last-child td:last-child {
    border-bottom-right-radius: 12px !important;
}

/* Tema oscuro: conservar el marco y las uniones de los bordes. */
body:not(:has(.hb-light-mode)) .st-key-registered_users_table [data-testid="stTable"] table {
    border-color: #344650 !important;
    background: #171e23 !important;
}
body:not(:has(.hb-light-mode)) .st-key-registered_users_table [data-testid="stTable"] th {
    background: #202a31 !important;
    color: #e7edf0 !important;
    border-right-color: #344650 !important;
    border-bottom-color: #344650 !important;
}
body:not(:has(.hb-light-mode)) .st-key-registered_users_table [data-testid="stTable"] td {
    background: #171e23 !important;
    color: #d9e1e5 !important;
    border-right-color: #344650 !important;
    border-bottom-color: #344650 !important;
}
</style>
""", unsafe_allow_html=True)



# ==========================================================
# MARCO EXTERIOR DEFINITIVO: CIERRA LOS CUATRO LADOS
# ==========================================================

st.markdown("""
<style>
/* El marco se dibuja encima de la tabla para que el lado derecho
   y las esquinas queden cerrados aunque Streamlit cambie sus bordes. */
.st-key-registered_users_table [data-testid="stTable"] {
    position: relative !important;
    border: 0 !important;
    border-radius: 14px !important;
    overflow: hidden !important;
}
.st-key-registered_users_table [data-testid="stTable"]::after {
    content: "" !important;
    position: absolute !important;
    inset: 0 !important;
    border: 1px solid #263b44 !important;
    border-radius: 14px !important;
    box-sizing: border-box !important;
    pointer-events: none !important;
    z-index: 10 !important;
}
.st-key-registered_users_table [data-testid="stTable"] table {
    width: 100% !important;
    border: 0 !important;
    border-collapse: separate !important;
    border-spacing: 0 !important;
    border-radius: 14px !important;
    overflow: hidden !important;
}
/* La última columna y la última fila conservan sus separadores internos;
   el marco superpuesto forma el cierre exterior negro continuo. */
.st-key-registered_users_table [data-testid="stTable"] th:last-child,
.st-key-registered_users_table [data-testid="stTable"] td:last-child {
    border-right: 0 !important;
}
.st-key-registered_users_table [data-testid="stTable"] tbody tr:last-child td {
    border-bottom: 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# AJUSTE FINO: REDUCIR EL CONTORNO Y EL ESPACIO INTERIOR
# DE LOS PANELES DE TRANSFERENCIA Y ELIMINACION
# ==========================================================

st.markdown("""
<style>
body:has(.hb-light-mode) .st-key-user_transfer_panel,
body:has(.hb-light-mode) .st-key-user_delete_panel {
    padding: 0.85rem !important;
    border: 1px solid #d4e1e3 !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 12px rgba(35, 91, 98, 0.045) !important;
}
body:has(.hb-light-mode) .st-key-user_transfer_panel:hover,
body:has(.hb-light-mode) .st-key-user_delete_panel:hover {
    border-color: #c4d8da !important;
    box-shadow: 0 5px 14px rgba(35, 91, 98, 0.06) !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# AJUSTE ADICIONAL: CONTORNO MAS DISCRETO EN LOS PANELES
# ==========================================================

st.markdown("""
<style>
body:has(.hb-light-mode) .st-key-user_transfer_panel,
body:has(.hb-light-mode) .st-key-user_delete_panel {
    padding: 0.7rem !important;
    border: 1px solid #e1e9ea !important;
    border-radius: 10px !important;
    box-shadow: 0 2px 7px rgba(35, 91, 98, 0.025) !important;
}
body:has(.hb-light-mode) .st-key-user_transfer_panel:hover,
body:has(.hb-light-mode) .st-key-user_delete_panel:hover {
    border-color: #d7e3e4 !important;
    box-shadow: 0 3px 9px rgba(35, 91, 98, 0.035) !important;
}

/* Reducir el espacio sobrante entre el borde superior y el título. */
body:has(.hb-light-mode) .st-key-user_transfer_panel,
body:has(.hb-light-mode) .st-key-user_delete_panel {
    padding-top: 0.25rem !important;
}
body:has(.hb-light-mode) .st-key-user_transfer_panel h3,
body:has(.hb-light-mode) .st-key-user_delete_panel h3 {
    margin-top: 0.2rem !important;
}
</style>
""", unsafe_allow_html=True)
