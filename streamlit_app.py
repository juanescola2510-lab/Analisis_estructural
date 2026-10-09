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
        header=1,
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

    if resultado:
        return int(resultado[0])

    return int(avance_inicial)


def preparar_panel(actividades):
    panel = actividades.copy()

    panel["Avance actual"] = panel.apply(
        lambda fila: obtener_ultimo_avance(
            fila["Itm"],
            fila["Avance inicial"]
        ),
        axis=1
    )

    panel["Estado"] = panel["Avance actual"].apply(
        lambda avance:
        "Finalizada"
        if avance >= 100
        else "En proceso"
        if avance > 0
        else "Pendiente"
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
        actividades["Líder"] == lider_seleccionado
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
            fila["Itm"],
            fila["Avance inicial"]
        )

        codigo_equipo = limpiar_texto(
            fila["Activo"]
        )

        nombre_tarea = limpiar_texto(
            fila["Nombre de tarea"]
        )

        texto_opcion = (
            codigo_equipo
            + " | "
            + nombre_tarea
            + " | "
            + str(avance_actual_fila)
            + "%"
        )

        opciones_actividades[texto_opcion] = fila["Itm"]

    actividad_seleccionada = st.selectbox(
        "Selecciona la actividad",
        list(opciones_actividades.keys())
    )

    item_seleccionado = opciones_actividades[
        actividad_seleccionada
    ]

    fila_actividad = actividades_lider[
        actividades_lider["Itm"] == item_seleccionado
    ].iloc[0]

    avance_actual = obtener_ultimo_avance(
        fila_actividad["Itm"],
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
        value="",
        placeholder="Escribe un comentario sobre el avance"
    )

    usuario = st.text_input(
        "Nombre de quien actualiza",
        value=""
    )

    pines = obtener_pines()

    if pines:
        pin = st.text_input(
            "PIN del lider",
            type="password"
        )
    else:
        pin = ""

    if st.button(
        "Guardar avance",
        type="primary",
        use_container_width=True
    ):
        if not usuario.strip():
            st.warning(
                "Escribe el nombre de quien actualiza."
            )

        elif not validar_pin(
            lider_seleccionado,
            pin
        ):
            st.error(
                "El PIN ingresado no es correcto."
            )

        else:
            guardar_avance(
                item=fila_actividad["Itm"],
                lider=lider_seleccionado,
                avance=nuevo_avance,
                comentario=comentario,
                usuario=usuario
            )

            st.cache_data.clear()

            st.success(
                "El avance se guardo correctamente."
            )

            st.rerun()


# PESTANA PANEL GENERAL
with pestana_panel:
    st.header("Panel general")

    panel = preparar_panel(actividades)

    total_actividades = len(panel)

    pendientes = len(
        panel[panel["Estado"] == "Pendiente"]
    )

    en_proceso = len(
        panel[panel["Estado"] == "En proceso"]
    )

    finalizadas = len(
        panel[panel["Estado"] == "Finalizada"]
    )

    avance_promedio = (
        round(panel["Avance actual"].mean(), 1)
        if total_actividades > 0
        else 0
    )

    columna_1, columna_2, columna_3, columna_4 = st.columns(4)

    with columna_1:
        st.metric(
            "Total de actividades",
            total_actividades
        )

    with columna_2:
        st.metric(
            "Pendientes",
            pendientes
        )

    with columna_3:
        st.metric(
            "En proceso",
            en_proceso
        )

    with columna_4:
        st.metric(
            "Finalizadas",
            finalizadas
        )

    st.metric(
        "Avance promedio",
        str(avance_promedio) + "%"
    )

    columnas_panel = [
        "Itm",
        "Activo",
        "Nombre de tarea",
        "OT",
        "Líder",
        "Responsable",
        "Avance actual",
        "Estado"
    ]

    columnas_disponibles = [
        columna
        for columna in columnas_panel
        if columna in panel.columns
    ]

    panel_mostrar = panel[
        columnas_disponibles
    ].copy()

    if "OT" in panel_mostrar.columns:
        panel_mostrar["OT"] = panel_mostrar["OT"].apply(
            limpiar_ot
        )

    st.dataframe(
        panel_mostrar,
        use_container_width=True,
        hide_index=True
    )

    archivo_panel = panel_mostrar.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="Descargar panel en CSV",
        data=archivo_panel,
        file_name="panel_avances_26-1-PH2.csv",
        mime="text/csv"
    )


# PESTANA HISTORIAL
with pestana_historial:
    st.header("Historial de actualizaciones")

    historial = cargar_historial()

    if historial.empty:
        st.info(
            "Todavia no existen actualizaciones registradas."
        )

    else:
        historial_mostrar = historial.copy()

        historial_mostrar = historial_mostrar.rename(
            columns={
                "item": "Itm",
                "lider": "Líder",
                "avance": "Avance",
                "comentario": "Comentario",
                "usuario": "Actualizado por",
                "fecha": "Fecha"
            }
        )

        columnas_historial = [
            "Itm",
            "Líder",
            "Avance",
            "Comentario",
            "Actualizado por",
            "Fecha"
        ]

        st.dataframe(
            historial_mostrar[columnas_historial],
            use_container_width=True,
            hide_index=True
        )

        archivo_historial = historial_mostrar[
            columnas_historial
        ].to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            label="Descargar historial en CSV",
            data=archivo_historial,
            file_name="historial_avances_26-1-PH2.csv",
            mime="text/csv"
        )
