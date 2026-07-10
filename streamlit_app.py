import streamlit as st

st.title("Prueba Excel")

archivo = st.file_uploader(
    "Seleccione un Excel",
    type=["xlsx"]
)

if archivo is not None:

    st.success("✅ Archivo cargado")

    st.write("Nombre:")

    st.write(archivo.name)

    st.write("Tamaño:")

    st.write(archivo.size)
