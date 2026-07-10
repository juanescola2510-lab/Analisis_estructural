import streamlit as st
import openpyxl
from io import BytesIO

st.set_page_config(
    page_title="Dashboard Salud Equipos",
    layout="wide"
)

st.title("⚙️ Dashboard Salud de Equipos")

# -------------------------------------------------
# MEMORIA
# -------------------------------------------------

if "datos" not in st.session_state:
    st.session_state.datos = None

# -------------------------------------------------
# CARGAR EXCEL
# -------------------------------------------------

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

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------

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
        sum(float(fila[idx_estado]) for fila in datos_equipo)
        / len(datos_equipo)
    )

    peor = min(
        datos_equipo,
        key=lambda x: float(x[idx_estado])
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "SALUD DEL EQUIPO",
            f"{salud:.0%}"
        )

    with c2:

        if salud >= 0.90:
            st.success("🟢 NORMAL")

        elif salud >= 0.70:
            st.warning("🟡 ALARMA")

        else:
            st.error("🔴 INTERVENIR")

    with c3:
        st.metric(
            "PUNTO MÁS CRÍTICO",
            peor[idx_punto]
        )

    st.subheader("Detalle del Equipo")

    for fila in datos_equipo:

        st.write(
            fila[idx_punto],
            "-",
            f"{float(fila[idx_estado]):.0%}"
        )
