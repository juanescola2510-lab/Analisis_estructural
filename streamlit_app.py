import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Reporte Fugas UNACEM", layout="centered")
st.title("📝 Registro de Fugas - UNACEM")

# --- CONEXIÓN NATIVA ---
try:
    # Esta función lee automáticamente la sección [connections.gsheets] de tus Secrets
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Error configurando la conexión: {e}")

# --- FORMULARIO ---
with st.form("main_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        area = st.selectbox("Área", ["Pretrituración", "Molienda", "Hornos", "Cribado"])
        ubicacion = st.text_input("Ubicación", placeholder="Ej: OTV-405-BC03")
        equipo = st.text_input("Equipo", value="Banda transportadora")
    with col2:
        novedad = st.text_area("Hallazgo / Fuga")
        propuesta = st.text_area("Propuesta Técnica")
        prioridad = st.selectbox("Prioridad", ["1", "2", "3"])
    
    comentario = st.text_input("Comentario Adicional")
    submitted = st.form_submit_button("GUARDAR EN EXCEL")

if submitted:
    if not ubicacion or not novedad:
        st.warning("⚠️ Completa los campos de Ubicación y Hallazgo.")
    else:
        try:
            with st.spinner("Guardando reporte..."):
                # 1. Leer los datos actuales de la pestaña "BD"
                # Usamos la URL que está en tus secrets
                existing_data = conn.read(worksheet="BD", usecols=list(range(8)))
                
                # 2. Crear el nuevo registro
                num_fila = len(existing_data) + 1
                new_entry = pd.DataFrame([{
                    "ITEM": num_fila,
                    "ÁREA": area,
                    "UBICACIÓN": ubicacion,
                    "EQUIPO": equipo,
                    "NOVEDAD": novedad,
                    "PROPUESTA": propuesta,
                    "PRIORIDAD": prioridad,
                    "COMENTARIO": comentario
                }])
                
                # 3. Concatenar y actualizar la hoja
                updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
                conn.update(worksheet="BD", data=updated_df)
                
                st.success(f"✅ ¡Registro #{num_fila} guardado con éxito!")
                st.balloons()
        except Exception as e:
            st.error(f"❌ Error al guardar: {str(e)}")
            st.info("Verifica que la pestaña del Excel se llame exactamente 'BD'.")
