import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io

st.set_page_config(page_title="Actualizador TD", layout="centered")
st.title("📊 Sincronizador de Datos")

archivo_base = st.file_uploader("1. Sube archivo con 'TD' y 'HojaDeDatos'", type=['xlsx'])
archivo_datos = st.file_uploader("2. Sube archivo con hoja 'BD'", type=['xlsx'])

if st.button("🚀 Actualizar Información"):
    if archivo_base and archivo_datos:
        try:
            # 1. Leer los datos de la hoja 'BD' del segundo archivo
            df_fuente = pd.read_excel(archivo_datos, sheet_name='BD')

            # 2. Leer TODAS las hojas del primer archivo para no perder nada
            # Esto evita el error de visibilidad porque mantenemos todo en memoria
            excel_original = pd.ExcelFile(archivo_base)
            nombres_hojas = excel_original.sheet_names
            
            # 3. Crear el archivo de salida
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # Recorremos cada hoja que ya existía en tu archivo
                for nombre in nombres_hojas:
                    if nombre == "HojaDeDatos":
                        # Si es la hoja de datos, escribimos la información nueva (la de BD)
                        df_fuente.to_excel(writer, sheet_name=nombre, index=False)
                    else:
                        # Si es TD o cualquier otra, la copiamos tal cual estaba
                        # Nota: Las tablas dinámicas podrían requerir actualizarse manualmente al abrir
                        df_temp = pd.read_excel(archivo_base, sheet_name=nombre)
                        df_temp.to_excel(writer, sheet_name=nombre, index=False)

            st.success(f"✅ ¡Proceso terminado! Se sincronizaron {len(df_fuente)} filas.")
            
            st.download_button(
                label="📥 Descargar Reporte Actualizado",
                data=output.getvalue(),
                file_name="REPORTE_SINCRONIZADO.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"Ocurrió un detalle técnico: {e}")
    else:
        st.warning("Asegúrate de subir ambos archivos.")
