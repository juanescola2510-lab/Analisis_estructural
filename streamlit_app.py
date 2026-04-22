import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

# Configuración de página
st.set_page_config(page_title="Simulador de Succión Industrial", layout="wide")

st.title("🌪️ Diagnóstico de Succión y Capacidad de Sistema")
st.markdown("---")

# --- BARRA LATERAL ---
st.sidebar.header("📊 Datos del Sistema")

with st.sidebar.expander("Ventilador (Fuerza de Succión)", expanded=True):
    cfm_entrada = st.sidebar.number_input("Caudal Nominal (CFM)", value=7600)
    sp_ventilador = st.sidebar.number_input("Presión Estática de Placa (in H2O)", value=10.0, help="Presión máxima que el ventilador puede vencer")
    v_diseno = st.sidebar.slider("Velocidad de Transporte (m/s)", 10, 35, 20)

with st.sidebar.expander("Filtro de Mangas Actual"):
    n_mangas_act = st.number_input("Número de Mangas Instaladas", value=120)
    diam_manga = st.number_input("Diámetro Manga (mm)", value=120)
    largo_manga = st.number_input("Largo Manga (mm)", value=2115)
    dp_filtro = st.number_input("Presión diferencial del filtro (in H2O)", value=4.0, help="Resistencia que ofrecen las mangas sucias")

st.sidebar.header("🔌 Red de Distribución")
with st.sidebar.expander("Ductos y Accesorios"):
    long_ducto = st.number_input("Longitud Ducto Principal (m)", value=20.0)
    n_ramales = st.number_input("Nuevos Ramales (200mm)", value=0)
    n_codos = st.number_input("Cantidad de Codos", value=2)
    angulo_codo = st.selectbox("Ángulo de los Codos (°)", [90, 60, 45, 30])
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

# 3. Cálculo de Pérdidas de Presión
densidad_aire = 1.225 # kg/m3
presion_dinamica_pa = 0.5 * densidad_aire * v_diseno**2
f_friccion = 0.02
p_recto_pa = (f_friccion * long_ducto / (max(0.1, diam_principal/1000))) * presion_dinamica_pa

k_base = 0.25 if tipo_codo == "Radio Largo (R=2.5D)" else 0.55
k_codo = k_base * (angulo_codo / 90)
p_codos_pa = n_codos * k_codo * presion_dinamica_pa

# Total pérdidas en in H2O (Ductos + Filtro)
total_perdidas_inH2O = ((p_recto_pa + p_codos_pa) / 249.08) + dp_filtro

# 4. Cálculo de Mangas
area_una_manga = math.pi * (diam_manga/1000) * (largo_manga/1000)
area_tot_filtracion = n_mangas_act * area_una_manga
relacion_at = caudal_total / (area_tot_filtracion * 60)
mangas_necesarias = math.ceil(caudal_total / (1.1 * 60 * area_una_manga))
mangas_faltantes = max(0, mangas_necesarias - n_mangas_act)

# --- INTERFAZ DE RESULTADOS ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Ducto Principal", f"{diam_principal:.0f} mm")
c2.metric("Relación Aire/Tela", f"{relacion_at:.2f} m/min")
c3.metric("Resistencia Total", f"{total_perdidas_inH2O:.2f} in H2O")
c4.metric("Mangas Faltantes", f"{mangas_faltantes:.0f}")

# --- DIAGNÓSTICO DE SUCCIÓN ---
st.subheader("📡 Estado de Succión en Ramales")

balance_presion = sp_ventilador - total_perdidas_inH2O

if balance_presion > 1.0:
    st.success(f"✅ **HAY SUCCIÓN:** El ventilador tiene reserva de presión ({balance_presion:.2f} in H2O). Los ramales funcionarán correctamente.")
elif balance_presion > 0:
    st.warning(f"⚠️ **SUCCIÓN DÉBIL:** El ventilador está al límite ({balance_presion:.2f} in H2O). La captación en ramales será pobre.")
else:
    st.error(f"🚨 **SIN SUCCIÓN:** El sistema tiene demasiada resistencia ({total_perdidas_inH2O:.2f} in H2O) para este ventilador ({sp_ventilador} in H2O). El aire NO circulará.")

# --- ALERTAS DE MANGAS ---
if mangas_faltantes > 0:
    st.info(f"💡 Para este flujo necesitas un total de **{mangas_necesarias} mangas**. Te faltan {mangas_faltantes}.")

# --- SIMULACIÓN VISUAL ---
st.subheader("🎬 Visualización del Flujo")
fig, ax = plt.subplots(figsize=(12, 2.5))
ax.set_facecolor('#1e1e1e')

n_p = 200
x_p = np.random.rand(n_p) * 10

if balance_presion <= 0:
    y_p = np.random.uniform(-0.75, -0.6, n_p) # Partículas quietas en el fondo
    status_txt = "FLUJO DETENIDO - SIN SUCCIÓN"
    color_p = "red"
elif v_diseno < 15:
    y_p = np.random.uniform(-0.75, -0.4, n_p)
    status_txt = "RIESGO DE SEDIMENTACIÓN"
    color_p = "brown"
else:
    y_p = np.random.uniform(-0.6, 0.6, n_p)
    status_txt = "SUCCIÓN ACTIVA"
    color_p = "#00FF00"

ax.scatter(x_p, y_p, s=12, color=color_p, alpha=0.6)
ax.set_xlim(0, 10); ax.set_ylim(-1, 1)
ax.set_title(status_txt, color="black")
ax.axis('off')
st.pyplot(fig)
