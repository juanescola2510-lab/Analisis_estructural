import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Simulador Succión Clinker - Hardox", layout="wide")

st.title("🌪️ Ingeniería de Succión: Polvo de Clinker en Ductos Hardox")
st.markdown("---")

# --- BARRA LATERAL ---
st.sidebar.header("📊 Configuración del Sistema")

with st.sidebar.expander("Ventilador y Entorno", expanded=True):
    cfm_entrada = st.sidebar.number_input("Caudal Nominal Ventilador (CFM)", value=7600)
    sp_ventilador = st.sidebar.number_input("Presión Estática de Placa (in H2O)", value=10.0)
    eficiencia_fan = st.sidebar.slider("Eficiencia (%)", 40, 90, 65) / 100
    altitud = st.sidebar.number_input("Altitud (msnm)", value=2500)
    v_transp_target = st.sidebar.slider("Velocidad de Transporte Objetivo (m/s)", 20, 40, 25)

with st.sidebar.expander("Red de Ductos y Ramales"):
    materiales = {"Acero Hardox / Antibrasivo": 0.0002, "Acero Galvanizado": 0.00015, "PVC": 0.0000015}
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

densidad_aire = 1.225 * math.exp(-altitud / 8500)
caudal_total_m3h = cfm_entrada * 1.699
caudal_por_ramal_m3h = caudal_total_m3h / n_ramales

# 1. Comparativa Ducto Principal e Ideal
area_ideal_m2 = (caudal_total_m3h / 3600) / v_transp_target
diam_ideal_mm = math.sqrt(4 * area_ideal_m2 / math.pi) * 1000
area_instalada_m2 = math.pi * (diam_principal_instalado_mm / 1000)**2 / 4
v_real_principal_ms = (caudal_total_m3h / 3600) / area_instalada_m2

# Caudal ideal basado en velocidad target en el ducto instalado
caudal_ideal_m3h = v_transp_target * area_instalada_m2 * 3600

# 2. Velocidades
area_ducto_ramal_m2 = math.pi * (diam_ramal_mm / 1000)**2 / 4
v_transporte_ramal_ms = (caudal_por_ramal_m3h / 3600) / area_ducto_ramal_m2
v_captacion_ms = (caudal_por_ramal_m3h / 3600) / area_campana_m2

# 3. Pérdidas
d_m_inst = diam_principal_instalado_mm / 1000
ld_dict = {"Codo": 25, "Union Y": 20, "Campana": 30}
total_codos = n_codos_ppal + (n_ramales * codos_por_ramal)
long_virtual = (long_ducto_ppal + (n_ramales * long_ramal_m)) + (total_codos * ld_dict["Codo"] * d_m_inst)
f = 0.022 
p_friccion_pa = (f * long_virtual / d_m_inst) * (0.5 * densidad_aire * v_real_principal_ms**2)
total_perdidas_inH2O = (p_friccion_pa / 249.08) + dp_filtro

# 4. Mangas
area_f = n_mangas_act * (math.pi * (diam_manga/1000) * (largo_manga/1000))
relacion_at = caudal_total_m3h / (area_f * 60)
mangas_nec = math.ceil(caudal_total_m3h / (1.0 * 60 * (math.pi * (diam_manga/1000) * (largo_manga/1000))))

# --- INTERFAZ DE RESULTADOS ---

# TABLA COMPARATIVA REQUERIDA
st.subheader("📋 Resumen Comparativo: Real vs Ideal")
data_comp = {
    "Parámetro": ["Ø Ducto Principal", "Velocidad en Campana", "Velocidad en Ducto Principal", "Número de Mangas", "Caudal Necesario"],
    "Unidad": ["mm", "m/s", "m/s", "u", "m³/h"],
    "Valor Real (Instalado)": [f"{diam_principal_instalado_mm}", f"{v_captacion_ms:.2f}", f"{v_real_principal_ms:.2f}", f"{n_mangas_act}", f"{caudal_total_m3h:.0f}"],
    "Valor Ideal (Diseño)": [f"{diam_ideal_mm:.0f}", "5.00 - 10.00", f"{v_transp_target:.2f}", f"{mangas_nec}", f"{caudal_ideal_m3h:.0f}"]
}
st.table(pd.DataFrame(data_comp))

# GRÁFICA DEL VENTILADOR
st.subheader("📈 Curva de Operación del Sistema")
q_range = np.linspace(100, cfm_entrada * 1.4, 50)
k = total_perdidas_inH2O / (cfm_entrada**2)
curva_resistencia = k * (q_range**2)

fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(q_range, curva_resistencia, label="Resistencia Sistema", color="#00FFAA", lw=2)
ax.axhline(y=sp_ventilador, color='red', linestyle='--', label="Límite Ventilador")
ax.scatter([cfm_entrada], [total_perdidas_inH2O], color='yellow', s=100, zorder=5, label="Punto Operación")
ax.set_xlabel("Caudal (CFM)")
ax.set_ylabel("Presión (in H2O)")
ax.legend()
st.pyplot(fig)

# MÉTRICAS ADICIONALES
st.subheader("📊 Análisis de Energía y Diagnóstico")
res1, res2, res3 = st.columns(3)
res1.metric("Resistencia Total", f"{total_perdidas_inH2O:.2f} inH2O")
hp_op = (cfm_entrada * total_perdidas_inH2O) / (6356 * eficiencia_fan)
res2.metric("Potencia Requerida", f"{hp_op:.1f} HP")
balance = sp_ventilador - total_perdidas_inH2O
res3.metric("Balance de Presión", f"{balance:.2f} inH2O", delta=f"{balance:.2f}")

if balance < 0:
    st.error(f"❌ **FALLO:** El ventilador no vence la resistencia. Velocidad real de transporte será menor a {v_real_principal_ms:.2f} m/s.")
else:
    st.success("✅ **SISTEMA OPERATIVO:** El ventilador cumple con la demanda de la red.")
