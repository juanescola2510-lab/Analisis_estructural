import streamlit as st
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import io

st.set_page_config(page_title="Sincronizador Inteligente", layout="centered")
st.title("📊 Actualizador de Reporte y Porcentajes")

# 1. Carga de archivos
archivo_base = st.file_uploader("1. Archivo Principal (TD, HojaDeDatos, RT)", type=['xlsx'])
archivo_datos = st.file_uploader("2. Archivo con hoja 'BD'", type=['xlsx'])
archivo_porcentaje = st.file_uploader("3. Archivo con hoja 'porcentaje'", type=['xlsx'])

if st.button("🚀 Iniciar Actualización"):
    if all([archivo_base, archivo_datos, archivo_porcentaje]):
        try:
            # --- PROCESO 1: DATOS PARA HOJADEDATOS ---
            df_bd = pd.read_excel(archivo_datos, sheet_name='BD')
            
            # --- PROCESO 2: DATOS PARA HOJA RT ---
            df_porcentajes_nuevos = pd.read_excel(archivo_porcentaje, sheet_name='porcentaje')
            
            # Aseguramos que las columnas no tengan espacios extra
            df_porcentajes_nuevos.columns = df_porcentajes_nuevos.columns.str.strip()

            # Cargamos el libro original en memoria
            archivo_base.seek(0)
            book = load_workbook(io.BytesIO(archivo_base.read()))
            
            # ACTUALIZACIÓN DE HOJADEDATOS
            if "HojaDeDatos" in book.sheetnames:
                sheet_db = book["HojaDeDatos"]
                sheet_db.delete_rows(1, sheet_db.max_row + 1)
                for r in dataframe_to_rows(df_bd, index=False, header=True):
                    sheet_db.append(r)
            
            # ACTUALIZACIÓN DE HOJA RT CON CRUCE INTELIGENTE
            if "RT" in book.sheetnames:
                sheet_rt = book["RT"]
                
                # Leemos lo que hay actualmente en RT
                data_rt = list(sheet_rt.values)
                if len(data_rt) > 0:
                    cols = data_rt[0]
                    df_rt_actual = pd.DataFrame(data_rt[1:], columns=cols)
                else:
                    df_rt_actual = pd.DataFrame(columns=['nombre', 'porcentaje'])

                # Limpieza de nombres para comparar sin errores
                df_rt_actual['nombre'] = df_rt_actual['nombre'].astype(str).str.strip()
                df_porcentajes_nuevos['nombre'] = df_porcentajes_nuevos['nombre'].astype(str).str.strip()

                # CRUCE (Outer Join): 
                # 1. Actualiza si existe. 
                # 2. Agrega si el nombre es nuevo.
                df_rt_final = pd.merge(
                    df_rt_actual.drop(columns=['porcentaje'], errors='ignore'), 
                    df_porcentajes_nuevos[['nombre', 'porcentaje']], 
                    on='nombre', 
                    how='outer'
                )

                # Limpiamos la hoja RT y escribimos el resultado final
                sheet_rt.delete_rows(1, sheet_rt.max_row + 1)
                for r in dataframe_to_rows(df_rt_final, index=False, header=True):
                    sheet_rt.append(r)
            
            # 3. Guardar y Descargar
            output = io.BytesIO()
            book.save(output)
            
            st.success("✅ ¡Sincronización completa! Se actualizaron datos y se añadieron nombres nuevos en RT.")
            st.download_button(
                label="📥 Descargar Reporte Final",
                data=output.getvalue(),
                file_name="REPORTE_SISTEMA_COMPLETO.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"Error técnico: {e}")
    else:
        st.warning("Faltan archivos por subir.")
