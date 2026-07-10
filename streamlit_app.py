import streamlit as st
import openpyxl
from io import BytesIO

st.title("Prueba Lectura Hoja")

archivo = st.file_uploader(
    "Excel",
    type=["xlsx"]
)

if archivo:

    if st.button("INICIAR"):

        wb = openpyxl.load_workbook(
            BytesIO(archivo.read()),
            data_only=True
        )

        ws = wb["Datos"]

        st.success("✅ Hoja abierta")

        st.write("Filas:")

        datos = []

        for fila in ws.iter_rows(values_only=True):

            datos.append(fila)

        st.write(datos[:10])
