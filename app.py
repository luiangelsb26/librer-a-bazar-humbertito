import streamlit as st
import sqlite3
import importlib
from pathlib import Path
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
            outline: 3px solid rgba(45, 129, 119, 0.4) !important;
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
            transition: transform 160ms ease, box-shadow 160ms ease;
        }
        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 24px rgba(20, 28, 32, 0.12);
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
            transition: transform 140ms ease, box-shadow 140ms ease;
        }
        [data-testid="stMain"] button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
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
    gap:1rem; margin:.2rem 0 1.45rem;
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
    border-color:#3ca193 !important; transform:translateY(-1px) !important;
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
            [data-testid="stDataFrame"] * {
                background-color: #ffffff !important;
                color: #263238 !important;
                border-color: #e5e7eb !important;
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
            }
            [data-testid="stTable"] td {
                background: #ffffff !important;
                color: #263238 !important;
                border-color: #e5e7eb !important;
            }
            [data-testid="stDataFrame"] [role="columnheader"] {
                background-color: #f1f5f9 !important;
                color: #263238 !important;
                font-weight: 700 !important;
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
                border: 2px solid var(--humbertito-teal) !important;
                border-radius: 0.65rem !important;
                color: #263238 !important;
                box-shadow: 0 3px 8px rgba(45, 129, 119, 0.16), inset 0 1px 0 rgba(255, 255, 255, 0.55);
            }
            [data-testid="stSidebar"] [class*="st-key-menu_active"] button:hover {
                background: #dce2e7 !important;
                border-color: #24665f !important;
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
    gap:1rem; margin:.2rem 0 1.45rem;
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
    border-color:#3ca193 !important; transform:translateY(-1px) !important;
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
    padding: 1.35rem 2.2rem 3rem !important;
}
[data-testid="stMain"] {
    min-width: 0;
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

DB_PATH = Path(__file__).resolve().parent / "data" / "humbertito.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
database.crear_base_datos()


# ==========================================================
# AUTENTICACIÓN Y CONTROL DE ACCESO
# ==========================================================

auth.inicializar()


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
            max-width: 620px !important;
            min-height: 100vh !important;
            padding: 2rem 1.25rem !important;
            margin: 0 auto !important;
            box-sizing: border-box !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
        }

        [data-testid="stMainBlockContainer"] > div {
            width: 100% !important;
        }

        .login-brand {
            text-align: center;
            margin-bottom: 1.15rem;
        }
        .login-brand-badge {
            display: inline-block;
            padding: 0.35rem 0.75rem;
            border: 1px solid rgba(45,129,119,0.45);
            border-radius: 999px;
            color: #8ed1c8;
            background: rgba(45,129,119,0.10);
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }
        .login-brand-title {
            margin-top: 0.8rem;
            color: #ffffff;
            font-family: Georgia, "Times New Roman", serif;
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: -0.025em;
        }
        .login-brand-subtitle {
            margin-top: 0.35rem;
            color: #9eabb2;
            font-size: 0.88rem;
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
        </style>
    """, unsafe_allow_html=True)

    st.markdown(
        """
        <div class="login-brand">
            <div class="login-brand-badge">SISTEMA DE GESTIÓN</div>
            <div class="login-brand-title">LIBRERÍA BAZAR “HUMBERTITO”</div>
            <div class="login-brand-subtitle">Gestión comercial inteligente · Humbertito IA</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if auth.cantidad_usuarios() == 0:
        st.info(
            "Primera configuración: crea la cuenta del administrador."
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
                        st.success(
                            "Administrador creado. Inicia sesión."
                        )
                        st.rerun()
                    except ValueError as error:
                        st.error(str(error))

    else:
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
    return sqlite3.connect(DB_PATH)


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
        ORDER BY nombre
    """)
    resultado = cur.fetchall()
    con.close()
    return resultado


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

    except sqlite3.IntegrityError:
        return False, "El código del producto ya existe."

    except Exception as e:
        return False, f"Error: {e}"

    finally:
        con.close()


# ==========================================================
# VENTAS
# ==========================================================

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
            dv.subtotal
        FROM ventas v
        JOIN detalle_ventas dv
            ON v.id = dv.venta_id
        JOIN productos p
            ON dv.producto_id = p.id
        ORDER BY v.id DESC
    """).fetchall()

    con.close()
    return resultado


def registrar_venta(producto_id, cantidad):
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

        if cantidad <= 0:
            return False, "La cantidad debe ser mayor que 0."

        if cantidad > stock_actual:
            return False, f"Stock insuficiente. Stock disponible: {stock_actual}"

        subtotal = precio_venta * cantidad
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cur = con.execute("""
            INSERT INTO ventas (fecha, total)
            VALUES (?, ?)
        """, (fecha, subtotal))

        venta_id = cur.lastrowid

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
            precio_venta,
            subtotal
        ))

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
            f"Stock restante: {nuevo_stock}."
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

    resultado = con.execute("""
        SELECT
            c.id,
            c.fecha,
            c.total,
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

    con.close()
    return resultado


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
        """, (fecha, subtotal))

        compra_id = cur.lastrowid

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


