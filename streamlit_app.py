import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import tempfile

# --- CONFIGURACIÓN DE CONEXIÓN ---
def get_creds():
    # Definir el alcance (scope)
    scope = ["https://google.com", "https://googleapis.com"]
    
    # CARGA DESDE SECRETS (Paso 1)
    creds_dict = dict(st.secrets["gcp_service_account"])
    # Corregir problema de saltos de línea en la llave privada
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

def upload_to_drive(file_bytes, file_name):
    creds = get_creds()
    gauth = GoogleAuth()
    gauth.credentials = creds
    drive = GoogleDrive(gauth)
    
    # ID de tu carpeta en Google Drive (Cópialo de la URL de tu carpeta)
    folder_id = "TU_ID_DE_CARPETA_AQUÍ" 
    
    # Crear archivo temporal para la subida
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name

    file_drive = drive.CreateFile({'title': file_name, 'parents': [{'id': folder_id}]})
    file_drive.SetContentFile(temp_path)
    file_drive.Upload()
    
    # Dar permisos de lectura para que la fórmula =IMAGE() funcione
    file_drive.InsertPermission({'type': 'anyone', 'value': 'anyone', 'role': 'reader'})
    
    return file_drive['webContentLink']

# --- INTERFAZ DE USUARIO ---
st.set_page_config(page_title="Reporte de Fugas", page_icon="🏭")
st.title("🚀 Informe de Fugas - Pretrituración")

# 1. Captura de Imagen
foto = st.camera_input("Capturar evidencia de la fuga")

# 2. Formulario de Datos
with st.form("form_registro"):
    col1, col2 = st.columns(2)
    
    with col1:
        area = st.selectbox("Área", ["Pretrituración", "Molienda", "Hornos"])
        ubicacion = st.text_input("Ubicación", placeholder="Ej: OTV-405-BC03")
        equipo = st.text_input("Equipo", value="Banda transportadora")
        prioridad = st.selectbox("Prioridad", ["1 (Alta)", "2 (Media)", "3 (Baja)"])
    
    with col2:
        novedad = st.text_area("Novedad / Hallazgo")
        propuesta = st.text_area("Propuesta Técnica")
        comentario = st.text_input("Comentario")

    enviar = st.form_submit_button("SUBIR REPORTE COMPLETO")

# 3. Lógica de Envío
if enviar:
    if foto is None:
        st.error("⚠️ Error: Debes capturar una foto antes de enviar.")
    else:
        try:
            with st.spinner("Procesando reporte..."):
                # Subir imagen a Drive
                nombre_img = f"fuga_{ubicacion}.png"
                link_img = upload_to_drive(foto.getvalue(), nombre_img)
                
                # Conectar a Google Sheets
                creds = get_creds()
                client = gspread.authorize(creds)
                # Asegúrate de que el nombre del Excel coincida exactamente
                sheet = client.open("INFORME FUGAS").worksheet("BD")
                
                # Obtener número de fila
                num_item = len(sheet.get_all_values())
                
                # Preparar fórmula de imagen para Excel
                formula_excel = f'=IMAGE("{link_img}")'
                
                # Armar la fila según tu estructura (Item, Área, Ubicación, Equipo, Novedad, Propuesta, Prioridad, Comentario, Imagen)
                fila = [num_item, area, ubicacion, equipo, novedad, propuesta, prioridad[0], comentario, formula_excel]
                
                sheet.append_row(fila, value_input_option='USER_ENTERED')
                
                st.success(f"✅ Reporte #{num_item} guardado en Excel exitosamente.")
                st.balloons()
                
        except Exception as e:
            st.error(f"❌ Error crítico: {e}")
