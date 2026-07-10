import streamlit as st
import openpyxl
from io import BytesIO

st.set_page_config(
    page_title="Dashboard Salud Equipos",
    layout="wide"
)

st.title("⚙️ Dashboard Salud de Equipos")

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

        st.success("✅ Datos cargados")

        st.write("Columnas encontradas:")
        st.write(encabezados)

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
            float(fila[idx_estado])
            for fila in datos_equipo
        ) / len(datos_equipo)

        st.subheader("Estado General del Equipo")

        st.metric(
            label="Salud",
            value=f"{salud:.0%}"
        )

        if salud >= 0.9:
            st.success("🟢 NORMAL")

        elif salud >= 0.7:
            st.warning("🟡 ALARMA")

        else:
            st.error("🔴 INTERVENIR")

        peor = min(
            datos_equipo,
            key=lambda x: float(x[idx_estado])
        )

        st.subheader("Punto Más Crítico")

        st.write(
            peor[idx_punto]
        )

        st.subheader("Detalle")

        st.dataframe(datos_equipo)
