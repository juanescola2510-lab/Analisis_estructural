import streamlit as st
import openpyxl
from io import BytesIO
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Salud Equipos",
    layout="wide"
)

st.title("⚙️ Dashboard Salud de Equipos")

# -------------------------
# CARGA INICIAL
# -------------------------

if "datos" not in st.session_state:
    st.session_state.datos = None

archivo = st.file_uploader(
    "Seleccione archivo Excel",
    type=["xlsx"]
)

if archivo and st.button("INICIAR"):

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

if st.session_state.datos is not None:

    encabezados = st.session_state.datos["encabezados"]
    registros = st.session_state.datos["registros"]

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
                if fila[idx_equipo]
            )
        )
    )

    equipo = st.sidebar.selectbox(
        "Equipo",
        equipos
    )

    datos_equipo = [
        fila
        for fila in registros
        if fila[idx_equipo] == equipo
    ]

    salud = sum(
        float(fila[idx_e])
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
        key=lambda x: float(x[idx_e])
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "SALUD DEL EQUIPO",
        f"{salud:.0%}"
    )

    c2.metric(
        "ESTADO",
        estado
    )

    c3.metric(
        "PUNTO MÁS CRÍTICO",
        punto_critico[idx_punto]
    )

    # ---------------------------------
    # VELOCÍMETRO
    # ---------------------------------

    fig_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=salud * 100,
            number={"suffix": "%"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": color},
                "steps": [
                    {"range": [0, 70], "color": "#ff4d4d"},
                    {"range": [70, 90], "color": "#ffd633"},
                    {"range": [90, 100], "color": "#33cc33"}
                ]
            }
        )
    )

    st.plotly_chart(
        fig_gauge,
        use_container_width=True
    )

    # ---------------------------------
    # BARRAS
    # ---------------------------------

    puntos = [
        fila[idx_punto]
        for fila in datos_equipo
    ]

    salud_puntos = [
        float(fila[idx_e]) * 100
        for fila in datos_equipo
    ]

    fig_bar = px.bar(
        x=salud_puntos,
        y=puntos,
        orientation="h",
