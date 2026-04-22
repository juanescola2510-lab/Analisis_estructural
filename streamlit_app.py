import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

# Configuración de página
st.set_page_config(page_title="Calculador de Succión Industrial", layout="wide")

st.title("🌪️ Diagnóstico de Colector: Ductos, Mangas y Codos")
st.markdown("---")

# --- BARRA LATERAL ---
st.sidebar.header("📊 Datos del Sistema")

with st.sidebar.expander("Ventilador y Capacidad", expanded=True):
    cfm_entrada = st.sidebar.number_input("Caudal del Ventilador (CFM)", value=7600)
    v_diseno = st.sidebar.slider("Velocidad de Transporte (m/s)", 10, 35, 20)

with st.sidebar.expander("Filtro de Mangas Actual"):
    n_mangas_act = st.number_input("Número de Mangas", value=120)
    diam_manga = st.number_input("Diámetro Manga (mm)", value=120)
    largo_manga = st.number_input("Largo Manga (mm)", value=2115)

st.sidebar.header("🔌 Red de Distribución")
with st.sidebar.expander("Ductos y Codos"):
    long_ducto = st.number_input("Longitud Ducto Recto (m)", value=20.0)
    n_ramales = st.number_input("Nuevos Ramales (200mm)", value=0)
    n_codos = st.number_input("Cantidad de Codos", value=2)
    angulo_codo = st.selectbox("Ángulo de los Codos", [90, 60, 45, 30])
    tipo_codo = st.radio("Tipo de Codo", ["Radio Corto (R=1D)", "Radio Largo (R=2.5D)"])

# --- LÓGICA DE CÁLCULO ---

# 1. Caudales
m3h_base = cfm_entrada * 1.699
area_ramal = math.pi * (0.200)**2 / 4
caudal_nuevos = n_ramales * (area_ramal * v_diseno * 3600)
caudal_total = max(m3h_base, caudal_nuevos)

# 2. Diámetro Ducto Principal
area_req = (caudal_total / 3600) / v_diseno
diam_principal = math.sqrt(4 * area_req / math.pi) * 1000 # mm

# 3. Pérdida de Presión (Ducto Recto)
densidad_aire = 1.225 # kg/m3
presion_dinamica = 0.5 * densidad_aire * v_diseno**2
f_friccion = 0.02
p_recto = (f_friccion * long_ducto / (max(0.1, diam_principal/1000))) * presion_dinamica

# 4. Pérdida de Presión (Codos)
# Coeficiente K aproximado según ángulo y radio
k_base = 0.25 if tipo_codo == "Radio Largo (R=2.5D)" else 0.50
# Ajuste por ángulo
factor_angulo = angulo_codo / 90
k_codo = k_base * factor_angulo
p_codos = n_codos * k_codo * presion_dinamica

p_total_pa = p_recto + p_codos

# 5. Relación Aire-Tela
area_una_manga = math.pi * (diam_manga/1000) * (largo_manga/1000)
area_tot_filtracion = n_mangas_act * area_una_manga
relacion_at = caudal_total / (area_tot_filtracion * 60)

# --- INTERFAZ ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Ducto Principal", f"{diam_principal:.0f} mm")
c2.metric("Relación Aire/Tela", f"{relacion_at:.2f} m/min")
c3.metric("Pérdida en Ductos", f"{p_recto:.1f} Pa")
c4.metric("Pérdida en Codos", f"{p_codos:.1f} Pa")

st.info(f"**Presión Total a Vencer:** {p_total_pa:.1f} Pa (aprox. {p_total_pa/249.08:.2f} pulgadas de columna de agua)")

# --- ALERTAS ---
st.subheader("📋 Diagnóstico")

if relacion_at > 1.1:
    st.error(f"❌ Sobrecarga en filtro. Relación {relacion_at:.2f} es muy alta.")
if p_total_pa > 1500:
    st.warning("⚠️ Pérdida de presión elevada. El ventilador podría no tener suficiente fuerza.")

# --- SIMULACIÓN VISUAL ---
st.subheader("🎬 Visualización del Flujo")
fig, ax = plt.subplots(figsize=(12, 2.5))
ax.set_facecolor('#1e1e1e')

# Dibujo de ducto y codo simbólico
x = np.linspace(0, 10, 200)
y_upper = np.full_like(x, 0.8)
y_lower = np.full_like(x, -0.8)
ax.plot(x, y_upper, color='white', lw=3)
ax.plot(x, y_lower, color='white', lw=3)

# Partículas
n_p = 150
xp = np.random.rand(n_p) * 10
if v_diseno < 15:
    yp = np.random.uniform(-0.75, -0.4, n_p)
    color_p = 'brown'
    msg = "SEDIMENTACIÓN"
else:
    yp = np.random.uniform(-0.6, 0.6, n_p)
    color_p = '#00FF00'
    msg = "TRANSPORTE ACTIVO"

ax.scatter(xp, yp, s=10, color=color_p, alpha=0.6)
ax.axis('off')
st.pyplot(fig)

st.write(f"**Nota Técnica:** Un codo de {angulo_codo}° {tipo_codo} genera una resistencia equivalente a varios metros de tubo recto. Evite ángulos de 90° si es posible.")
