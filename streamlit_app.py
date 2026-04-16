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
            # 1. Leer los datos nuevos de 'BD'
            df_actualizado = pd.read_excel(archivo_datos, sheet_name='BD')

            # 2. Cargar el libro original en memoria
            archivo_base.seek(0) # Resetear puntero de lectura
            book = load_workbook(io.BytesIO(archivo_base.read()))
            
            # 3. Verificar si la hoja existe, si no, crearla
            if "BaseDeDatos" not in book.sheetnames:
                book.create_sheet("BaseDeDatos")
            
            sheet = book["BaseDeDatos"]
            
            # 4. LIMPIAR la hoja existente sin borrarla del libro
            # Esto evita el error de "At least one sheet must be visible"
            for row in sheet.iter_rows():
                for cell in row:
                    cell.value = None

            # 5. Escribir los nuevos datos usando ExcelWriter sobre el libro cargado
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                writer.book = book
                # Indicamos que use la hoja existente
                writer.sheets = {ws.title: ws for ws in book.worksheets}
                df_actualizado.to_excel(writer, sheet_name="BaseDeDatos", index=False)
            
            st.success(f"✅ ¡Hecho! Se cargaron {len(df_actualizado)} filas en 'BaseDeDatos'.")
            st.download_button(
                label="📥 Descargar Archivo Actualizado",
                data=output.getvalue(),
                file_name="TABLA_DINAMICA_FINAL.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except ValueError:
            st.error("❌ No encontré la hoja llamada 'BD' en el segundo archivo.")
        except Exception as e:
            st.error(f"❌ Error inesperado: {e}")
    else:
        st.warning("Por favor, sube ambos archivos.")
