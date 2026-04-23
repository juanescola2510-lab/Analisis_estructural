import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

# Configuración de página
st.set_page_config(page_title="Simulador de Succión Pro", layout="wide")

st.title("🌪️ Ingeniería de Succión: Velocidad, Capacidad y Filtrado")
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
    tipo_mat = st.selectbox("Material de Ductos", list(materiales.keys()))
    
    st.markdown("**Datos de los Ramales**")
    n_ramales = st.number_input("Número de Ramales Abiertos", value=4, min_value=1)
    diam_ramal_mm = st.number_input("Diámetro del Ducto Ramal (mm)", value=150)
    long_ramal_m = st.number_input("Longitud por Ramal (m)", value=3.0)
    codos_por_ramal = st.number_input("Codos por cada Ramal", value=2)

    st.markdown("---")
    st.markdown("**📐 Dimensiones de la Campana (Boca)**")
    tipo_campana = st.radio("Forma de la Boca de Succión", ["Circular", "Rectangular"])
    
    if tipo_campana == "Circular":
        diam_campana_mm = st.number_input("Diámetro de la Boca (mm)", value=250)
        area_campana_m2 = math.pi * (diam_campana_mm / 1000)**2 / 4
    else:
        ancho_mm = st.number_input("Ancho de la Boca (mm)", value=300)
        alto_mm = st.number_input("Alto de la Boca (mm)", value=200)
        area_campana_m2 = (ancho_mm / 1000) * (alto_mm / 1000)

    st.markdown("---")
    st.markdown("**Línea Principal**")
    long_ducto_ppal = st.number_input("Longitud Línea Principal (m)", value=15.0)
    n_codos_ppal = st.number_input("Codos en Línea Principal", value=2)

with st.sidebar.expander("Filtro de Mangas"):
    n_mangas_act = st.number_input("Número de Mangas Instaladas", value=120)
    diam_manga = st.number_input("Ø Manga (mm)", value=120)
    largo_manga = st.number_input("Largo Manga (mm)", value=2115)
    dp_filtro = st.number_input("Pérdida en Mangas (in H2O)", value=4.0)

# --- LÓGICA DE CÁLCULO ---

# 1. Propiedades del Aire y Caudales
densidad_aire = 1.225 * math.exp(-altitud / 8500)
caudal_total_m3h = cfm_entrada * 1.699
caudal_por_ramal_m3h = caudal_total_m3h / n_ramales

# 2. CALCULO DE VELOCIDADES
# Velocidad de Transporte (Dentro del ducto del ramal)
area_ducto_ramal_m2 = math.pi * (diam_ramal_mm / 1000)**2 / 4
v_transporte_ms = (caudal_por_ramal_m3h / 3600) / area_ducto_ramal_m2

# Velocidad de Captación (En la boca de la campana)
v_captacion_ms = (caudal_por_ramal_m3h / 3600) / area_campana_m2

# 3. Pérdidas de Presión (Longitud Equivalente)
d_m_ppal = math.sqrt(4 * (caudal_total_m3h / 3600 / 20) / math.pi) # Ø aprox para 20m/s
ld_dict = {"Codo": 20, "Union Y": 20, "Campana": 25}
total_codos = n_codos_ppal + (n_ramales * codos_por_ramal)

long_virtual = (long_ducto_ppal + (n_ramales * long_ramal_m)) + \
               (total_codos * ld_dict["Codo"] * d_m_ppal) + \
               (n_ramales * ld_dict["Union Y"] * d_m_ppal)

f = 0.02 # Coeficiente de fricción promedio
presion_din_pa = 0.5 * densidad_aire * 20**2
p_friccion_pa = (f * long_virtual / d_m_ppal) * presion_din_pa
total_perdidas_inH2O = (p_friccion_pa / 249.08) + dp_filtro

# 4. CAPACIDAD DE MANGAS (No borrado)
area_una_manga = math.pi * (diam_manga/1000) * (largo_manga/1000)
area_total_filtracion = n_mangas_act * area_una_manga
relacion_at = caudal_total_m3h / (area_total_filtracion * 60) # m/min

mangas_necesarias = math.ceil(caudal_total_m3h / (1.1 * 60 * area_una_manga))
diferencia_mangas = n_mangas_act - mangas_necesarias

# 5. Potencia
hp_op = (cfm_entrada * total_perdidas_inH2O) / (6356 * eficiencia_fan)

# --- INTERFAZ DE RESULTADOS ---

# Fila 1: Velocidades
st.subheader("🎯 Análisis de Velocidades")
v1, v2, v3 = st.columns(3)
v1.metric("Velocidad Captación (Boca)", f"{v_captacion_ms:.2f} m/s")
v2.metric("Velocidad Transporte (Tubo)", f"{v_transporte_ms:.2f} m/s")
v3.metric("Área Campana", f"{area_campana_m2:.3f} m²")

if v_transporte_ms < 15:
    st.error("🚨 **Velocidad de transporte insuficiente:** El material se acumulará en los ductos.")
elif v_transporte_ms > 28:
    st.warning("⚠️ **Velocidad muy alta:** Alto desgaste abrasivo en ductos y exceso de ruido.")

# Fila 2: Filtro de Mangas (SECCIÓN REQUERIDA)
st.subheader("🧵 Estado del Filtro de Mangas")
m1, m2, m3 = st.columns(3)
m1.metric("Relación Aire/Tela", f"{relacion_at:.2f} m/min")
m2.metric("Mangas Necesarias", f"{mangas_necesarias}")
m3.metric("Superficie Filtrante", f"{area_total_filtracion:.2f} m²")

if diferencia_mangas >= 0:
    st.success(f"✅ Tienes **{n_mangas_act}** mangas. Sobran **{diferencia_mangas}** para el caudal actual.")
else:
    st.error(f"🚨 Faltan **{abs(diferencia_mangas)}** mangas. El filtro está saturado (Relación Aire/Tela alta).")

# Fila 3: Energía y Diagnóstico
st.subheader("📊 Potencia y Resistencia")
p1, p2, p3 = st.columns(3)
p1.metric("Resistencia Total", f"{total_perdidas_inH2O:.2f} inH2O")
p2.metric("Potencia Requerida", f"{hp_op:.1f} HP")

balance = sp_ventilador - total_perdidas_inH2O
if balance >= 0:
    p3.metric("Reserva de Presión", f"{balance:.2f} inH2O", delta=f"{balance:.2f}")
    st.success("✅ El ventilador es capaz de operar el sistema.")
else:
    p3.metric("Déficit de Presión", f"{balance:.2f} inH2O", delta=f"{balance:.2f}", delta_color="inverse")
    st.error("❌ El ventilador NO tiene presión suficiente para esta red.")
