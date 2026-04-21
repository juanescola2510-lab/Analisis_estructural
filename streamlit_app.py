import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_gspread_client():
    scope = ["https://google.com", "https://googleapis.com"]
    
    # 1. Extraemos los secretos del formato [connections.gsheets]
    # Usamos .get() para evitar errores si algo falta
    gs_secrets = st.secrets["connections"]["gsheets"]
    
    # 2. LIMPIEZA CRÍTICA DE LA LLAVE PRIVADA
    # El error 'unsupported' suele ser por espacios o saltos de línea mal formateados
    raw_key = gs_secrets["private_key"]
    
    # Reemplazamos saltos de línea literales y aseguramos el formato correcto
    clean_key = raw_key.replace("\\n", "\n")
    
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

st.set_page_config(page_title="Registro de Fugas UNACEM", page_icon="📝")
st.title("🚀 Reporte de Fugas - UNACEM")

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
            with st.spinner("Conectando y guardando..."):
                client = get_gspread_client()
                
                # Acceso directo por URL para evitar fallas de nombre
                url_sheet = st.secrets["connections"]["gsheets"]["spreadsheet"]
                spreadsheet = client.open_by_url(url_sheet)
                
                # IMPORTANTE: Asegúrate de que la pestaña se llame exactamente "BD"
                sheet = spreadsheet.worksheet("BD")
                
                # Calcular Item
                num_fila = len(sheet.get_all_values())
                
                # Fila: Item, Área, Ubicación, Equipo, Novedad, Propuesta, Prioridad, Comentario
                datos = [num_fila, area, ubicacion, equipo, novedad, propuesta, prioridad, comentario]
                
                sheet.append_row(datos)
                st.success(f"✅ ¡Registro #{num_fila} guardado exitosamente!")
                st.balloons()
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
