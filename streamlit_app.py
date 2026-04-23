import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

# Configuración de página
st.set_page_config(page_title="Simulador de Succión Pro", layout="wide")

st.title("🌪️ Ingeniería de Succión: Comparativa de Ductos y Filtrado")
st.markdown("---")

# --- BARRA LATERAL ---
st.sidebar.header("📊 Configuración del Sistema")

with st.sidebar.expander("Ventilador y Entorno", expanded=True):
    cfm_entrada = st.sidebar.number_input("Caudal Nominal Ventilador (CFM)", value=7600)
    sp_ventilador = st.sidebar.number_input("Presión Estática de Placa (in H2O)", value=10.0)
    eficiencia_fan = st.sidebar.slider("Eficiencia (%)", 40, 90, 65) / 100
    altitud = st.sidebar.number_input("Altitud (msnm)", value=2500)
    v_transp_target = st.sidebar.slider("Velocidad de Transporte Objetivo (m/s)", 15, 30, 20)

with st.sidebar.expander("Red de Ductos y Ramales"):
    materiales = {"Acero Galvanizado": 0.00015, "PVC": 0.0000015, "Ducto Flexible": 0.003}
    tipo_mat = st.selectbox("Material de Ductos", list(materiales.keys()))
    
    st.markdown("**Línea Principal**")
    diam_principal_instalado_mm = st.number_input("Diámetro Principal INSTALADO (mm)", value=400)
    long_ducto_ppal = st.number_input("Longitud Línea Principal (m)", value=15.0)
    n_codos_ppal = st.number_input("Codos en Línea Principal", value=2)
    
    st.markdown("---")
    st.markdown("**Datos de los Ramales**")
    n_ramales = st.number_input("Número de Ramales Abiertos", value=4, min_value=1)
    diam_ramal_mm = st.number_input("Diámetro del Ducto Ramal (mm)", value=150)
    long_ramal_m = st.number_input("Longitud por Ramal (m)", value=3.0)
    codos_por_ramal = st.number_input("Codos por cada Ramal", value=2)

    st.markdown("---")
    st.markdown("**📐 Dimensiones de la Campana (Boca)**")
    tipo_campana = st.radio("Forma de la Boca", ["Circular", "Rectangular"])
    if tipo_campana == "Circular":
        diam_campana_mm = st.number_input("Diámetro de la Boca (mm)", value=250)
        area_campana_m2 = math.pi * (diam_campana_mm / 1000)**2 / 4
    else:
        ancho_mm = st.number_input("Ancho de la Boca (mm)", value=300)
        alto_mm = st.number_input("Alto de la Boca (mm)", value=200)
        area_campana_m2 = (ancho_mm / 1000) * (alto_mm / 1000)

with st.sidebar.expander("Filtro de Mangas"):
    n_mangas_act = st.number_input("Número de Mangas Instaladas", value=120)
    diam_manga = st.number_input("Ø Manga (mm)", value=120)
    largo_manga = st.number_input("Largo Manga (mm)", value=2115)
    dp_filtro = st.number_input("Pérdida en Mangas (in H2O)", value=4.0)

# --- LÓGICA DE CÁLCULO ---

# 1. Caudales y Propiedades
densidad_aire = 1.225 * math.exp(-altitud / 8500)
caudal_total_m3h = cfm_entrada * 1.699
caudal_por_ramal_m3h = caudal_total_m3h / n_ramales

# 2. COMPARATIVA DE DUCTO PRINCIPAL
# Diámetro Ideal (para mantener la velocidad objetivo)
area_ideal_m2 = (caudal_total_m3h / 3600) / v_transp_target
diam_ideal_mm = math.sqrt(4 * area_ideal_m2 / math.pi) * 1000

# Velocidad Real en el Ducto Instalado
area_instalada_m2 = math.pi * (diam_principal_instalado_mm / 1000)**2 / 4
v_real_principal_ms = (caudal_total_m3h / 3600) / area_instalada_m2

# 3. VELOCIDADES EN RAMALES Y CAMPANA
area_ducto_ramal_m2 = math.pi * (diam_ramal_mm / 1000)**2 / 4
v_transporte_ramal_ms = (caudal_por_ramal_m3h / 3600) / area_ducto_ramal_m2
v_captacion_ms = (caudal_por_ramal_m3h / 3600) / area_campana_m2

