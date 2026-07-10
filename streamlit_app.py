import streamlit as st
import openpyxl
from io import BytesIO
import plotly.graph_objects as go

st.set_page_config(
    page_title="Dashboard Salud Equipos",
    layout="wide"
)

st.title("⚙️ Dashboard Salud de Equipos")

# -------------------------
# MEMORIA
# -------------------------

if "datos" not in st.session_state:
    st.session_state.datos = None

# -------------------------
# SUBIR EXCEL
# -------------------------

archivo = st.file_uploader(
    "Seleccione archivo Excel",
    type=["xlsx"]
)

if archivo is not None and st.button("INICIAR"):

    wb = openpyxl.load_workbook(
        BytesIO(archivo.read()),
        data_only=True
    )

    ws = wb["Datos"]

    datos = list(ws.values)

    encabezados = list(datos[0])

    registros = list(datos[1:])

    st.session_state.datos = {
        "encabezados": encabezados,
        "registros": registros
    }

# -------------------------
# DASHBOARD
# -------------------------

if st.session_state.datos:

    encabezados = st.session_state.datos["encabezados"]
    registros = st.session_state.datos["registros"]

    idx_equipo = encabezados.index("EQUIPO")
    idx_punto = encabezados.index("PUNTO DE MEDICIÓN")
    idx_estado = encabezados.index("ESTADO E")

    equipos = sorted(
        list(
            set(
                fila[idx_equipo]
                for fila in registros
                if fila[idx_equipo] is not None
            )
        )
    )

    equipo = st.sidebar.selectbox(
        "Seleccione Equipo",
        equipos
    )

    datos_equipo = [
        fila
        for fila in registros
        if fila[idx_equipo] == equipo
    ]

    salud = (
        sum(
            float(fila[idx_estado])
            for fila in datos_equipo
        )
        / len(datos_equipo)
    )

    if salud >= 0.90:
        estado = "🟢 NORMAL"

    elif salud >= 0.70:
        estado = "🟡 ALARMA"

    else:
        estado = "🔴 INTERVENIR"

    punto_critico = min(
        datos_equipo,
        key=lambda x: float(x[idx_estado])
    )

    col1, col2 = st.columns(2)

    with col1:

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=salud * 100,

                number={
                    "suffix": "%"
                },

                gauge={
                    "axis": {
                        "range": [0, 100]
                    },

                    "bar": {
                        "color": "black"
                    },

