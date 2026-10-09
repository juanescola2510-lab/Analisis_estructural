import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).parent
EXCEL_PATH = BASE_DIR / "Avances 26-1-PH2.xlsx"
DB_PATH = BASE_DIR / "avances.db"

st.set_page_config(
    page_title="Avances 26-1-PH2",
    page_icon="📋",
    layout="wide",
)


def limpiar_texto(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip()


def normalizar_avance(valor):
    try:
        numero = float(valor)

        if numero <= 1:
            numero *= 100

        return max(0, min(100, round(numero)))

    except (TypeError, ValueError):
        return 0


@st.cache_data(show_spinner=False)
def cargar_actividades():
    df = pd.read_excel(EXCEL_PATH, sheet_name=0)
    df.columns = [limpiar_texto(columna) for columna in df.columns]

    columnas_requeridas = [
        "Itm",
        "Nombre de tarea",
        "Líder",
        "%",
    ]

    faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in df.columns
    ]

    if faltantes:
        raise ValueError(
            f"Faltan columnas en el Excel: {', '.join(faltantes)}"
        )

    df["Itm"] = pd.to_numeric(df["Itm"], errors="coerce")
    df = df[df["Itm"].notna()].copy()
    df["Itm"] = df["Itm"].astype(int)

    for columna in [
        "Líder",
        "Nombre de tarea",
        "Activo",
        "OT",
        "Responsable",
        "Comentarios",
    ]:
        if columna not in df.columns:
            df[columna] = ""

        df[columna] = df[columna].apply(limpiar_texto)

    df["Avance inicial"] = df["%"].apply(normalizar_avance)

    return df


def conectar_bd():
    conexion = sqlite3.connect(
        DB_PATH,
        check_same_thread=False,
    )

    conexion.execute(
        """
        CREATE TABLE IF NOT EXISTS avances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item INTEGER NOT NULL,
            lider TEXT NOT NULL,
            avance INTEGER NOT NULL,
            comentario TEXT,
            usuario TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
        """
    )

    conexion.commit()
    return conexion


def guardar_avance(
    item,
    lider,
    avance,
    comentario,
    usuario,
):
    conexion = conectar_bd()

    conexion.execute(
        """
        INSERT INTO avances (
            item,
 
