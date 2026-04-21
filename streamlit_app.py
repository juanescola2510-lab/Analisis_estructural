import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- FUNCIÓN PARA CONECTAR A GOOGLE SHEETS ---
def get_gspread_client():
    # Definir el alcance
    scope = ["https://google.com", "https://googleapis.com"]
    
    # Extraer los datos de la sección [connections.gsheets] que pasaste
    creds_dict = {
        "type": st.secrets["connections"]["gsheets"]["type"],
        "project_id": st.secrets["connections"]["gsheets"]["project_id"],
        "private_key_id": st.secrets["connections"]["gsheets"]["private_key_id"],
        "private_key": st.secrets["connections"]["gsheets"]["private_key"],
        "client_email": st.secrets["connections"]["gsheets"]["client_email"],
        "client_id": st.secrets["connections"]["gsheets"]["client_id"],
        "auth_uri": st.secrets["connections"]["gsheets"]["auth_uri"],
        "token_uri": st.secrets["connections"]["gsheets"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["connections"]["gsheets"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["connections"]["gsheets"]["client_x509_cert_url"]
    }
    
    # Limpiar saltos de línea en la llave privada si fuera necesario
    if "\\n" in creds_dict["private_key"]:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

# --- INTERFAZ DE USUARIO ---
st.set_page_config(page_title="Registro de Fugas", page_icon="📋")
st.title("📝 Reporte de Fugas - UNACEM")

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

# --- LÓGICA DE ENVÍO ---
if submitted:
    if not ubicacion or not novedad:
        st.warning("⚠️ Completa los campos obligatorios (Ubicación y Hallazgo).")
    else:
        try:
            with st.spinner("Registrando..."):
                client = get_gspread_client()
                
                # Usamos la URL que pasaste en tus secretos
                url_sheet = st.secrets["connections"]["gsheets"]["spreadsheet"]
                spreadsheet = client.open_by_url(url_sheet)
                
                # Se asume que la pestaña se llama "BD" según tus imágenes previas
                sheet = spreadsheet.worksheet("BD")
                
                # Calcular número de Item
                num_fila = len(sheet.get_all_values())
                
                # Fila: Item, Área, Ubicación, Equipo, Novedad, Propuesta, Prioridad, Comentario
                datos = [num_fila, area, ubicacion, equipo, novedad, propuesta, prioridad, comentario]
                
                sheet.append_row(datos)
                st.success(f"✅ ¡Registro #{num_fila} guardado con éxito!")
                st.balloons()
        except Exception as e:
            st.error(f"❌ Error: {e}")
