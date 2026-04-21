import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN DE CONEXIÓN ---
def get_gspread_client():
    # Definir el alcance (scope) para Google Sheets y Drive
    scope = ["https://google.com", "https://googleapis.com"]
    
    # Cargar credenciales desde los Secrets de Streamlit Cloud
    # Asegúrate de haber pegado tu JSON en el panel de Settings -> Secrets
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # Corregir el formato de la llave privada (necesario para Streamlit Cloud)
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

# --- INTERFAZ DE USUARIO ---
st.set_page_config(page_title="Registro de Fugas", page_icon="📋")
st.title("📝 Reporte de Fugas - Pretrituración")
st.markdown("---")

# Formulario de entrada de datos
with st.form("formulario_fugas", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        area = st.selectbox("Área", ["Pretrituración", "Molienda", "Hornos", "Cribado"])
        ubicacion = st.text_input("Ubicación", placeholder="Ej: OTV-405-BC03")
        equipo = st.text_input("Equipo", value="Banda transportadora")
        prioridad = st.selectbox("Prioridad", ["1", "2", "3"])
    
    with col2:
        novedad = st.text_area("Novedad / Hallazgo (Fuga)")
        propuesta = st.text_area("Propuesta Técnica")
        comentario = st.text_input("Comentario Adicional")

    # Botón de registro
    submitted = st.form_submit_button("REGISTRAR EN GOOGLE SHEETS")

# --- LÓGICA DE PROCESAMIENTO ---
if submitted:
    if not ubicacion or not novedad:
        st.warning("⚠️ Los campos 'Ubicación' y 'Novedad' son obligatorios.")
    else:
        try:
            with st.spinner("Conectando con Google Sheets..."):
                client = get_gspread_client()
                
                # ABRE EL EXCEL: Asegúrate que el nombre sea EXACTO al de tu Drive
                # IMPORTANTE: Comparte el Excel con el email de tu cuenta de servicio
                spreadsheet = client.open("INFORME FUGAS")
                sheet = spreadsheet.worksheet("BD")
                
                # Calcular el siguiente número de ITEM (fila)
                # get_all_values trae todas las filas, restamos encabezados si es necesario
                num_items = len(sheet.get_all_values())
                
                # Preparar la fila (Columnas: Item, Área, Ubicación, Equipo, Novedad, Propuesta, Prioridad, Comentario)
                nueva_fila = [
                    num_items, area, ubicacion, equipo, 
                    novedad, propuesta, prioridad, comentario
                ]
                
                # Escribir en la hoja
                sheet.append_row(nueva_fila)
                
                st.success(f"✅ ¡Registro #{num_items} guardado exitosamente!")
                st.balloons()
                
        except Exception as e:
            st.error(f"❌ Error al guardar: {e}")
            st.info("Revisa si compartiste el Excel con el correo de la cuenta de servicio.")
