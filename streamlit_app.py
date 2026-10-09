import sqlite3
import unicodedata
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


def normalizar_nombre(valor):
    texto = limpiar_texto(valor).lower()

    texto = "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caracter) != "Mn"
    )

    texto = " ".join(texto.split())

    return texto


def limpiar_ot(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()

    try:
        numero = float(texto)

        if numero.is_integer():
            return str(int(numero))

    except (ValueError, TypeError):
        pass

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

    pin_guardado = str(
        pines.get(lider, "")
    )

    return pin_guardado == str(pin)


# CARGAR EXCEL
@st.cache_data(show_spinner=False)
def cargar_actividades():
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(
            "No se encontró el archivo "
            "Avances 26-1-PH2.xlsx"
        )

    vista_previa = pd.read_excel(
        EXCEL_PATH,
        sheet_name=0,
        header=None,
        engine="openpyxl"
    )

    fila_encabezado = None

    for indice, fila in vista_previa.head(100).iterrows():
        valores_normalizados = [
            normalizar_nombre(valor)
            for valor in fila.tolist()
        ]

        if "itm project" in valores_normalizados:
            fila_encabezado = indice
            break

    if fila_encabezado is None:
        raise ValueError(
            "No se encontró la columna 'Itm project' "
            "en las primeras 100 filas del Excel."
        )

    df = pd.read_excel(
        EXCEL_PATH,
        sheet_name=0,
        header=fila_encabezado,
        engine="openpyxl"
    )

    df.columns = [
        limpiar_texto(columna)
        for columna in df.columns
    ]

    nombres_columnas = {
        normalizar_nombre(columna): columna
        for columna in df.columns
    }

    equivalencias = {}

    if "itm project" in nombres_columnas:
        equivalencias[
            nombres_columnas["itm project"]
        ] = "Itm project"

    for nombre_normalizado, columna_real in nombres_columnas.items():
        if nombre_normalizado == "nombre de tarea":
            equivalencias[columna_real] = "Nombre de tarea"

        elif nombre_normalizado == "lider":
            equivalencias[columna_real] = "Líder"

        elif nombre_normalizado == "activo":
            equivalencias[columna_real] = "Activo"

        elif nombre_normalizado == "ubicacion":
            equivalencias[columna_real] = "Ubicacion"

        elif nombre_normalizado == "ot":
            equivalencias[columna_real] = "OT"

        elif nombre_normalizado == "responsable":
            equivalencias[columna_real] = "Responsable"

        elif nombre_normalizado == "comentarios":
            equivalencias[columna_real] = "Comentarios"

        elif (
            nombre_normalizado == "%"
            or nombre_normalizado == "avance"
            or nombre_normalizado == "% avance"
            or nombre_normalizado == "porcentaje"
            or nombre_normalizado == "porcentaje avance"
        ):
            equivalencias[columna_real] = "%"

    df = df.rename(
        columns=equivalencias
    )

    columnas_necesarias = [
        "Itm project",
        "Nombre de tarea",
        "Líder",
        "Ubicacion",
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
            + ". Columnas encontradas: "
            + ", ".join(
                str(columna)
                for columna in df.columns
            )
        )

    df["Itm project"] = pd.to_numeric(
        df["Itm project"],
        errors="coerce"
    )

    df = df[
        df["Itm project"].notna()
    ].copy()

    df["Itm project"] = (
        df["Itm project"].astype(int)
    )

    columnas_texto = [
        "Líder",
        "Nombre de tarea",
        "Activo",
        "Ubicacion",
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

    df["OT"] = df["OT"].apply(
        limpiar_ot
    )

    df["Avance inicial"] = df["%"].apply(
        normalizar_avance
    )

    df = df[
        df["Líder"] != ""
    ].copy()

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
        "ORDER BY id DESC"
    )

    historial = pd.read_sql_query(
        consulta,
        conexion
    )

    conexion.close()

    return historial


def obtener_ultimo_avance(
    item,
    avance_inicial
):
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

    if resultado:
        return int(resultado[0])

    return int(avance_inicial)


def preparar_panel(actividades):
    panel = actividades.copy()

    panel["Avance actual"] = panel.apply(
        lambda fila: obtener_ultimo_avance(
            fila["Itm project"],
            fila["Avance inicial"]
        ),
        axis=1
    )

    panel["Estado"] = panel[
        "Avance actual"
    ].apply(
        lambda avance: (
            "Finalizada"
            if avance >= 100
            else "En proceso"
            if avance > 0
            else "Pendiente"
        )
    )

    return panel


# INICIO DE LA APLICACION
st.title("📋 Registro de avances 26-1-PH2")

try:
    actividades = cargar_actividades()

except Exception as error:
    st.error(str(error))
    st.stop()


pestana_registro, pestana_panel, pestana_historial = st.tabs(
    [
        "Registrar avance",
        "Panel general",
        "Historial"
    ]
)


# PESTANA REGISTRAR AVANCE
with pestana_registro:
    st.header("Registrar avance")

    lideres = sorted(
        actividades["Líder"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    lider_seleccionado = st.selectbox(
        "Selecciona el codigo del lider",
        lideres
    )

    actividades_lider = actividades[
        actividades["Líder"]
        == lider_seleccionado
    ].copy()

    st.info(
        "Actividades asignadas a "
        + lider_seleccionado
        + ": "
        + str(len(actividades_lider))
    )

    opciones_actividades = {}

    for _, fila in actividades_lider.iterrows():
        avance_actual_fila = obtener_ultimo_avance(
            fila["Itm project"],
            fila["Avance inicial"]
        )

        ubicacion = limpiar_texto(
            fila["Ubicacion"]
        )

        nombre_tarea = limpiar_texto(
            fila["Nombre de tarea"]
        )

        texto_opcion = (
            ubicacion
            + " | "
            + nombre_tarea
            + " | "
            + str(avance_actual_fila)
            + "%"
        )

        opciones_actividades[
            texto_opcion
        ] = fila["Itm project"]

    if not opciones_actividades:
        st.warning(
            "Este líder no tiene actividades asignadas."
        )
        st.stop()

    actividad_seleccionada = st.selectbox(
        "Selecciona la actividad",
        list(opciones_actividades.keys())
    )

    item_seleccionado = opciones_actividades[
        actividad_seleccionada
    ]

    fila_actividad = actividades_lider[
        actividades_lider["Itm project"]
        == item_seleccionado
    ].iloc[0]

    avance_actual = obtener_ultimo_avance(
        fila_actividad["Itm project"],
        fila_actividad["Avance inicial"]
    )

    ot_mostrada = limpiar_ot(
        fila_actividad["OT"]
    )

    columna_ot, columna_avance = st.columns(2)

    with columna_ot:
        st.metric(
            label="OT",
            value=ot_mostrada
        )

    with columna_avance:
        st.metric(
            label="Avance actual",
            value=str(avance_actual) + "%"
        )

    responsable = limpiar_texto(
        fila_actividad["Responsable"]
    )

    if responsable:
        st.markdown(
            "**Responsable:** " + responsable
        )

    nuevo_avance = st.slider(
        "Nuevo avance (%)",
        min_value=0,
        max_value=100,
        value=avance_actual,
        step=5
    )

    comentario = st.text_area(
        "Comentario",
        value
