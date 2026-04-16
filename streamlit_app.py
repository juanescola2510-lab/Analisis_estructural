import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io

st.set_page_config(page_title="Actualizador de Tablas Dinámicas", layout="centered")

st.title("📊 Procesador de Datos para Excel")
st.write("Sube tus archivos para consolidar la base de la tabla dinámica.")

# 1. Carga de archivos en el Sidebar
st.sidebar.header("Carga de Archivos")
archivo_base = st.sidebar.file_uploader("Subir Excel con Tabla Dinámica", type=['xlsx'])
datos_nuevos = st.sidebar.file_uploader("Subir Tabla de Datos Principal", type=['xlsx'])
extra_1 = st.sidebar.file_uploader("Subir Archivo Extra 1", type=['xlsx'])
extra_2 = st.sidebar.file_uploader("Subir Archivo Extra 2", type=['xlsx'])

if st.button("🚀 Procesar y Generar Reporte"):
    if all([archivo_base, datos_nuevos, extra_1, extra_2]):
        try:
            # 2. Lectura de datos con Pandas
            df_datos = pd.read_excel(datos_nuevos)
            df_e1 = pd.read_excel(extra_1)
            df_e2 = pd.read_excel(extra_2)

            # 3. Consolidación (ajusta el tipo de unión según necesites)
            # Aquí asumimos que se pegan uno debajo del otro (mismas columnas)
            df_consolidado = pd.concat([df_datos, df_e1, df_e2], ignore_index=True)

            # 4. Inyectar datos en el Excel original sin romper la Tabla Dinámica
            # Leemos el archivo base en memoria
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                # Cargamos el libro original para no perder la tabla dinámica
                writer.book = load_workbook(archivo_base)
                
                # IMPORTANTE: El nombre de la hoja debe ser el mismo que usa la Tabla Dinámica
                nombre_hoja_datos = "HojaDeDatos" 
                
                # Si la hoja ya existe, la eliminamos para escribir los nuevos datos
                if nombre_hoja_datos in writer.book.sheetnames:
                    std = writer.book[nombre_hoja_datos]
                    writer.book.remove(std)
                
                df_consolidado.to_excel(writer, sheet_name=nombre_hoja_datos, index=False)
            
            # Preparar descarga
            st.success("✅ ¡Datos consolidados con éxito!")
            st.download_button(
                label="📥 Descargar Excel Actualizado",
                data=buffer.getvalue(),
                file_name="Reporte_Actualizado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.info("⚠️ **Nota:** Al abrir el archivo, Excel te pedirá actualizar. Haz clic en 'Datos > Actualizar todo' para que la Tabla Dinámica lea los nuevos datos.")

        except Exception as e:
            st.error(f"Hubo un error: {e}")
    else:
        st.warning("Por favor, sube todos los archivos requeridos.")
