import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

# Configuración de página
st.set_page_config(page_title="Simulador de Succión Pro", layout="wide")

st.title("🌪️ Ingeniería de Succión y Velocidad en Campanas")
st.markdown("---")

# --- BARRA LATERAL ---
st.sidebar.header("📊 Configuración del Sistema")

with st.sidebar.expander("Ventilador y Entorno", expanded=True):
    cfm_entrada = st.sidebar.number_input("Caudal Nominal Ventilador (CFM)", value=7600)
    sp_ventilador = st.sidebar.number_input("Presión Estática de Placa (in H2O)", value=10.0)
    eficiencia_fan = st.sidebar.slider("Eficiencia (%)", 40, 90, 65) / 100
    altitud = st.sidebar.number_input("Altitud (msnm)", value=2500)

with st.sidebar.expander("Red de Ductos y Ramales"):
    materiales = {"Acero Galvanizado": 0.00015, "PVC": 0.0000015, "Ducto Flexible": 0.003}
    tipo_mat = st.selectbox("Material", list(materiales.keys()))
    
    st.markdown("**Datos de los Ramales**")
    n_ramales = st.number_input("Número de Ramales Abiertos", value=4, min_value=1)
    diam_ramal_mm = st.number_input("Diámetro de cada Ramal (mm)", value=150)
    long_ramal_m = st.number_input("Longitud por Ramal (m)", value=3.0)
    codos_por_ramal = st.number_input("Codos por Ramal", value=2)
    
    st.markdown("**Línea Principal**")
    long_ducto_ppal = st.number_input("Longitud Línea Principal (m)", value=15.0)
    n_codos_ppal = st.number_input("Codos en Línea Principal", value=2)

with st.sidebar.expander("Filtro de Mangas"):
    n_mangas_act = st.number_input("Número de Mangas", value=120)
    diam_manga = st.number_input("Ø Manga (mm)", value=120)
    largo_manga = st.number_input("Largo Manga (mm)", value=2115)
    dp_filtro = st.number_input("Pérdida en Mangas (in H2O)", value=4.0)

# --- LÓGICA DE CÁLCULO ---

# 1. Conversión de Caudal (Nominal a m3/h)
caudal_total_m3h = cfm_entrada * 1.699
caudal_por_ramal_m3h = caudal_total_m3h / n_ramales

# 2. CALCULO DE VELOCIDAD EN CADA CAMPANA (V = Q / A)
area_ramal_m2 = math.pi * (diam_ramal_mm / 1000)**2 / 4
# Velocidad en m/s = (m3/h / 3600) / m2
v_campana_ms = (caudal_por_ramal_m3h / 3600) / area_ramal_m2

# 3. Cálculo de Pérdidas de Presión (para diagnóstico)
densidad_aire = 1.225 * math.exp(-altitud / 8500)
# Usamos el diámetro del ducto principal ideal para transporte (aprox 20 m/s)
d_m_ppal = math.sqrt(4 * (caudal_total_m3h / 3600 / 20) / math.pi)

ld_dict = {"Codo": 20, "Union Y": 20, "Campana": 25}
long_virtual = (long_ducto_ppal + (n_ramales * long_ramal_m)) + \
               ((n_codos_ppal + (n_ramales * codos_por_ramal)) * ld_dict["Codo"] * d_m_ppal)

f = 0.02 # Simplificado para el ejemplo
presion_din_pa = 0.5 * densidad_aire * 20**2
p_friccion_pa = (f * long_virtual / d_m_ppal) * presion_din_pa
total_perdidas_inH2O = (p_friccion_pa / 249.08) + dp_filtro

# --- INTERFAZ DE RESULTADOS ---
st.subheader("🎯 Velocidad de Captación")
c1, c2, c3 = st.columns(3)

# Mostrar la velocidad calculada por campana
color_v = "normal"
if v_campana_ms < 15: color_v = "inverse" # Alerta si es muy lenta para madera

c1.metric("Velocidad en cada Campana", f"{v_campana_ms:.2f} m/s", delta_color=color_v)
c2.metric("Caudal por Ramal", f"{caudal_por_ramal_m3h:.0f} m³/h")
c3.metric("Caudal Total Real", f"{caudal_total_m3h:.0f} m³/h")

# Alertas de velocidad
if v_campana_ms < 15:
    st.error(f"🚨 **VELOCIDAD INSUFICIENTE:** {v_campana_ms:.2f} m/s es muy bajo. El polvo se sedimentará en los ramales. (Mínimo recomendado: 18-20 m/s)")
elif v_campana_ms > 30:
    st.warning(f"⚠️ **VELOCIDAD EXCESIVA:** {v_campana_ms:.2f} m/s. Estás desperdiciando energía y podrías dañar las mangas por abrasión.")
else:
    st.success(f"✅ **VELOCIDAD ÓPTIMA:** {v_campana_ms:.2f} m/s es ideal para transporte de virutas y polvo.")

st.markdown("---")

# Resto de cálculos (Mangas y Diagnóstico)
st.subheader("📊 Estado General del Sistema")
res1, res2, res3 = st.columns(3)

# Mangas
area_f = n_mangas_act * (math.pi * (diam_manga/1000) * (largo_manga/1000))
rel_at = caudal_total_m3h / (area_f * 60)
res1.metric("Relación Aire/Tela", f"{rel_at:.2f} m/min")

# Resistencia
res2.metric("Pérdida de Presión", f"{total_perdidas_inH2O:.2f} inH2O")

# HP
hp_op = (cfm_entrada * total_perdidas_inH2O) / (6356 * eficiencia_fan)
res3.metric("Potencia Requerida", f"{hp_op:.1f} HP")

# Diagnóstico Final
balance = sp_ventilador - total_perdidas_inH2O
if balance < 0:
    st.error(f"❌ **FALLO DE DISEÑO:** El ventilador no tiene presión suficiente para mover el aire a esa velocidad.")
else:
    st.info(f"ℹ️ Con esta configuración, el ventilador tiene una reserva de {balance:.2f} in H2O.")
