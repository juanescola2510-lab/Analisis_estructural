import streamlit as st
import openpyxl
from io import BytesIO

st.title("Dashboard Salud Equipos")

archivo = st.file_uploader(
    "Seleccione Excel",
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

        encabezados = datos[0]

        registros = datos[1:]

        st.success("✅ Datos cargados")

        st.write("Encabezados:")

        st.write(encabezados)

        st.write("Primeras filas:")

        st.write(registros[:10])
