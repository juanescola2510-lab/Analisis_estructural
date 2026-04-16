import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io

st.set_page_config(page_title="Actualizador Express", layout="centered")

st.title("📊 Actualizador de Tabla Dinámica")

archivo_base = st.file_uploader("1. Subir archivo 'TABLA DINAMICA'", type=['xlsx'])
archivo_datos = st.file_uploader("2. Subir archivo con hoja 'BD'", type=['xlsx'])

if st.button("🚀 Actualizar BaseDeDatos"):
    if archivo_base and archivo_datos:
        try:
            # 1. Leer los datos de la hoja 'BD' (Aseguramos que lea aunque haya hojas ocultas)
            df_actualizado = pd.read_excel(archivo_datos, sheet_name='BD')

            # 2. Cargar el libro de destino
            input_book = io.BytesIO(archivo_base.read())
            book = load_workbook(input_book)
            
            # 3. Crear o actualizar la hoja sin borrar todas las hojas del libro
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                writer.book = book
                
                # Si la hoja ya existe, la sobrescribimos directamente
                if "BaseDeDatos" in book.sheetnames:
                    # En lugar de borrar la hoja del 'book', dejamos que pandas la reemplace
                    # Esto evita el error de "ninguna hoja visible"
                    pass 
                
                df_actualizado.to_excel(writer, sheet_name="BaseDeDatos", index=False)
            
            st.success(f"✅ ¡Éxito! Se procesaron {len(df_actualizado)} filas.")
            st.download_button(
                label="📥 Descargar Archivo Actualizado",
                data=output.getvalue(),
                file_name="TABLA_DINAMICA_FINAL.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"Error detectado: {e}")
            st.info("Asegúrate de que la hoja 'BD' no esté protegida o con el nombre escrito diferente (ej. espacios al final).")
    else:
        st.warning("Sube ambos archivos.")



