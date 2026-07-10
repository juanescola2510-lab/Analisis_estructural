import streamlit as st

st.title("Prueba Excel")

archivo = st.file_uploader(
    "Seleccione un Excel",
    type=["xlsx"]
)

if archivo is not None:

    st.success("✅ Archivo cargado")

    st.write("Nombre:", archivo.name)
    st.write("Tamaño:", archivo.size)

    if st.button("INICIAR"):

        contenido = archivo.read()

        st.success("✅ Contenido leído")

        st.write("Bytes leídos:")

        st.write(len(contenido))
