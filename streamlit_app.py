import streamlit as st
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import io

st.set_page_config(page_title="Actualizador TD", layout="centered")
st.title("📊 Sincronizador de Datos Real")

archivo_base = st.file_uploader("1. Sube tu archivo con la Tabla Dinámica", type=['xlsx'])
archivo_datos = st.file_uploader("2. Sube el archivo con la hoja 'BD'", type=['xlsx'])

if st.button("🚀 Actualizar sin borrar TD"):
    if archivo_base and archivo_datos:
        try:
            # 1. Leer los datos nuevos
            df_nuevo = pd.read_excel(archivo_datos, sheet_name='BD')

            # 2. Cargar el libro original manteniendo estilos y objetos
            archivo_base.seek(0)
            book = load_workbook(io.BytesIO(archivo_base.read()))
            
            if "HojaDeDatos" in book.sheetnames:
                sheet = book["HojaDeDatos"]
                
                # 3. Limpiar solo los datos viejos (desde la fila 1 hasta el final)
                # Esto es mejor que borrar la hoja porque no rompe los links de la TD
                sheet.delete_rows(1, sheet.max_row + 1)
                
                # 4. Escribir los nuevos datos fila por fila
                for r in dataframe_to_rows(df_nuevo, index=False, header=True):
                    sheet.append(r)
                
                # 5. Guardar en memoria
                output = io.BytesIO()
                book.save(output)
                
                st.success("✅ ¡Base actualizada! La Tabla Dinámica sigue ahí.")
                st.download_button(
                    label="📥 Descargar Archivo con TD intacta",
                    data=output.getvalue(),
                    file_name="REPORTE_CON_TD.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.info("💡 **Importante:** Al abrirlo, ve a 'TD', clic derecho y 'Actualizar'.")
            else:
                st.error("No se encontró la pestaña 'HojaDeDatos'.")

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Sube ambos archivos.")
