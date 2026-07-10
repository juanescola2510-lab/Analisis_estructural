import streamlit as st
import pandas as pd

st.title("Prueba Lectura Excel")

archivo = st.file_uploader(
    "Selecciona un archivo Excel",
    type=["xlsx"]
)

if archivo is not None:

    if st.button("INICIAR"):

        try:

            df = pd.read_excel(
                archivo,
                engine="openpyxl"
            )

            st.success("✅ Excel leído correctamente")

            st.write("Columnas detectadas:")

            st.write(df.columns.tolist())

            st.write("Primeras filas:")

            st.dataframe(df.head())

        except Exception as e:

            st.error(f"Error al leer el Excel: {e}")
