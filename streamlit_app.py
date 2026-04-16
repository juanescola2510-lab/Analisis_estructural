import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io

st.set_page_config(page_title="Actualizador TABLA DINAMICA", layout="centered")

st.title("📊 Actualizador de Reporte")
st.write("Sube los archivos para actualizar la hoja **BaseDeDatos**.")

# 1. Carga de archivos
archivo_base = st.file_uploader("Subir archivo 'TABLA DINAMICA'", type=['xlsx'])
archivo_datos = st.file_uploader("Subir segundo archivo con hoja 'BD'", type=['xlsx'])
extra_1 = st.file_uploader("Subir Archivo Extra 1", type=['xlsx'])
extra_2 = st.file_uploader("Subir Archivo Extra 2", type=['xlsx'])

if st.button("🚀 Actualizar Base de Datos"):
    if all([archivo_base, archivo_datos, extra_1, extra_2]):
        try:
            # 2. Lectura específica de la hoja 'BD' del segundo archivo
            df_principal = pd.read_excel(archivo_datos, sheet_name='BD')
            df_e1 = pd.read_excel(extra_1)
            df_e2 = pd.read_excel(extra_2)

            # 3. Consolidación de los 3 orígenes
            df_consolidado = pd.concat([df_principal, df_e1, df_e2], ignore_index=True)

            # 4. Proceso de inyección en la hoja 'BaseDeDatos'
            output = io.BytesIO()
            book = load_workbook(archivo_base)
            
            # Si la hoja BaseDeDatos existe, la reemplazamos con la nueva data
            if "BaseDeDatos" in book.sheetnames:
                del book["BaseDeDatos"]
            
            # Usamos ExcelWriter para insertar el DataFrame consolidado
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                writer.book = book
                df_consolidado.to_excel(writer, sheet_name="BaseDeDatos", index=False)
            
            # 5. Botón de descarga
            st.success("✅ ¡Hoja 'BaseDeDatos' actualizada!")
            st.download_button(
                label="📥 Descargar TABLA DINAMICA Actualizada",
                data=output.getvalue(),
                file_name="TABLA_DINAMICA_ACTUALIZADA.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.info("💡 **Recuerda:** Al abrir el archivo, ve a la hoja de la Tabla Dinámica, haz clic derecho sobre ella y selecciona **'Actualizar'**.")

        except Exception as e:
            st.error(f"Error: Asegúrate de que el segundo archivo tenga una hoja llamada 'BD'. Detalles: {e}")
    else:
        st.warning("Por favor, sube todos los archivos para proceder.")
