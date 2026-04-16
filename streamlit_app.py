import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io

st.set_page_config(page_title="Actualizador TD", layout="centered")
st.title("📊 Actualizador de Reporte Excel")

# 1. Carga de archivos
archivo_base = st.file_uploader("1. Sube tu archivo con pestañas 'TD' y 'HojaDeDatos'", type=['xlsx'])
archivo_datos = st.file_uploader("2. Sube el archivo que tiene la hoja 'BD'", type=['xlsx'])

if st.button("🚀 Sincronizar Datos"):
    if archivo_base and archivo_datos:
        try:
            # 2. Leer los datos nuevos de la hoja 'BD'
            df_actualizado = pd.read_excel(archivo_datos, sheet_name='BD')

            # 3. Cargar el Excel original (el de la imagen)
            archivo_base.seek(0)
            book = load_workbook(io.BytesIO(archivo_base.read()))
            
            # Verificamos que la hoja de destino exista
            if "HojaDeDatos" not in book.sheetnames:
                st.error("❌ No encontré la pestaña 'HojaDeDatos' en el primer archivo.")
                st.stop()
            
            sheet = book["HojaDeDatos"]
            
            # 4. Limpiar contenido viejo celda por celda (mantiene la hoja visible)
            for row in sheet.iter_rows():
                for cell in row:
                    cell.value = None

            # 5. Escribir la nueva data sobre 'HojaDeDatos'
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                writer.book = book
                writer.sheets = {ws.title: ws for ws in book.worksheets}
                df_actualizado.to_excel(writer, sheet_name="HojaDeDatos", index=False)
            
            st.success(f"✅ ¡Completado! Se cargaron {len(df_actualizado)} filas en la pestaña 'HojaDeDatos'.")
            
            # 6. Botón de descarga
            st.download_button(
                label="📥 Descargar Excel Actualizado",
                data=output.getvalue(),
                file_name="REPORTE_ACTUALIZADO.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.warning("⚠️ **Paso final:** Abre el archivo, ve a la pestaña 'TD' y dale clic derecho a la tabla -> **Actualizar**.")

        except Exception as e:
            st.error(f"❌ Error: {e}")
    else:
        st.warning("Por favor, sube ambos archivos para continuar.")
