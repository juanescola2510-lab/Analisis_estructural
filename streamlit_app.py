import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

# Configuración de página
st.set_page_config(page_title="Simulador Industrial: Horno & Colector", layout="wide")

st.title("🏭 Sistema Integral de Simulación: Horno y Control de Polvo")
st.markdown("---")

# --- BARRA LATERAL: ENTRADA DE DATOS ---
st.sidebar.header("🔥 Configuración del Horno")
with st.sidebar.expander("Dimensiones y Material"):
    long_horno = st.number_input("Longitud Horno (m)", value=60.0)
    diam_horno = st.number_input("Diámetro Interno (m)", value=4.0)
    flujo_crudo = st.number_input("Alimentación Crudo (kg/h)", value=120000)

with st.sidebar.expander("Combustible (HFO/Petcoke)"):
    pci_comb = st.number_input("PCI Combustible (kJ/kg)", value=40900) # Valor HFO
    flujo_comb = st.number_input("Flujo Combustible (kg/h)", value=8000)

st.sidebar.header("🌪️ Sistema de Colector")
with st.sidebar.expander("Ventilador y Mangas"):
    cfm_entrada = st.number_input("Caudal Ventilador (CFM)", value=7600)
    v_diseno = st.slider("Velocidad Transporte (m/s)", 10, 35, 20)
    n_mangas_act = st.number_input("Número de Mangas Actual", value=120)
    largo_manga = st.number_input("Largo Manga (mm)", value=2115)
    diam_manga = st.number_input("Diámetro Manga (mm)", value=120)

st.sidebar.header("🔌 Red de Ductos")
n_ramales = st.sidebar.number_input("Nuevos Ramales (200mm)", value=0)
long_ducto = st.sidebar.number_input("Longitud Ducto Principal (m)", value=20.0)

# --- LÓGICA DE CÁLCULO ---

# 1. Balance del Horno
area_ext = math.pi * diam_horno * long_horno
q_comb = (flujo_comb * pci_comb) / 3600 # kW
perdidas_ref = (2.5 * area_ext * (1450 - 250)) / 0.2 / 1000 # kW (k=2.5, e=0.2m)
temp_clinker = 900 + (q_comb - perdidas_ref) / (flujo_crudo/3600 * 1.1)

# 2. Caudales y Ductos
m3h_base = cfm_entrada * 1.699
area_ramal = math.pi * (0.200)**2 / 4 # Ramales de 200mm
caudal_nuevos = n_ramales * (area_ramal * v_diseno * 3600)
caudal_total = max(m3h_base, caudal_nuevos)

area_req = (caudal_total / 3600) / v_diseno
diam_principal = math.sqrt(4 * area_req / math.pi) * 1000

# 3. Presión Estática (Pérdida en 20m)
# Factor de fricción simplificado para polvo de cemento
friccion = (0.02 * long_ducto / (diam_principal/1000)) * (v_diseno**2 / (2 * 9.81))
presion_perdida = friccion * 1.225 * 9.81 # Pa

# 4. Relación Aire-Tela
area_una_manga = math.pi * (diam_manga/1000) * (largo_manga/1000)
area_tot_filtracion = n_mangas_act * area_una_manga
relacion_at = caudal_total / (area_tot_filtracion * 60)

# --- INTERFAZ DE RESULTADOS ---

col1, col2, col3, col4 = st.columns(4)
col1.metric("Temp. Clinker", f"{temp_clinker:.0f} °C")
col2.metric("Ducto Principal", f"{diam_principal:.0f} mm")
col3.metric("Relación Aire/Tela", f"{relacion_at:.2f} m/min")
col4.metric("Pérdida de Carga", f"{presion_perdida:.1f} Pa")

# --- ALERTAS SISTÉMICAS ---
st.subheader("📋 Diagnóstico Técnico")

# Alerta de Horno
if temp_clinker < 1400:
    st.error("⚠️ Temperatura insuficiente para formar Alita (C3S). Aumente combustible.")

# Alerta de Ductos
if v_diseno < 15:
    st.error(f"🚨 PELIGRO DE FRAGUADO: Velocidad de {v_diseno} m/s causará depósitos en los {long_ducto}m de ducto.")
elif v_diseno > 25:
    st.warning("⚠️ DESGASTE EXCESIVO: Alta abrasión en codos por velocidad elevada.")

# Alerta de Capacidad
if relacion_at > 1.1:
    mangas_faltantes = math.ceil(caudal_total / (1.1 * 60 * area_una_manga)) - n_mangas_act
    st.error(f"❌ COLECTOR SOBRECARGADO: Faltan {mangas_faltantes:.0f} mangas para operar a 1.1 m/min.")

if caudal_nuevos > m3h_base:
    st.warning(f"⚡ CAMBIO DE MOTOR: El sistema requiere {caudal_nuevos/1.699:.0f} CFM. Su ventilador es de {cfm_entrada} CFM.")

# --- SIMULACIÓN VISUAL ---
st.subheader("🎬 Simulación de Partículas en Ducto Principal")
fig, ax = plt.subplots(figsize=(12, 3))
ax.set_facecolor('#202020')

# Dibujo de ducto
ax.axhline(0.8, color='white', lw=4)
ax.axhline(-0.8, color='white', lw=4)

# Partículas
n_p = 200
x_p = np.random.rand(n_p) * 20
if v_diseno < 15:
    y_p = np.random.uniform(-0.78, -0.4, n_p) # Caen al fondo
    label = "ESTADO: SEDIMENTACIÓN (TAPONAMIENTO)"
    color = '#A52A2A'
else:
    y_p = np.random.uniform(-0.6, 0.6, n_p) # Fluyen
    label = "ESTADO: TRANSPORTE NEUMÁTICO EFICIENTE"
    color = '#00FF00'

ax.scatter(x_p, y_p, s=10, color=color, alpha=0.7)
ax.set_xlim(0, 20)
ax.set_ylim(-1, 1)
ax.set_title(label, color='black', fontsize=14)
ax.axis('off')
st.pyplot(fig)

st.info(f"💡 Nota: En {long_ducto} metros de recorrido, una caída de presión de {presion_perdida:.1f} Pa reduce la succión efectiva del ventilador en un {min(100, presion_perdida/10):.1f}%.")
