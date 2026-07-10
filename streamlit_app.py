import streamlit as st
import openpyxl
from io import BytesIO

st.title("Prueba Lectura Workbook")

archivo = st.file_uploader(
    "Excel",
    type=["xlsx"]
)

if archivo:

    if st.button("INICIAR"):

        try:

            wb = openpyxl.load_workbook(
                BytesIO(archivo.read())
            )

            st.success("✅ Workbook abierto")

            st.write(wb.sheetnames)

        except Exception as e:

            st.error(e)
