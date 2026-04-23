import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Ingeniería de Succión Clinker", layout="wide")

st.title("🌪️ Diagnóstico Pro: Resistencia Acumulativa por Ramales")
st.markdown("---")

# --- BARRA LATERAL ---
st.sidebar.header("📊 Datos del Sistema")

with st.sidebar.expander("Ficha Técnica Ventilador", expanded=True):
    cfm_nominal = st.sidebar.number_input("Caudal Nominal (CFM)", value=7600)
    sp_ventilador = st.sidebar.number_input("Presión Máxima (in H2O)", value=17.0)
    hp_motor_placa = st.sidebar.number_input("Potencia Motor Placa (HP)", value=30.0)
    eficiencia_fan = st.sidebar.slider("Eficiencia (%)", 40, 90, 65) / 100
    altitud = st.sidebar.number_input("Altitud (msnm)", value=2500)
    v_transp_target = st.sidebar.slider("Velocidad Transporte Objetivo (m/s)", 20, 40, 25)

st.sidebar.markdown("### 🛑 Simulación de Obstrucción")
pct_obstruccion = st.sidebar.slider("% Obstrucción Principal", 0, 90, 0)

with st.sidebar.expander("Línea Principal (Hardox)"):
    diam_ppal_mm = st.number_input("Ø Ducto Principal (mm)", value=400)
    long_ppal = st.number_input("Longitud Principal (m)", value=15.0)
    n_codos_ppal = st.number_input("Codos Línea Principal", value=2)
    
    st.markdown("**Boca de Línea Principal**")
    diam_boca_ppal = st.number_input("Ø Boca Principal (mm)", value=500)
    area_c_ppal = math.pi * (diam_boca_ppal / 1000)**2 / 4

st.sidebar.markdown("### 🛠️ Ramales (Suman Resistencia)")
n_ramales = st.sidebar.number_input("Número de Ramales Abiertos", min_value=1, value=2)

datos_ramales = []
for i in range(n_ramales):
    with st.sidebar.expander(f"Ramal #{i+1}", expanded=False):
        d_r = st.number_input(f"Ø Ducto Ramal {i+1} (mm)", value=150, key=f"dr_{i}")
        l_r = st.number_input(f"Longitud Ramal {i+1} (m)", value=3.0, key=f"lr_{i}")
        c_r = st.number_input(f"N° Codos R{i+1}", value=2, key=f"cr_{i}")
        a_r = st.number_input(f"Ø Boca R{i+1} (mm)", value=250, key=f"dc_{i}")
        area_c = math.pi * (a_r / 1000)**2 / 4
        datos_ramales.append({"id": i+1, "diam": d_r, "long": l_r, "codos": c_r, "area_c": area_c})

with st.sidebar.expander("Filtro de Mangas"):
    n_mangas_act = st.number_input("Número de Mangas", value=120)
    diam_manga = st.number_input("Ø Manga (mm)", value=120)
    largo_manga = st.number_input("Largo Manga (mm)", value=2115)
    dp_filtro = st.number_input("DP Filtro (in H2O)", value=5.0)

# --- LÓGICA DE CÁLCULO MEJORADA (RESISTENCIA SUMATORIA) ---
densidad_aire = 1.225 * math.exp(-altitud / 8500)

