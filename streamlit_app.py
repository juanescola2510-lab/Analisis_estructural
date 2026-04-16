import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io

st.set_page_config(page_title="Actualizador Express", layout="centered")

st.title("📊 Actualizador de Tabla Dinámica")
st.write("Sube los dos archivos para sincronizar la información.")

# 1. Carga de los dos archivos únicos
archivo_base = st.file_uploader("1. Subir archivo 'TABLA DINAMICA'", type=['xlsx'])
archivo_datos = st.file_uploader("2. Subir archivo con hoja 'BD'", type=['xlsx'])

if st.button("🚀 Actualizar BaseDeDatos"):
    if archivo_base and archivo_datos:
        try:
            # 2. Leer los datos de la hoja 'BD'
            df_actualizado = pd.read_excel(archivo_datos, sheet_name='BD')

            # 3. Preparar el archivo de destino en memoria
            output = io.BytesIO()
            book = load_workbook(archivo_base)
            
            # Borrar la hoja antigua 'BaseDeDatos' para insertar la nueva
            if "BaseDeDatos" in book.sheetnames:
                del book["BaseDeDatos"]
            
            # Escribir el nuevo contenido manteniendo la hoja de la Tabla Dinámica intacta
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                writer.book = book
                df_actualizado.to_excel(writer, sheet_name="BaseDeDatos", index=False)
            
            # 4. Resultado y Descarga
            st.success("✅ ¡Datos transferidos con éxito!")
            st.download_button(
                label="📥 Descargar Archivo Actualizado",
                data=output.getvalue(),
                file_name="TABLA_DINAMICA_FINAL.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"Error: Verifica que el segundo archivo tenga la hoja 'BD'. {e}")
    else:
        st.warning("Por favor, sube ambos archivos para continuar.")