# ==========================================================
# DASHBOARD
# ==========================================================

def resumen_dashboard():
    con = conectar()

    ventas, cantidad_ventas = con.execute("""
        SELECT COALESCE(SUM(total), 0), COUNT(*)
        FROM ventas
    """).fetchone()

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

    return ventas, cantidad_ventas, compras, stock_bajo


def resumen_operativo():
    ventas, cantidad_ventas, compras, stock_bajo = resumen_dashboard()
    margen_neto = ventas - compras
    costo_promedio = compras / cantidad_ventas if cantidad_ventas else 0
    return {
        "ventas": ventas,
        "cantidad_ventas": cantidad_ventas,
        "compras": compras,
        "stock_bajo": stock_bajo,
        "margen_neto": margen_neto,
        "costo_promedio_por_venta": costo_promedio,
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
# ENCABEZADO
# ==========================================================

st.markdown("""
<div class="hb-page-header">
    <div>
        <h1 class="hb-page-title">Humbertito IA</h1>
        <p class="hb-page-subtitle">
            Gestión comercial inteligente · apoyo a la toma de decisiones gerenciales
        </p>
    </div>
    <div class="hb-status-pill">
        <span class="hb-status-dot"></span>
        Sistema operativo
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================================
# INDICADORES
# ==========================================================

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Productos registrados", contar_productos())

with c2:
    st.metric("Stock disponible", obtener_stock())

with c3:
    st.metric("Estado del sistema", "Activo")

st.divider()


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
                <span class="user-status-text">SESIÓN ACTIVA</span>
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

    for indice, opcion in enumerate(opciones_menu):
        clave = "menu_active" if opcion == st.session_state.menu else f"menu_item_{indice}"
        if st.button(opcion, key=clave):
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
                st.success(
                    "Sistema reiniciado correctamente. Ya puedes comenzar un nuevo registro."
                )
                st.rerun()
            except Exception as error:
                st.error(f"No se pudo reiniciar el sistema: {error}")

# ==========================================================
# INICIO
# ==========================================================

if menu == "Inicio":

    st.header("Panel principal")

    operacion = resumen_operativo()
    alertas = obtener_alertas_stock(3)

    st.success(
        "Sistema operativo y conectado correctamente con la base de datos."
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Ingresos totales", f"S/ {operacion['ventas']:.2f}")
    with k2:
        st.metric("Margen neto", f"S/ {operacion['margen_neto']:.2f}")
    with k3:
        st.metric("Stock crítico", operacion['stock_bajo'])
    with k4:
        st.metric("Ventas registradas", operacion['cantidad_ventas'])

    st.divider()

    st.subheader("Acciones rápidas")
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
        if st.button("Ir a productos", key="quick_productos"):
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
        if st.button("Ir a ventas", key="quick_ventas"):
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
        if st.button("Ir a compras", key="quick_compras"):
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
        if st.button("Ver dashboard", key="quick_dashboard"):
            st.session_state.menu = "Dashboard gerencial"
            st.rerun()

    st.divider()

    st.subheader("Recomendación del día")

    if alertas:
        st.warning("Hay productos con stock bajo o al límite mínimo de inventario.")
        st.markdown(
            """
            <ul class="alert-list">
                <li>Revisa primero el inventario crítico antes de cerrar el día.</li>
                <li>Prioriza reposiciones de los productos con mayor rotación.</li>
                <li>Verifica si la demanda proyectada supera el stock disponible.</li>
            </ul>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.success("El inventario está saludable y no requiere reposición urgente.")
        st.markdown(
            """
            <ul class="alert-list">
                <li>Tu stock general está estable.</li>
                <li>Puedes seguir monitoreando ventas y tendencias.</li>
                <li>La próxima compra puede enfocarse en artículos con más movimiento.</li>
            </ul>
            """,
            unsafe_allow_html=True,
        )

    st.info(
        "Utilice el menú lateral para gestionar productos, compras, ventas y análisis inteligente de la operación."
    )

    
# ==========================================================
# ADMINISTRACIÓN DE USUARIOS
# ==========================================================

elif menu == "Administrar usuarios":

    if not es_admin:
        st.error("No tienes permisos para administrar usuarios.")
        st.stop()

    st.header("Administración de usuarios")

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
                    st.success(
                        f"Usuario {username} creado correctamente."
                    )
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))

    st.divider()
    st.subheader("Usuarios registrados")

    usuarios = auth.listar_usuarios()

    if usuarios:
        # Tabla HTML/estática para que la información se mantenga visible
        # tanto en modo oscuro como en modo blanco.
        tabla_usuarios = [
            {
                "ID": u[0],
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

        st.table(
            tabla_usuarios,
            border=True,
            width="stretch",
            hide_index=True
        )
    else:
        st.info("Todavía no hay usuarios registrados.")


# ==========================================================
# DASHBOARD
# ==========================================================

elif menu == "Dashboard gerencial":

    st.header("Dashboard gerencial")

    ventas, cantidad_ventas, compras, stock_bajo = resumen_dashboard()

    d1, d2, d3, d4 = st.columns(4)

    with d1:
        st.metric("Ventas acumuladas", f"S/ {ventas:.2f}")

    with d2:
        st.metric("Número de ventas", cantidad_ventas)

    with d3:
        st.metric("Compras acumuladas", f"S/ {compras:.2f}")

    with d4:
        st.metric("Productos con stock bajo", stock_bajo)

    st.divider()

    resumen = analysis.resumen_ventas()
    tendencia = analysis.tendencia_ventas()

    s1, s2, s3 = st.columns(3)

    with s1:
        st.metric(
            "Unidades vendidas",
            int(resumen["unidades_vendidas"])
        )

    with s2:
        st.metric(
            "Días con ventas",
            int(resumen["dias_con_ventas"])
        )

    with s3:
        st.metric(
            "Promedio diario",
            f"S/ {resumen['promedio_diario']:.2f}"
        )

    st.subheader("Evolución de las ventas")

    datos_dia = analysis.obtener_datos_ventas()

    if not datos_dia.empty:
        diario = (
            datos_dia.groupby(
                datos_dia["fecha"].dt.date
            )["subtotal"]
            .sum()
            .rename("Ventas")
        )

        st.line_chart(diario)
    else:
        st.info("No existen ventas para mostrar.")

    st.subheader("Productos con mayor movimiento")

    top = analysis.productos_mas_vendidos()

    if not top.empty:
        st.bar_chart(
            top.set_index("nombre")["unidades_vendidas"]
        )
    else:
        st.info("No existen ventas registradas.")


# ==========================================================
# PRODUCTOS
# ==========================================================

elif menu == "Productos":

    st.header("Gestión de productos")

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
                        st.success(mensaje)
                        st.rerun()
                    else:
                        st.error(mensaje)

    with tab2:

        productos = obtener_productos()

        if productos:

            tabla = []

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

            st.table(tabla)

        else:

            st.info("Todavía no hay productos registrados.")


# ==========================================================
# VENTAS
# ==========================================================

elif menu == "Ventas":

    st.header("Gestión de ventas")

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

            vender = st.form_submit_button(
                "Registrar venta"
            )

            if vender:

                ok, mensaje = registrar_venta(
                    productos[indice][0],
                    cantidad
                )

                if ok:
                    st.success(mensaje)
                    st.rerun()
                else:
                    st.error(mensaje)

        st.subheader("Historial de ventas")

        ventas = obtener_ventas()

        if ventas:

            tabla = []

            for venta in ventas:
                tabla.append({
                    "Venta": venta[0],
                    "Fecha": venta[1],
                    "Total": f"S/ {venta[2]:.2f}",
                    "Producto": venta[3],
                    "Cantidad": venta[4],
                    "Precio unitario": f"S/ {venta[5]:.2f}",
                    "Subtotal": f"S/ {venta[6]:.2f}"
                })

            st.table(tabla)

        else:

            st.info("Todavía no hay ventas registradas.")


# ==========================================================
# COMPRAS
# ==========================================================

elif menu == "Compras":

    st.header("Gestión de compras")

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
                    st.success(mensaje)
                    st.rerun()
                else:
                    st.error(mensaje)

        st.subheader("Historial de compras")

        compras = obtener_compras()

        if compras:

            tabla = []

            for compra in compras:
                tabla.append({
                    "Compra": compra[0],
                    "Fecha": compra[1],
                    "Total": f"S/ {compra[2]:.2f}",
                    "Producto": compra[3],
                    "Cantidad": compra[4],
                    "Precio unitario": f"S/ {compra[5]:.2f}",
                    "Subtotal": f"S/ {compra[6]:.2f}"
                })

            st.table(tabla)

        else:

            st.info("Todavía no hay compras registradas.")


# ==========================================================
# ANÁLISIS INTELIGENTE
# ==========================================================

elif menu == "Análisis inteligente":

    st.header("Análisis inteligente")

    resumen = analysis.resumen_ventas()
    tendencia = analysis.tendencia_ventas()

    st.subheader("Resumen comercial")

    a1, a2, a3, a4 = st.columns(4)

    with a1:
        st.metric(
            "Ventas",
            f"S/ {resumen['total_ventas']:.2f}"
        )

    with a2:
        st.metric(
            "Unidades vendidas",
            int(resumen["unidades_vendidas"])
        )

    with a3:
        st.metric(
            "Días con ventas",
            int(resumen["dias_con_ventas"])
        )

    with a4:
        st.metric(
            "Promedio diario",
            f"S/ {resumen['promedio_diario']:.2f}"
        )

    st.divider()

    st.subheader("Tendencia de ventas")

    st.info(
        f"Tendencia identificada: {tendencia['tipo']}"
    )

    st.subheader("Productos más vendidos")

    top = analysis.productos_mas_vendidos()

    if not top.empty:
        st.table(top)

    else:

        st.info(
            "Todavía no existen ventas suficientes para realizar este análisis."
        )

    st.subheader("Productos con stock bajo")

    bajo = analysis.productos_stock_bajo()

    if not bajo.empty:
        st.table(bajo)

    else:

        st.success(
            "No existen productos con stock bajo."
        )

    st.subheader("Clasificación del comportamiento de productos")

    comportamiento = analysis.analisis_productos()

    if not comportamiento.empty:
        st.table(
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
            ]
        )

    else:

        st.info(
            "No existen productos para analizar."
        )

# ==========================================================
# PREDICCIÓN DE DEMANDA
# ==========================================================

elif menu == "Predicción de demanda":

    st.header("Predicción de demanda")

    st.write(
        "Estimación de la demanda futura a partir del historial "
        "de ventas registrado en el sistema."
    )

    st.info(
        "Para realizar una estimación se requiere historial de "
        "ventas en al menos 3 días distintos por producto."
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
                        "Tendencia",
                        resultado["tendencia"].capitalize()
                    )

                st.divider()

                st.subheader(
                    f"Demanda estimada para los próximos {int(dias)} días"
                )

                nombres_dias = [
                    f"Día {i}"
                    for i in range(1, int(dias) + 1)
                ]

                datos_pred = {
                    "Día": nombres_dias,
                    "Unidades estimadas": [
                        round(valor, 2)
                        for valor in resultado["predicciones"]
                    ]
                }

                st.line_chart(
                    datos_pred,
                    x="Día",
                    y="Unidades estimadas"
                )

                st.subheader("Detalle de la predicción")

                st.dataframe(
                    datos_pred,
                    width="stretch",
                    hide_index=True
                )

                st.subheader("Necesidad de reposición")

                producto = productos[
                    productos["id"] == producto_id
                ].iloc[0]

                stock_actual = float(producto["stock"])
                stock_minimo = float(producto["stock_minimo"])

                cantidad_sugerida = max(
                    0,
                    round(
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

            elif resultado["estado"] == "datos_insuficientes":

                st.warning(
                    resultado["mensaje"]
                )

                st.write(
                    "Registre ventas del mismo producto en diferentes "
                    "días para poder generar una estimación."
                )

            else:

                st.info(
                    resultado["mensaje"]
                )


with st.container(key="theme_toggle"):
    st.button(
        "C" if st.session_state.tema_blanco else "O",
        key="darkModeBtn",
        on_click=alternar_tema,
        help="Cambiar entre modo claro y modo oscuro"
    )
    