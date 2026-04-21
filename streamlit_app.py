import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

# --- FUNCIÓN DE LIMPIEZA TOTAL DE LLAVE ---
def fix_private_key(key):
    # Eliminar espacios en blanco accidentales al inicio/final
    key = key.strip()
    # Si la llave viene en una sola línea larga, le devolvemos sus saltos de línea
    if "-----BEGIN PRIVATE KEY-----" in key and "\n" not in key[26:-24]:
        header = "-----BEGIN PRIVATE KEY-----"
        footer = "-----END PRIVATE KEY-----"
        content = key.replace(header, "").replace(footer, "").replace(" ", "").replace("\n", "")
        # Google espera bloques de 64 caracteres por línea
        chunks = [content[i:i+64] for i in range(0, len(content), 64)]
        key = header + "\n" + "\n".join(chunks) + "\n" + footer
    return key

def get_gspread_client():
    scope = ["https://google.com", "https://googleapis.com"]
    
    # Extraer de [connections.gsheets]
    gs_secrets = st.secrets["connections"]["gsheets"]
    
    # Procesar la llave para que no de error de DECODER
    clean_key = fix_private_key(gs_secrets["private_key"])
    
    creds_dict = {
        "type": gs_secrets["type"],
        "project_id": gs_secrets["project_id"],
        "private_key_id": gs_secrets["private_key_id"],
        "private_key": clean_key,
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
            with st.spinner("Conectando con Google Sheets..."):
                client = get_gspread_client()
                url_sheet = st.secrets["connections"]["gsheets"]["spreadsheet"]
                spreadsheet = client.open_by_url(url_sheet)
                
                # SE ASUME QUE LA PESTAÑA SE LLAMA "BD"
                sheet = spreadsheet.worksheet("BD")
                
                # Calcular Item
                num_fila = len(sheet.get_all_values())
                
                # Fila: Item, Área, Ubicación, Equipo, Novedad, Propuesta, Prioridad, Comentario
                datos = [num_fila, area, ubicacion, equipo, novedad, propuesta, prioridad, comentario]
                
                sheet.append_row(datos)
                st.success(f"✅ ¡Registro #{num_fila} guardado con éxito!")
                st.balloons()
        except Exception as e:
            st.error(f"❌ Error de conexión: {str(e)}")
            st.info("Asegúrate de haber compartido el Excel con el correo: balanceo-unacem@enduring-range-371901.iam.gserviceaccount.com")
