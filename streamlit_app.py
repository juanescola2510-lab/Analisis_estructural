import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

def get_gspread_client():
    # 1. Extraer datos de st.secrets
    gs_secrets = st.secrets["connections"]["gsheets"]
    
    # 2. RECONSTRUCCIÓN CRÍTICA DE LA LLAVE (Soluciona el error de Token/Decoder)
    raw_key = gs_secrets["private_key"].strip()
    header = "-----BEGIN PRIVATE KEY-----"
    footer = "-----END PRIVATE KEY-----"
    
    # Extraemos solo el contenido base64 y eliminamos cualquier espacio o salto de línea previo
    content = raw_key.replace(header, "").replace(footer, "").replace(" ", "").replace("\n", "").replace("\r", "")
    
    # Google requiere líneas de 64 caracteres
    formatted_content = "\n".join([content[i:i+64] for i in range(0, len(content), 64)])
    
    # Ensamblamos la llave final con el formato correcto
    fixed_key = f"{header}\n{formatted_content}\n{footer}\n"

    # 3. Configurar credenciales
    scopes = ["https://googleapis.com", "https://googleapis.com"]
    creds_info = {
        "type": gs_secrets["type"],
        "project_id": gs_secrets["project_id"],
        "private_key_id": gs_secrets["private_key_id"],
        "private_key": fixed_key,
        "client_email": gs_secrets["client_email"],
        "client_id": gs_secrets["client_id"],
        "auth_uri": gs_secrets["auth_uri"],
        "token_uri": gs_secrets["token_uri"],
        "auth_provider_x509_cert_url": gs_secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": gs_secrets["client_x509_cert_url"]
    }
    
    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
    return gspread.authorize(creds)

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="UNACEM - Fugas", layout="centered")
st.title("🏭 Reporte de Fugas - UNACEM")

with st.form("form_fugas", clear_on_submit=True):
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
    enviar = st.form_submit_button("💾 GUARDAR EN EXCEL")

if enviar:
    if not ubicacion or not novedad:
        st.warning("⚠️ Los campos Ubicación y Hallazgo son obligatorios.")
    else:
        try:
            with st.spinner("Conectando con Google Sheets..."):
                client = get_gspread_client()
                # Abrir usando la URL de tus secretos
                url = st.secrets["connections"]["gsheets"]["spreadsheet"]
                sh = client.open_by_url(url)
                
                # Acceder a la pestaña (Verifica que se llame BD)
                try:
                    worksheet = sh.worksheet("BD")
                except:
                    worksheet = sh.get_worksheet(0) # Si falla, usa la primera pestaña
                
                # Calcular Item y guardar
                num_fila = len(worksheet.get_all_values())
                fila_datos = [num_fila, area, ubicacion, equipo, novedad, propuesta, prioridad, comentario]
                
                worksheet.append_row(fila_datos)
                st.success(f"✅ ¡Registro #{num_fila} guardado con éxito!")
                st.balloons()
        except Exception as e:
            st.error(f"❌ Error de acceso: {e}")
