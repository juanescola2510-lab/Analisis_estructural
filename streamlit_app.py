import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# --- FUNCIÓN DE CONEXIÓN ROBUSTA ---
def get_gspread_client():
    # Definir alcances
    scopes = [
        "https://googleapis.com",
        "https://googleapis.com"
    ]
    
    # Extraer de [connections.gsheets] de tus Secrets
    gs_secrets = st.secrets["connections"]["gsheets"]
    
    # Limpieza profunda de la llave privada
    private_key = gs_secrets["private_key"].replace("\\n", "\n")
    
    # Crear diccionario de credenciales
    creds_info = {
        "type": gs_secrets["type"],
        "project_id": gs_secrets["project_id"],
        "private_key_id": gs_secrets["private_key_id"],
        "private_key": private_key,
        "client_email": gs_secrets["client_email"],
        "client_id": gs_secrets["client_id"],
        "auth_uri": gs_secrets["auth_uri"],
        "token_uri": gs_secrets["token_uri"],
        "auth_provider_x509_cert_url": gs_secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": gs_secrets["client_x509_cert_url"]
    }
    
    # Autenticación con Google Auth
    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
    return gspread.authorize(creds)

# --- INTERFAZ ---
st.set_page_config(page_title="UNACEM - Registro", layout="centered")
st.title("📝 Registro de Fugas - UNACEM")

with st.form("form_registro", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        area = st.selectbox("ÁREA", ["PRETRITURACIÓN", "MOLIENDA", "HORNOS", "CRIBADO"])
        ubicacion = st.text_input("UBICACIÓN", placeholder="Ej: OTV-405-BC03")
        equipo = st.text_input("EQUIPO", value="BANDA TRANSPORTADORA")
    with col2:
        novedad = st.text_area("HALLAZGO / FUGA")
        propuesta = st.text_area("PROPUESTA TÉCNICA")
        prioridad = st.selectbox("PRIORIDAD", ["1", "2", "3"])
    
    comentario = st.text_input("COMENTARIO ADICIONAL")
    enviar = st.form_submit_button("GUARDAR EN EXCEL")

if enviar:
    if not ubicacion or not novedad:
        st.warning("⚠️ Completa los campos obligatorios.")
    else:
        try:
            with st.spinner("Conectando con Google..."):
                client = get_gspread_client()
                # Abrir por URL (la que tienes en tus secrets)
                url = st.secrets["connections"]["gsheets"]["spreadsheet"]
                sh = client.open_by_url(url)
                # Seleccionar pestaña "BD"
                worksheet = sh.worksheet("BD")
                
                # Calcular Item (Número de fila)
                num_fila = len(worksheet.get_all_values())
                
                # Datos
                fila_datos = [num_fila, area, ubicacion, equipo, novedad, propuesta, prioridad, comentario]
                
                worksheet.append_row(fila_datos)
                st.success(f"✅ ¡Registro #{num_fila} guardado exitosamente!")
                st.balloons()
        except Exception as e:
            st.error(f"❌ Error de autenticación: {e}")
            st.info("Revisa que la 'private_key' en Secrets no tenga espacios extra al inicio.")
