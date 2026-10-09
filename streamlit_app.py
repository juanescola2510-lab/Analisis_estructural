import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


# CONFIGURACION
BASE_DIR = Path(__file__).parent
EXCEL_PATH = BASE_DIR / "Avances 26-1-PH2.xlsx"
DB_PATH = BASE_DIR / "avances.db"

st.set_page_config(
    page_title="Avances 26-1-PH2",
    page_icon="📋",
    layout="wide"
)


# FUNCIONES GENERALES
def limpiar_texto(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip()


def limpiar_ot(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()

    if texto.endswith(".0"):
        texto = texto[:-2]

    return texto


def normalizar_avance(valor):
    try:
        numero = float(valor)

        if numero <= 1:
            numero = numero * 100

        numero = round(numero)

        return max(0, min(100, numero))

    except (TypeError, ValueError):
        return 0


def obtener_pines():
    try:
        return st.secrets.get("leader_pins", {})
    except Exception:
        return {}


def validar_pin(lider, pin):
    pines = obtener_pines()

    if not pines:
        return True

    pin_guardado = str(pines.get(lider, ""))

    return pin_guardado == str(pin)


# CARGAR EXCEL
@st.cache_data(show_spinner=False)
def cargar_actividades():
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(
            "No se encontro el archivo Avances 26-1-PH2.xlsx"
        )

    df = pd.read_excel(
        EXCEL_PATH,
        sheet_name=0,
        header=0,
        engine="openpyxl"
    )

    df.columns = [
        limpiar_texto(columna)
        for columna in df.columns
    ]

    columnas_necesarias = [
        "Itm",
        "Nombre de tarea",
        "Líder",
        "%"
    ]

    columnas_faltantes = [
        columna
        for columna in columnas_necesarias
        if columna not in df.columns
    ]

    if columnas_faltantes:
        raise ValueError(
            "Faltan columnas en el Excel: "
            + ", ".join(columnas_faltantes)
        )

    df["Itm"] = pd.to_numeric(
        df["Itm"],
        errors="coerce"
    )

    df = df[df["Itm"].notna()].copy()
    df["Itm"] = df["Itm"].astype(int)

    columnas_texto = [
        "Líder",
        "Nombre de tarea",
        "Activo",
        "Responsable",
        "Comentarios"
    ]

    for columna in columnas_texto:
        if columna not in df.columns:
            df[columna] = ""

        df[columna] = df[columna].apply(
            limpiar_texto
        )

    if "OT" not in df.columns:
        df["OT"] = ""

    df["OT"] = df["OT"].apply(limpiar_ot)

    df["Avance inicial"] = df["%"].apply(
        normalizar_avance
    )

    df = df[df["Líder"] != ""].copy()

    return df


# BASE DE DATOS
def conectar_bd():
    conexion = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    consulta = (
        "CREATE TABLE IF NOT EXISTS avances ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "item INTEGER NOT NULL, "
        "lider TEXT NOT NULL, "
        "avance INTEGER NOT NULL, "
        "comentario TEXT, "
        "usuario TEXT NOT NULL, "
        "fecha TEXT NOT NULL"
        ")"
    )

    conexion.execute(consulta)
    conexion.commit()

    return conexion


def guardar_avance(
    item,
    lider,
    avance,
    comentario,
    usuario
):
    conexion = conectar_bd()

    consulta = (
        "INSERT INTO avances ("
        "item, lider, avance, comentario, usuario, fecha"
        ") VALUES (?, ?, ?, ?, ?, ?)"
    )

    fecha_actual = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    conexion.execute(
        consulta,
        (
            int(item),
            limpiar_texto(lider),
            int(avance),
            limpiar_texto(comentario),
            limpiar_texto(usuario),
            fecha_actual
        )
    )

    conexion.commit()
    conexion.close()


def cargar_historial():
    conexion = conectar_bd()

    consulta = (
        "SELECT id, item, lider, avance, comentario, "
        "usuario, fecha FROM avances "
        "ORDER BY fecha DESC"
    )

    historial = pd.read_sql_query(
        consulta,
        conexion
    )

    conexion.close()

    return historial


def obtener_ultimo_avance(item, avance_inicial):
    conexion = conectar_bd()

    consulta = (
        "SELECT avance FROM avances "
        "WHERE item = ? "
        "ORDER BY id DESC LIMIT 1"
    )

    resultado = conexion.execute(
        consulta,
        (int(item),)
    ).fetchone()

    conexion.close()

    if 