def calcular_sistema_total(obs_pct):
    # 1. Resistencia Línea Principal
    d_m_ppal = diam_ppal_mm / 1000
    area_nom_ppal = math.pi * (d_m_ppal**2) / 4
    area_real_ppal = area_nom_ppal * (1 - obs_pct / 100)
    v_ppal = (cfm_nominal * 1.699 / 3600) / max(0.01, area_real_ppal)
    
    # Pérdida fricción principal + codos + obstrucción
    le_ppal = long_ppal + (n_codos_ppal * 25 * d_m_ppal)
    p_ppal_pa = (0.022 * le_ppal / d_m_ppal) * (0.5 * densidad_aire * v_ppal**2)
    p_obs_pa = ((obs_pct/10)**2 * 0.5 * densidad_aire * v_ppal**2) if obs_pct > 0 else 0
    
    # 2. Resistencia Acumulada de Ramales (SUMATORIA)
    p_ramales_pa = 0
    for r in datos_ramales:
        d_m_r = r["diam"] / 1000
        v_r = ( (cfm_nominal * 1.699 / n_ramales) / 3600) / (math.pi * d_m_r**2 / 4)
        # Cada ramal tiene su fricción, sus codos y una entrada "Y" (20D)
        le_r = r["long"] + (r["codos"] * 25 * d_m_r) + (20 * d_m_r) 
        p_ramales_pa += (0.022 * le_r / d_m_r) * (0.5 * densidad_aire * v_r**2)
    
    # Resistencia Total = Principal + Ramales (Promedio de caída) + Filtro
    p_total_in = ((p_ppal_pa + p_obs_pa + (p_ramales_pa / n_ramales)) / 249.08) + dp_filtro
    
    # Ajuste de caudal por pérdida de carga
    f_q = math.sqrt(max(0.05, sp_ventilador / p_total_in)) if p_total_in > sp_ventilador else 1.0
    return cfm_nominal * 1.699 * f_q, p_total_in, area_real_ppal

q_real_m3h, p_real_in, a_real_ppal = calcular_sistema_total(pct_obstruccion)
hp_req = (q_real_m3h / 1.699 * p_real_in) / (6356 * eficiencia_fan)
v_real_ppal = (q_real_m3h / 3600) / a_real_ppal

# --- INTERFAZ ---
tab1, tab2 = st.tabs(["📊 Diagnóstico y Gráficas", "💡 Recomendaciones Técnicas"])

with tab1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Carga Motor", f"{(hp_req/hp_motor_placa)*100:.1f}%")
    c2.metric("Caudal Real", f"{q_real_m3h:.0f} m³/h")
    c3.metric("Resistencia Total", f"{p_real_in:.2f} in H2O")

    st.subheader("📋 Resumen Real vs Ideal")
    mangas_nec = math.ceil(q_real_m3h / (1.0 * 60 * (math.pi * (diam_manga/1000) * (largo_manga/1000))))
    st.table(pd.DataFrame({
        "Parámetro": ["V. Transporte Ppal", "Resistencia del Sistema", "Mangas Requeridas", "Caudal Sistema"],
        "Real": [f"{v_real_ppal:.2f} m/s", f"{p_real_in:.2f} inH2O", f"{n_mangas_act}", f"{q_real_m3h:.0f} m³/h"],
        "Ideal": [f"{v_transp_target} m/s", f"< {sp_ventilador} inH2O", f"{mangas_nec}", f"{cfm_nominal*1.699:.0f} m³/h"]
    }))

    st.subheader("📈 Curva de Operación")
    q_plot = np.linspace(100, cfm_nominal * 1.5, 50)
    k = p_real_in / (q_real_m3h/1.699)**2
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(q_plot, k*(q_plot**2), color="#00FFAA", label="Resistencia (Sumando Ramales)")
    ax1.axhline(y=sp_ventilador, color='red', linestyle='--', label="Capacidad Ventilador")
    ax1.scatter([q_real_m3h/1.699], [p_real_in], color='yellow', s=100, zorder=5)
    st.pyplot(fig1)

with tab2:
    st.subheader("🚀 Plan de Mejora")
    if p_real_in > sp_ventilador:
        st.error(f"⚠️ **SISTEMA AHOGADO:** La resistencia ({p_real_in:.2f}) supera al ventilador. Cada ramal extra está 'frenando' el aire.")
    if hp_req > hp_motor_placa:
        st.error(f"⚠️ **MOTOR:** Peligro de quemadura. Necesitas un motor de **{hp_req*1.15:.0f} HP**.")
    
    area_nec_camp = (q_real_m3h / n_ramales / 3600) / 12
    st.info(f"📢 **DISEÑO CAMPANA:** Para 12 m/s, usa bocas de **Ø {math.sqrt(4*area_nec_camp/math.pi)*1000:.0f} mm**.")
    
    if v_real_ppal < v_transp_target:
        st.warning(f"📐 **DUCTOS:** Velocidad insuficiente ({v_real_ppal:.2f} m/s). El clinker se va a asentar.")
