import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Función para limpiar la llave y evitar errores de Decoder/Token
def get_gspread_client():
    scope = ["https://google.com", "https://googleapis.com"]
    
    # Extraer secretos de la sección que ya tienes configurada
    gs_secrets = st.secrets["connections"]["gsheets"]
    
    # Limpieza manual de la llave privada
    private_key = gs_secrets["private_key"]
    if "-----BEGIN PRIVATE KEY-----" in private_key:
        # Si la llave tiene saltos de línea literales (\n), los convertimos
        private_key = private_key.replace("\\n", "\n")
    
    creds_dict = {
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
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

# --- INTERFAZ ---
st.set_page_config(page_title="Reporte Fugas UNACEM", layout="centered")
st.title("📝 Registro de Fugas - UNACEM")

with st.form("form_fugas", clear_on_submit=True):
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
        st.warning("⚠️ Completa los campos obligatorios.")
    else:
        try:
            with st.spinner("Enviando datos..."):
                client = get_gspread_client()
                
                # Abre por URL (la que tienes en tus secrets)
                url_sheet = st.secrets["connections"]["gsheets"]["spreadsheet"]
                spreadsheet = client.open_by_url(url_sheet)
                
                # Acceder a la pestaña BD
                sheet = spreadsheet.worksheet("BD")
                
                # Calcular el número de fila (Item)
                num_item = len(sheet.get_all_values())
                
                # Preparar datos
                datos = [num_item, area, ubicacion, equipo, novedad, propuesta, prioridad, comentario]
                
                # Escribir
                sheet.append_row(datos)
                
                st.success(f"✅ ¡Registro #{num_item} guardado con éxito!")
                st.balloons()
        except Exception as e:
            st.error(f"Error: {e}")
