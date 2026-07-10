import streamlit as st
import pandas as pd

st.title("Prueba")

archivo = st.file_uploader(
    "Sube Excel",
    type=["xlsx"]
)

if archivo is not None:

    df = pd.read_excel(
        archivo,
        engine="openpyxl"
    )

    st.write(df.head())
