import streamlit as st
import importlib
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
            max-width: 12ch;
            margin-top: 1.55rem;
            color: #f5f9f9;
            font-size: clamp(2rem, 3.4vw, 3rem);
            font-weight: 780;
            line-height: 1.03;
            letter-spacing: -0.045em;
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

    mensaje_traspaso = st.session_state.pop(
        "mensaje_traspaso_admin",
        None,
    )
    if mensaje_traspaso:
        st.success(mensaje_traspaso)

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
                            st.success(
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

    except Exception as e:
        if database.es_error_integridad(e):
            return False, "El código del producto ya existe."
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
            RETURNING id
        """, (fecha, subtotal))

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

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Ingresos totales", f"S/ {operacion['ventas']:.2f}", border=True)
    with k2:
        st.metric("Margen neto", f"S/ {operacion['margen_neto']:.2f}", border=True)
    with k3:
        st.metric("Stock crítico", operacion['stock_bajo'], border=True)
    with k4:
        st.metric("Ventas registradas", operacion['cantidad_ventas'], border=True)

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

        st.dataframe(
            tabla_usuarios,
            width="stretch",
            hide_index=True,
            height=360,
        )

        st.divider()
        usuarios_eliminables = [
            usuario for usuario in usuarios
            if str(usuario[0]) != str(usuario_actual.get("id"))
        ]

        with st.container(border=True):
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
                selector, resumen = st.columns([1.3, 1])
                with selector:
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
                with resumen:
                    st.caption("SE TRANSFERIRÁ A")
                    st.markdown(
                        f"**{nuevo_admin[2]}** · @{nuevo_admin[1]}"
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
                        st.session_state["mensaje_traspaso_admin"] = (
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

        st.divider()
        st.subheader("Eliminar una cuenta")
        st.caption(
            "La eliminación es permanente. Las ventas y compras registradas "
            "se conservarán."
        )

        if usuarios_eliminables:
            for usuario in usuarios_eliminables:
                usuario_id, username, nombre, rol_usuario = usuario[:4]
                with st.container(border=True):
                    datos_usuario, accion_usuario = st.columns([4, 1])
                    with datos_usuario:
                        st.write(f"**{nombre}** · @{username}")
                        st.caption(
                            "Administrador" if rol_usuario == "admin" else "Empleado"
                        )
                    with accion_usuario:
                        if st.button(
                            "Eliminar",
                            key=f"preparar_eliminar_usuario_{usuario_id}",
                            icon=":material/delete_outline:",
                            type="secondary",
                            width="stretch",
                        ):
                            st.session_state["usuario_pendiente_eliminar_id"] = usuario_id
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
                st.session_state.pop("usuario_pendiente_eliminar_id", None)
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
                    st.session_state.pop("usuario_pendiente_eliminar_id", None)
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
                        st.success(
                            f"La cuenta @{username} se eliminó correctamente."
                        )
                        st.rerun()
                    except ValueError as error:
                        st.error(str(error))
        else:
            st.info(
                "No hay otras cuentas para eliminar. Crea otra cuenta arriba "
                "para que aparezca aquí. La cuenta que estás usando no se puede eliminar."
            )
    else:
        st.info("Todavía no hay usuarios registrados.")


# ==========================================================
# DASHBOARD
# ==========================================================

elif menu == "Dashboard gerencial":

    st.header("Dashboard gerencial", icon=":material/dashboard:")

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

            st.dataframe(
                tabla,
                width="stretch",
                hide_index=True,
                height=420,
            )

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

            st.dataframe(
                tabla,
                width="stretch",
                hide_index=True,
                height=420,
            )

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

            st.dataframe(
                tabla,
                width="stretch",
                hide_index=True,
                height=420,
            )

        else:

            st.info("Todavía no hay compras registradas.")


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
    