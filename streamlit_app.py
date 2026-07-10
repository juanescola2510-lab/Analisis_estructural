import streamlit as st

st.title("Prueba Openpyxl")

if st.button("INICIAR"):

    try:

        import openpyxl

        st.success("✅ Openpyxl cargado correctamente")

    except Exception as e:

        st.error(e)
