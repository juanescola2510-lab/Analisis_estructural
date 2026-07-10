import streamlit as st
import openpyxl
from io import BytesIO
import plotly.graph_objects as go

st.set_page_config(
    page_title="Dashboard Salud Equipos",
    layout="wide"
)

st.title("⚙️ Dashboard Salud de Equipos")

# ------------------------------------
# MEMORIA
# ------------------------------------

if "datos" not in st.session_state:
    st.session_state.datos = None

# ------------------------------------
# CARGAR EXCEL
# ------------------------------------

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

    st.success("✅ Archivo cargado correctamente")

# ------------------------------------
# DASHBOARD
# ------------------------------------

if st.session_state.datos is not None:

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
        color = "#28a745"

    elif salud >= 0.70:
        estado = "🟡 ALARMA"
        color = "#ffc107"

    else:
        estado = "🔴 INTERVENIR"
        color = "#dc3545"

    punto_critico = min(
        datos_equipo,
        key=lambda x: float(x[idx_estado])
    )

    col1, col2 = st.columns([1, 1])

    # -------------------------
    # DONA
    # -------------------------

    with col1:

        fig = go.Figure()

        fig.add_trace(
            go.Pie(
                values=[
                    salud * 100,
                    100 - (salud * 100)
                ],
                hole=0.75,
                marker=dict(
                    colors=[
                        color,
                        "#E0E0E0"
                    ]
                ),
                textinfo="none"
            )
        )

        fig.update_layout(
            showlegend=False,
            height=400,
            annotations=[
                dict(
                    text=f"{salud:.0%}",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font_size=40
                )
            ]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # -------------------------
    # INFORMACIÓN
    # -------------------------

    with col2:

        st.metric(
            "SALUD DEL EQUIPO",
            f"{salud:.0%}"
        )

        st.write("## Estado")
        st.write(estado)

        st.write("## Punto Más Crítico")
        st.write(
