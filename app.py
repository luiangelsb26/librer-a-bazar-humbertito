import streamlit as st
import sqlite3
import importlib
from pathlib import Path
from datetime import datetime
import analysis
import prediction
import database

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
        [data-testid="stSidebar"] button[aria-label*="sidebar" i],
        [data-testid="stSidebar"] button[aria-label*="barra lateral" i] {
            display: none !important;
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
            border-left: 2px solid var(--humbertito-teal);
            border-radius: 0 0.35rem 0.35rem 0;
            background: rgba(45, 129, 119, 0.06);
            color: #263238;
        }
        .alert-list li {
            margin-bottom: 0.45rem;
            line-height: 1.5;
            font-size: 0.86rem;
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
        }
        [data-testid="stAlertContainer"] {
            box-sizing: border-box;
            display: flex;
            align-items: center;
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
        }
        [data-testid="stAlert"] p {
            text-align: left !important;
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
    </style>
""", unsafe_allow_html=True)


if st.session_state.tema_blanco:
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
            [data-testid="stMainBlockContainer"] {
                padding: 1rem 0.9rem 2rem !important;
            }
            [data-testid="stMain"] h1 {
                font-size: 1.65rem !important;
            }
            [data-testid="stMain"] h2 {
                font-size: 1.35rem !important;
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


with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
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

st.title("Sistema basado en Inteligencia Artificial")
st.subheader('LIBRERÍA BAZAR “HUMBERTITO”')

st.write(
    "Sistema de apoyo a la toma de decisiones gerenciales "
    "mediante el procesamiento y análisis de información comercial."
)

st.divider()


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
    st.markdown("#### Menú principal")
    opciones_menu = [
        "Inicio",
        "Dashboard gerencial",
        "Productos",
        "Ventas",
        "Compras",
        "Análisis inteligente",
        "Predicción de demanda"
    ]

    if "menu" not in st.session_state:
        st.session_state.menu = "Inicio"

    for indice, opcion in enumerate(opciones_menu):
        clave = "menu_active" if opcion == st.session_state.menu else f"menu_item_{indice}"
        if st.button(opcion, key=clave):
            st.session_state.menu = opcion
            st.rerun()

    menu = st.session_state.menu
    st.caption(f"Sección activa: **{menu}**")
    st.divider()

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
                registros = database.reiniciar_datos()
                st.session_state.pop("confirmar_reinicio", None)
                st.success(
                    "Sistema reiniciado correctamente. Ya puedes comenzar un "
                    "nuevo registro."
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

