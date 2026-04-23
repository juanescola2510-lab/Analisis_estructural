import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

# Configuración de página
st.set_page_config(page_title="Simulador de Succión Pro", layout="wide")

st.title("🌪️ Ingeniería de Succión y Capacidad de Sistema")
st.markdown("---")

# --- BARRA LATERAL ---
st.sidebar.header("📊 Configuración del Sistema")

with st.sidebar.expander("Ventilador y Entorno", expanded=True):
    cfm_entrada = st.sidebar.number_input("Caudal Nominal (CFM)", value=7600)
    sp_ventilador = st.sidebar.number_input("Presión Estática de Placa (in H2O)", value=10.0)
    eficiencia_fan = st.sidebar.slider("Eficiencia del Ventilador (%)", 40, 90, 65) / 100
    altitud = st.sidebar.number_input("Altitud del Sitio (msnm)", value=2500)
    v_diseno = st.sidebar.slider("Velocidad de Transporte (m/s)", 10, 35, 20)

with st.sidebar.expander("Filtro de Mangas"):
    n_mangas_act = st.number_input("Número de Mangas Instaladas", value=120)
    diam_manga = st.number_input("Diámetro Manga (mm)", value=120)
    largo_manga = st.number_input("Largo Manga (mm)", value=2115)
    dp_filtro = st.number_input("DP del Filtro (in H2O)", value=4.0)

with st.sidebar.expander("Red de Ductos y Energía"):
    materiales = {
        "Acero Galvanizado": 0.00015,
        "PVC / Plástico": 0.0000015,
        "Acero Inoxidable": 0.000045,
        "Ducto Flexible": 0.003
    }
    tipo_mat = st.selectbox("Material", list(materiales.keys()))
    long_ducto_ppal = st.number_input("Longitud Ducto Principal (m)", value=20.0)
    n_codos_ppal = st.number_input("Codos en Línea Principal", value=2)
    
    st.markdown("---")
    st.markdown("**Configuración de Ramales**")
    n_ramales = st.number_input("Número de Ramales", value=2)
    diam_ramal_mm = st.number_input("Diámetro de Ramales (mm)", value=200)
    long_ramal_m = st.number_input("Longitud por Ramal (m)", value=3.0)
    codos_por_ramal = st.number_input("Codos por cada Ramal", value=1)
    
    tipo_codo = st.radio("Tipo de Codo", ["Radio Corto (R=1D)", "Radio Largo (R=2.5D)"])
    
    st.markdown("---")
    horas_uso = st.number_input("Horas de uso al día", value=8)
    costo_kwh = st.number_input("Costo kWh (USD)", value=0.09)

# --- LÓGICA DE CÁLCULO ---

# 1. Propiedades del Aire
densidad_aire = 1.225 * math.exp(-altitud / 8500)
viscosidad = 1.5e-5

# 2. Caudales
area_un_ramal = math.pi * (diam_ramal_mm / 1000)**2 / 4
caudal_total_ramales = n_ramales * (area_un_ramal * v_diseno * 3600)
caudal_total = max(cfm_entrada * 1.699, caudal_total_ramales)
cfm_total = caudal_total / 1.699

# Diámetro Principal Sugerido
area_req_ppal = (caudal_total / 3600) / v_diseno
d_m_ppal = math.sqrt(4 * area_req_ppal / math.pi)

# 3. Longitudes Equivalentes (Cálculo Detallado de Accesorios)
ld_dict = {"Radio Corto (R=1D)": 30, "Radio Largo (R=2.5D)": 15, "Union Y": 20, "Campana": 25}

# Longitud física
long_fisica_total = long_ducto_ppal + (n_ramales * long_ramal_m)

# Codos totales (Principal + todos los de los ramales)
total_codos_sistema = n_codos_ppal + (n_ramales * codos_por_ramal)

# Equivalentes en metros
le_codos = total_codos_sistema * ld_dict[tipo_codo] * d_m_ppal
le_uniones = n_ramales * ld_dict["Union Y"] * d_m_ppal
le_campanas = n_ramales * ld_dict["Campana"] * (diam_ramal_mm / 1000) # Pérdida en cada boca

long_virtual = long_fisica_total + le_codos + le_uniones + le_campanas

# 4. Fricción y Pérdidas
reynolds = (v_diseno * d_m_ppal) / viscosidad
rugosidad = materiales[tipo_mat]
f = 0.25 / (math.log10((rugosidad / (3.7 * d_m_ppal)) + (5.74 / reynolds**0.9)))**2
presion_din_pa = 0.5 * densidad_aire * v_diseno**2

p_friccion_pa = (f * long_virtual / d_m_ppal) * presion_din_pa
total_perdidas_inH2O = (p_friccion_pa / 249.08) + dp_filtro

# 5. Mangas y Potencia
area_manga = math.pi * (diam_manga/1000) * (largo_manga/1000)
relacion_at = caudal_total / (n_mangas_act * area_manga * 60)
mangas_nec = math.ceil(caudal_total / (1.1 * 60 * area_manga))

hp_op = (cfm_total * total_perdidas_inH2O) / (6356 * eficiencia_fan)
motor_comercial = next((x for x in [1,2,3,5,7.5,10,15,20,25,30,40,50,60,75,100] if x >= hp_op * 1.15), "N/A")

# --- INTERFAZ DE RESULTADOS ---
res1, res2, res3, res4 = st.columns(4)
res1.metric("Ø Principal", f"{d_m_ppal*1000:.0f} mm")
res2.metric("Caudal Sistema", f"{caudal_total:.0f} m³/h")
res3.metric("Resistencia Total", f"{total_perdidas_inH2O:.2f} inH2O")
res4.metric("Codos Totales", f"{total_codos_sistema}")

st.subheader("🧵 Capacidad de Filtrado")
if n_mangas_act >= mangas_nec:
    st.success(f"✅ Tienes **{n_mangas_act}** mangas. Sobran **{n_mangas_act - mangas_nec}**.")
else:
    st.error(f"🚨 Tienes **{n_mangas_act}** mangas. Faltan **{mangas_nec - n_mangas_act}** (Se requieren {mangas_nec}).")

with st.expander("📊 Ver desglose de Potencia y Energía"):
    col_e1, col_e2 = st.columns(2)
    col_e1.write(f"**Potencia de Operación:** {hp_op:.2f} HP")
    col_e1.write(f"**Motor Recomendado:** {motor_comercial} HP")
    col_e2.write(f"**Costo Eléctrico Est.:** ${hp_op * 0.746 * horas_uso * 22 * costo_kwh:.2f} USD/mes")

# Diagnóstico Final
st.subheader("📡 Diagnóstico de Operación")
balance = sp_ventilador - total_perdidas_inH2O
if balance > 0:
    st.balloons()
    st.success(f"**SISTEMA FUNCIONAL:** El ventilador tiene una reserva de {balance:.2f} in H2O.")
else:
    st.error(f"**SISTEMA INSUFICIENTE:** La resistencia ({total_perdidas_inH2O:.2f}) supera al ventilador ({sp_ventilador}).")
