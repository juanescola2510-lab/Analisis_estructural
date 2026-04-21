import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os

# --- CONFIGURACIÓN DE CREDENCIALES ---
def get_gspread_client():
    scope = ["https://google.com", "https://googleapis.com"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("secretos.json", scope)
    return gspread.authorize(creds)

def upload_to_drive(file_bytes, file_name):
    # Configuración simple de PyDrive para subir a una carpeta específica
    gauth = GoogleAuth()
    # Usamos las mismas credenciales de cuenta de servicio
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name("secretos.json", 
                        ["https://googleapis.com"])
    drive = GoogleDrive(gauth)
    
    # Crea el archivo en la carpeta (reemplaza FOLDER_ID por el ID de tu carpeta en Drive)
    folder_id = "TU_ID_DE_CARPETA_DE_GOOGLE_DRIVE" 
    file_drive = drive.CreateFile({'title': file_name, 'parents': [{'id': folder_id}]})
    
    # Guardar temporalmente para subir
    with open("temp.png", "wb") as f:
        f.write(file_bytes)
    
    file_drive.SetContentFile("temp.png")
    file_drive.Upload()
    
    # Hacer el archivo público para que el Excel lo vea (Opcional)
    file_drive.InsertPermission({'type': 'anyone', 'value': 'anyone', 'role': 'reader'})
    
    return file_drive['webContentLink'] # Retorna link directo

# --- INTERFAZ STREAMLIT ---
st.title("🚀 Reporte de Fugas en Campo")

# Campo de Cámara
foto = st.camera_input("Tomar foto de la fuga")

with st.form("formulario_fugas"):
    area = st.selectbox("Área", ["Pretrituración", "Molienda"])
    ubicacion = st.text_input("Ubicación", placeholder="Ej: OTV-405-BC03")
    novedad = st.text_area("Novedad")
    prioridad = st.selectbox("Prioridad", [1, 2, 3])
    
    enviar = st.form_submit_button("Subir Reporte Completo")

if enviar:
    if foto is not None:
        try:
            with st.spinner("Subiendo imagen y datos..."):
                # 1. Subir Foto a Drive
                nombre_foto = f"fuga_{ubicacion}.png"
                link_foto = upload_to_drive(foto.getvalue(), nombre_foto)
                
                # 2. Conectar a Excel
                client = get_gspread_client()
                sheet = client.open("INFORME FUGAS").worksheet("BD")
                
                # 3. Preparar Fila (Columna I con fórmula de imagen)
                num_items = len(sheet.get_all_values())
                formula_imagen = f'=IMAGE("{link_foto}")'
                
                fila = [num_items, area, ubicacion, "Banda transportadora", 
                        novedad, "Revisar sistema", prioridad, "", formula_imagen]
                
                sheet.append_row(fila, value_input_option='USER_ENTERED')
                
                st.success("✅ ¡Reporte enviado con éxito!")
                st.balloons()
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("⚠️ Por favor, toma una foto antes de enviar.")
