import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

BASE_DIR = Path(__file__).parent
EXCEL_PATH = BASE_DIR / "Avances 26-1-PH2.xlsx"
DB_PATH = BASE_DIR / "avances.db"

st.set_page_config(
    page_title="Avances 26-1-PH2",
    page_icon="📋",
    layout="wide",
)


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def limpiar_texto(valor):
    if pd.isna(valor):
        return ""

    return str(valor).strip()


def normalizar_avance(valor):
    try:
        numero = float(valor)

        if numero <= 1:
            numero = numero * 100

        numero = round(numero)

        if numero < 0:
            numero = 0

        if numero > 100:
            numero = 100

        return int(numero)

    except (TypeError, ValueError):
        return 0


def obtener_columna(df, nombre_columna):
    if nombre_columna in df.columns:
        return df[nombre_columna].apply(limpiar_texto)

    return pd.Series(
        [""] * len(df),
        index=df.index,
    )


# =========================================================
# LECTURA DEL EXCEL
# =========================================================

@st.cache_data(show_spinner=False)
def cargar_actividades():
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(
            "No se encontró el archivo Avances 26-1-PH2.xlsx."
        )

    df = pd.read_excel(
        EXCEL_PATH,
        sheet_name=0,
        engine="openpyxl",
    )

    df.columns = [
        limpiar_texto(columna)
        for columna in df.columns
    ]

    columnas_requeridas = [
        "Itm",
        "Nombre de tarea",
        "Líder",
        "%",
    ]

    columnas_faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in df.columns
    ]

    if columnas_faltantes:
        mensaje = ", ".join(columnas_faltantes)

        raise ValueError(
            "Faltan estas columnas en el Excel: "
            + mensaje
        )

    df["Itm"] = pd.to_numeric(
        df["Itm"],
        errors="coerce",
    )

    df = df[
        df["Itm"].notna()
    ].copy()

    df["Itm"] = df["Itm"].astype(int)

    df["Líder"] = obtener_columna(
        df,
        "Líder",
    )

    df["Nombre de tarea"] = obtener_columna(
        df,
        "Nombre de tarea",
    )

    df["Activo"] = obtener_columna(
        df,
        "Activo",
    )

    df["OT"] = obtener_columna(
        df,
        "OT",
    )

    df["Responsable"] = obtener_columna(
        df,
        "Responsable",
    )

    df["Comentarios"] = obtener_columna(
        df,
        "Comentarios",
    )

    df["Avance inicial"] = df["%"].apply(
        normalizar_avance
    )

    df = df[
        df["Líder"] != ""
    ].copy()

    df = df[
        df["Nombre de tarea"] != ""
    ].copy()

    return df


# =========================================================
# BASE DE DATOS
# =========================================================

def conectar_bd():
    conexion = sqlite3.connect(
        DB_PATH,
        check_same_thread=False,
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
    usuario,
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
            str(lider),
            int(avance),
            comentario.strip(),
            usuario.strip(),
            fecha_actual,
        ),
    )

    conexion.commit()
    conexion.close()


def cargar_historial():
    conexion = conectar_bd()

    consulta = (
        "SELECT "
        "id, item, lider, avance, comentario, usuario, fecha "
        "FROM avances "
        "ORDER BY fecha DESC, id DESC"
    )

    historial = pd.read_sql_query(
        consulta,
        conexion,
    )

    conexion.close()

    return historial


def obtener_ultimos_avances():
    historial = cargar_historial()

    if historial.empty:
        return historial

    historial = historial.sort_values(
        by=["fecha", "id"],
        ascending=True,
    )

    ultimos = historial.drop_duplicates(
        subset=["item"],
        keep="last",
    )

    return ultimos


# =========================================================
# SEGURIDAD OPCIONAL
# =========================================================

def obtener_pines():
    try:
        return st.secrets.get(
            "leader_pins",
            {},
        )

    except Exception:
        return {}


def validar_pin(lider, pin):
    pines = obtener_pines()

    if not pines:
        return True

    pin_guardado = str(
        pines.get(lider, "")
    )

    return pin_guardado == str(pin)


# =========================================================
# ENCABEZADO
# =========================================================

st.title("📋 Registro de avances   
