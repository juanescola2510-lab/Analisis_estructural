import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

# Configuración de página
st.set_page_config(page_title="Gestor de Colectores de Polvo", layout="wide")

st.title("🌪️ Sistema de Diagnóstico: Colector de Mangas y Ductos")
st.markdown("---")

# --- BARRA LATERAL: ENTRADA DE DATOS ---
st.sidebar.header("📊 Datos del Sistema")

with st.sidebar.expander("Ventilador y Capacidad", expanded=True):
    cfm_entrada = st.number_input("Caudal del Ventilador (CFM)", value=7600)
    v_diseno = st.slider("Velocidad de Transporte (m/s)", 10, 35, 20)

with st.sidebar.expander("Filtro de Mangas Actual"):
    n_mangas_act = st.number_input("Número de Mangas", value=120)
    diam_manga = st.number_input("Diámetro Manga (mm)", value=120)
    largo_manga = st.number_input("Largo Manga (mm)", value=2115)

st.sidebar.header("🔌 Red de Distribución")
with st.sidebar.expander("Ramales y Ductos"):
    n_ramales = st.number_input("Nuevos Ramales (200mm)", value=0)
    long_ducto = st.number_input("Longitud Ducto Principal (m)", value=20.0)

# --- LÓGICA DE CÁLCULO ---

# 1. Caudales
m3h_base = cfm_entrada * 1.699
area_ramal = math.pi * (0.200)**2 / 4 # Ramales de 200mm
caudal_nuevos = n_ramales * (area_ramal * v_diseno * 3600)

# El caudal total es el del ventilador, a menos que los ramales pidan más
caudal_total = max(m3h_base, caudal_nuevos)

# 2. Diámetro Ducto Principal
area_req = (caudal_total / 3600) / v_diseno
diam_principal = math.sqrt(4 * area_req / math.pi) * 1000

# 3. Presión Estática (Pérdida por fricción en longitud de ducto)
# Basado en densidad de aire estándar y factor de fricción para ductos industriales
friccion_factor = 0.02 
presion_perdida = (friccion_factor * long_ducto / (max(0.1, diam_principal/1000))) * (v_diseno**2 / (2 * 9.81)) * 1.225 * 9.81

# 4. Relación Aire-Tela (G/C Ratio)
area_una_manga = math.pi * (diam_manga/1000) * (largo_manga/1000)
area_tot_filtracion = n_mangas_act * area_una_manga
relacion_at = caudal_total / (area_tot_filtracion * 60)

# --- INTERFAZ DE RESULTADOS ---

col1, col2, col3 = st.columns(3)
col1.metric("Ducto Principal Requerido", f"{diam_principal:.0f} mm")
col2.metric("Relación Aire/Tela", f"{relacion_at:.2f} m/min")
col3.metric("Pérdida de Presión Estática", f"{presion_perdida:.1f} Pa")

# --- ALERTAS TÉCNICAS ---
st.subheader("📋 Diagnóstico de Operación")

# Alerta de Ductos (Sedimentación o Abrasión)
if v_diseno < 15:
    st.error(f"🚨 **PELIGRO DE FRAGUADO:** Velocidad de {v_diseno} m/s es muy baja. El polvo se asentará en los {long_ducto}m de ducto.")
elif v_diseno > 25:
    st.warning(f"⚠️ **DESGASTE ACELERADO:** Velocidad de {v_diseno} m/s causará erosión en codos y paredes.")
else:
    st.success(f"✅ Velocidad de transporte ideal ({v_diseno} m/s).")

# Alerta de Capacidad de Mangas
if relacion_at > 1.1:
    mangas_faltantes = math.ceil(caudal_total / (1.1 * 60 * area_una_manga)) - n_mangas_act
    st.error(f"❌ **FILTRO SOBRECARGADO:** Faltan {mangas_faltantes:.0f} mangas para operar a 1.1 m/min.")
else:
    st.success("✅ Superficie de filtración adecuada.")

# Alerta de Potencia de Ventilador
if caudal_nuevos > m3h_base:
    st.warning(f"⚡ **INSUFICIENCIA DE AIRE:** Los ramales exigen {caudal_nuevos/1.699:.0f} CFM. Su ventilador actual es de {cfm_entrada} CFM. Requiere cambio de motor.")

# --- SIMULACIÓN VISUAL ---
st.subheader("🎬 Simulación de Partículas en Ducto")
fig, ax = plt.subplots(figsize=(12, 3))
ax.set_facecolor('#202020')

# Dibujo de ducto (Paredes)
ax.axhline(0.8, color='white', lw=4)
ax.axhline(-0.8, color='white', lw=4)

# Generación de Partículas (Visualización de flujo)
n_p = 200
x_p = np.random.rand(n_p) * 10
if v_diseno < 15:
    y_p = np.random.uniform(-0.78, -0.4, n_p) # Partículas caen
    label = "ESTADO: SEDIMENTACIÓN (ACUMULACIÓN DE POLVO)"
    color = '#A52A2A' # Marrón
else:
    y_p = np.random.uniform(-0.6, 0.6, n_p) # Partículas fluyen
    label = "ESTADO: FLUJO AERODINÁMICO CORRECTO"
    color = '#00FF00' # Verde

ax.scatter(x_p, y_p, s=12, color=color, alpha=0.7)
ax.set_xlim(0, 10)
ax.set_ylim(-1, 1)
ax.set_title(label, color='black', fontsize=14, fontweight='bold')
ax.axis('off')
st.pyplot(fig)

st.info(f"💡 **Dato clave:** En {long_ducto} metros de recorrido, el aire pierde energía. Si el ducto principal se reduce por fraguado, la pérdida de presión sube exponencialmente.")
