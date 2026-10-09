import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


# =========================================================
# CONFIGURACION
# =========================================================

BASE_DIR = Path(__file__).parent
EXCEL_PATH = BASE_DIR / "Avances 26-1-PH2.xlsx"
DB_PATH = BASE_DIR / "avances.db"

st.set_page_config(
    page_title="Avances 26-1-PH2",
    page_icon="📋",
    layout="wide"
)


# =========================================================
# FUNCIONES GENERALES
# =========================================================

def limpiar_texto(valor)
