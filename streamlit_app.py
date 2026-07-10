import streamlit as st
import openpyxl
from io import BytesIO
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Salud Equipos",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Dashboard Predictivo")

archivo = st.file_uploader(
    "Seleccione archivo Excel",
    type=["xlsx"]
)

if archivo:

    if st.button("INICIAR"):

        wb = openpyxl.load_workbook(
            BytesIO(archivo.read()),
            data_only=True
        )

        ws = wb["Datos"]

        datos = list(ws.values)

        encabezados = list(datos[0])

        registros = list(datos[1:])

        idx_equipo = encabezados.index("EQUIPO")
        idx_punto = encabezados.index("PUNTO DE MEDICIÓN")

        idx_u = encabezados.index("ESTADO U")
        idx_v = encabezados.index("ESTADO V")
        idx_t = encabezados.index("ESTADO T")
        idx_e = encabezados.index("ESTADO E")

        equipos = sorted(
            list(
                set(
                    fila[idx_equipo]
                    for fila in registros
                )
            )
        )

        equipo = st.selectbox(
            "Seleccione Equipo",
            equipos
        )

        datos_equipo = [
            fila
            for fila in registros
            if fila[idx_equipo] == equipo
        ]

        salud = sum(
            fila[idx_e]
            for fila in datos_equipo
        ) / len(datos_equipo)

        if salud >= 0.9:
            estado = "🟢 NORMAL"
            color = "green"

        elif salud >= 0.7:
            estado = "🟡 ALARMA"
            color = "orange"

        else:
            estado = "🔴 INTERVENIR"
            color = "red"

        punto_critico = min(
            datos_equipo,
            key=lambda x: x[idx_e]
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "SALUD DEL EQUIPO",
                f"{salud:.0%}"
            )

        with c2:
            st.metric(
                "ESTADO",
                estado
            )

        with c3:
            st.metric(
                "PUNTO MÁS CRÍTICO",
                punto_critico[idx_punto]
            )

        # ----------------------
        # VELOCIMETRO
        # ----------------------

        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=salud * 100,

                number={
                    "suffix":"%"
                },

                gauge={
                    "axis":{