# 4. Pérdidas de Presión (Basado en el ducto instalado)
d_m_inst = diam_principal_instalado_mm / 1000
ld_dict = {"Codo": 20, "Union Y": 20, "Campana": 25}
total_codos = n_codos_ppal + (n_ramales * codos_por_ramal)
long_virtual = (long_ducto_ppal + (n_ramales * long_ramal_m)) + \
               (total_codos * ld_dict["Codo"] * d_m_inst) + \
               (n_ramales * ld_dict["Union Y"] * d_m_inst)

f = 0.02 
presion_din_pa = 0.5 * densidad_aire * v_real_principal_ms**2
p_friccion_pa = (f * long_virtual / d_m_inst) * presion_din_pa
total_perdidas_inH2O = (p_friccion_pa / 249.08) + dp_filtro

# 5. MANGAS (Se mantiene igual)
area_total_f = n_mangas_act * (math.pi * (diam_manga/1000) * (largo_manga/1000))
relacion_at = caudal_total_m3h / (area_total_f * 60)
mangas_nec = math.ceil(caudal_total_m3h / (1.1 * 60 * (math.pi * (diam_manga/1000) * (largo_manga/1000))))

# --- INTERFAZ DE RESULTADOS ---

# COMPARATIVA DE DUCTO PRINCIPAL
st.subheader("📏 Comparativa de Ducto Principal")
col_d1, col_d2, col_d3 = st.columns(3)
col_d1.metric("Ø Ideal Calculado", f"{diam_ideal_mm:.0f} mm")
col_d2.metric("Ø Real Instalado", f"{diam_principal_instalado_mm} mm")
col_d3.metric("Velocidad en Principal", f"{v_real_principal_ms:.2f} m/s")

if v_real_principal_ms < v_transp_target - 2:
    st.error(f"🚨 **Ducto Principal muy GRANDE:** La velocidad ({v_real_principal_ms:.2f} m/s) es menor a la de transporte. El material se va a acumular en el piso del ducto.")
elif v_real_principal_ms > v_transp_target + 8:
    st.warning(f"⚠️ **Ducto Principal muy PEQUEÑO:** La velocidad es excesiva, lo que genera demasiada fricción y pérdida de presión.")
else:
    st.success("✅ **Diámetro Correcto:** El ducto principal mantiene una velocidad de transporte adecuada.")

# VELOCIDADES Y MANGAS
st.subheader("🎯 Velocidades y Filtrado")
v1, v2, v3, v4 = st.columns(4)
v1.metric("V. Captación (Boca)", f"{v_captacion_ms:.2f} m/s")
v2.metric("V. Ramal (Ducto)", f"{v_transporte_ramal_ms:.2f} m/s")
v3.metric("Aire/Tela", f"{relacion_at:.2f} m/min")
v4.metric("Mangas Necesarias", f"{mangas_nec}")

# RESULTADOS DE FILTRADO
if n_mangas_act >= mangas_nec:
    st.info(f"✅ Filtro adecuado: Tienes {n_mangas_act} mangas (Sobran {n_mangas_act - mangas_nec}).")
else:
    st.error(f"🚨 Filtro insuficiente: Faltan {mangas_nec - n_mangas_act} mangas.")

# DIAGNÓSTICO DE PRESIÓN
st.subheader("📊 Potencia y Resistencia")
res1, res2, res3 = st.columns(3)
res1.metric("Resistencia Total", f"{total_perdidas_inH2O:.2f} inH2O")
hp_op = (cfm_entrada * total_perdidas_inH2O) / (6356 * eficiencia_fan)
res2.metric("Potencia Requerida", f"{hp_op:.1f} HP")

balance = sp_ventilador - total_perdidas_inH2O
if balance >= 0:
    res3.metric("Reserva Presión", f"{balance:.2f} inH2O")
    st.success("💪 El ventilador tiene fuerza suficiente.")
else:
    res3.metric("Déficit Presión", f"{balance:.2f} inH2O", delta_color="inverse")
    st.error("❌ El ventilador no podrá mover este aire debido a la alta resistencia.")
