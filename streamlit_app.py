import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_gspread_client():
    scope = ["https://google.com", "https://googleapis.com"]
    
    # Extraemos de [connections.gsheets]
    gs_secrets = st.secrets["connections"]["gsheets"]
    
    # --- EL TRUCO DEFINITIVO PARA EL ERROR DE DECODER ---
    # Limpiamos cualquier espacio, comilla o salto de línea raro que tenga la llave
    key_raw = gs_secrets["private_key"].replace("\\n", "\n").strip()
    
    # Si la llave se pegó sin saltos de línea (como una línea larga), esto la arregla:
    if "-----BEGIN PRIVATE KEY-----" in key_raw and "\n" not in key_raw[26:-24]:
        header = "-----BEGIN PRIVATE KEY-----"
        footer = "-----END PRIVATE KEY-----"
        content = key_raw.replace(header, "").replace(footer, "").replace(" ", "").replace("\n", "")
        # Google necesita bloques de 64 caracteres por línea
        chunks = [content[i:i+64] for i in range(0, len(content), 64)]
        key_raw = header + "\n" + "\n".join(chunks) + "\n" + footer

    creds_dict = {
        "type": gs_secrets["type"],
        "project_id": gs_secrets["project_id"],
        "private_key_id": gs_secrets["private_key_id"],
        "private_key": key_raw, # <--- Llave reconstruida perfectamente
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
st.title("🚀 Registro de Fugas - UNACEM")

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
    submitted = st.form_submit_button("GUARDAR EN EXCEL")

if submitted:
    if not ubicacion or not novedad:
        st.warning("⚠️ Completa los campos obligatorios.")
    else:
        try:
            with st.spinner("Guardando..."):
                client = get_gspread_client()
                url_sheet = st.secrets["connections"]["gsheets"]["spreadsheet"]
                spreadsheet = client.open_by_url(url_sheet)
                
                # BUSCA LA PESTAÑA 'BD' (Asegúrate que se llame así)
                sheet = spreadsheet.worksheet("BD")
                
                # Calcular el Item (Número de fila)
                num_fila = len(sheet.get_all_values())
                
                # Datos en MAYÚSCULAS como pediste
                datos = [num_fila, area, ubicacion, equipo, novedad, propuesta, prioridad, comentario]
                
                sheet.append_row(datos)
                st.success(f"✅ ¡Registro #{num_fila} guardado exitosamente!")
                st.balloons()
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
