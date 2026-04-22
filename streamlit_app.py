import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

# Configuración de página
st.set_page_config(page_title="Calculador Pro Colector de Polvo", layout="wide")

st.title("🌪️ Diagnóstico de Colector: Ductos, Codos y Filtro")
st.markdown("---")

# --- BARRA LATERAL ---
st.sidebar.header("📊 Datos del Sistema")

with st.sidebar.expander("Ventilador y Capacidad", expanded=True):
    cfm_entrada = st.sidebar.number_input("Caudal del Ventilador (CFM)", value=7600)
    v_diseno = st.sidebar.slider("Velocidad de Transporte (m/s)", 10, 35, 20)

with st.sidebar.expander("Filtro de Mangas Actual"):
    n_mangas_act = st.number_input("Número de Mangas Instaladas", value=120)
    diam_manga = st.number_input("Diámetro Manga (mm)", value=120)
    largo_manga = st.number_input("Largo Manga (mm)", value=2115)

st.sidebar.header("🔌 Red de Distribución")
with st.sidebar.expander("Ductos y Accesorios"):
    long_ducto = st.number_input("Longitud Ducto Recto (m)", value=20.0)
    n_ramales = st.number_input("Nuevos Ramales (200mm)", value=0)
    n_codos = st.number_input("Cantidad de Codos en la red", value=2)
    angulo_codo = st.selectbox("Ángulo de los Codos (°)", [90, 60, 45, 30, 15])
    tipo_codo = st.radio("Tipo de Curvatura", ["Radio Corto (R=1D)", "Radio Largo (R=2.5D)"])

# --- LÓGICA DE CÁLCULO ---

# 1. Caudales
m3h_base = cfm_entrada * 1.699
area_ramal = math.pi * (0.200)**2 / 4
caudal_nuevos = n_ramales * (area_ramal * v_diseno * 3600)
caudal_total = max(m3h_base, caudal_nuevos)

# 2. Diámetro Ducto Principal
area_req = (caudal_total / 3600) / v_diseno
diam_principal = math.sqrt(4 * area_req / math.pi) * 1000 # mm

# 3. Pérdida de Presión (Fricción y Codos)
densidad_aire = 1.225 # kg/m3
presion_dinamica = 0.5 * densidad_aire * v_diseno**2
f_friccion = 0.02
p_recto = (f_friccion * long_ducto / (max(0.1, diam_principal/1000))) * presion_dinamica

# Coeficiente K según tipo y ángulo de codo
k_base = 0.25 if tipo_codo == "Radio Largo (R=2.5D)" else 0.55
k_codo = k_base * (angulo_codo / 90)
p_codos = n_codos * k_codo * presion_dinamica
p_total_pa = p_recto + p_codos

# 4. Relación Aire-Tela y Cálculo de Mangas Faltantes
area_una_manga = math.pi * (diam_manga/1000) * (largo_manga/1000)
area_tot_filtracion = n_mangas_act * area_una_manga
relacion_at = caudal_total / (area_tot_filtracion * 60)

# CÁLCULO CRÍTICO: MANGAS NECESARIAS
mangas_necesarias = math.ceil(caudal_total / (1.1 * 60 * area_una_manga))
mangas_faltantes = max(0, mangas_necesarias - n_mangas_act)

# --- INTERFAZ DE RESULTADOS ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Ducto Principal", f"{diam_principal:.0f} mm")
c2.metric("Relación Aire/Tela", f"{relacion_at:.2f} m/min")
c3.metric("Pérdida de Carga", f"{p_total_pa:.1f} Pa")
c4.metric("Mangas Necesarias", f"{mangas_necesarias:.0f} uds")

# --- BLOQUE DE ALERTAS ---
st.subheader("📋 Diagnóstico de Capacidad")

if mangas_faltantes > 0:
    st.error(f"⚠️ **DÉFICIT DE FILTRACIÓN:** Faltan **{mangas_faltantes} mangas** adicionales para operar a 1.1 m/min. El filtro actual está saturado.")
else:
    st.success("✅ **CAPACIDAD OK:** El número de mangas actual es suficiente para el flujo solicitado.")

if relacion_at > 1.5:
    st.warning("🚨 **FALLO INMINENTE:** La relación Aire/Tela es extremadamente alta. Las mangas se romperán o el polvo saldrá por la chimenea.")

# --- SIMULACIÓN VISUAL ---
st.subheader("🎬 Simulación de Flujo de Polvo")
fig, ax = plt.subplots(figsize=(12, 3))
ax.set_facecolor('#1e1e1e')

# Ducto principal
ax.axhline(0.8, color='white', lw=3)
ax.axhline(-0.8, color='white', lw=3)

# Partículas dinámicas según velocidad
n_p = 200
x_p = np.random.rand(n_p) * 10
if v_diseno < 15:
    y_p = np.random.uniform(-0.75, -0.45, n_p)
    status_text = "RIESGO: SEDIMENTACIÓN EN DUCTO"
    p_color = '#FF4B4B'
else:
    y_p = np.random.uniform(-0.6, 0.6, n_p)
    status_text = "ESTADO: TRANSPORTE NEUMÁTICO ACTIVO"
    p_color = '#00FF00'

ax.scatter(x_p, y_p, s=12, color=p_color, alpha=0.6)
ax.set_xlim(0, 10)
ax.set_ylim(-1, 1)
ax.set_title(status_text, color='black', fontsize=12)
ax.axis('off')
st.pyplot(fig)

# --- DETALLE TÉCNICO ---
with st.expander("Ver desglose de pérdidas de presión"):
    st.write(f"- Pérdida por ducto recto ({long_ducto}m): {p_recto:.1f} Pa")
    st.write(f"- Pérdida por {n_codos} codo(s) de {angulo_codo}°: {p_codos:.1f} Pa")
    st.write(f"- Resistencia total del sistema: {p_total_pa/249.08:.2f} in H2O")
    st.info("Nota: Estas pérdidas no incluyen la resistencia propia de las mangas (DP del filtro), que suele sumar otros 1000-1500 Pa.")
