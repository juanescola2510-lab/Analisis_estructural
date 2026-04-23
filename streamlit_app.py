import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Ingeniería de Succión Clinker", layout="wide")

st.title("🌪️ Sistema Inteligente de Diagnóstico de Succión")
st.markdown("---")

# --- BARRA LATERAL (ENTRADA DE DATOS) ---
st.sidebar.header("📊 Datos del Sistema")

with st.sidebar.expander("Ficha Técnica Ventilador", expanded=True):
    cfm_nominal = st.sidebar.number_input("Caudal Nominal (CFM)", value=7600)
    sp_ventilador = st.sidebar.number_input("Presión de Diseño (in H2O)", value=17.0)
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

st.sidebar.markdown("### 🛠️ Ramales")
n_ramales = st.sidebar.number_input("Número de Ramales Abiertos", min_value=1, value=2)

datos_ramales = []
for i in range(n_ramales):
    with st.sidebar.expander(f"Ramal #{i+1}", expanded=False):
        d_r = st.number_input(f"Ø Ducto Ramal {i+1} (mm)", value=150, key=f"dr_{i}")
        l_r = st.number_input(f"Longitud Ramal {i+1} (m)", value=3.0, key=f"lr_{i}")
        a_r = st.number_input(f"Ø Boca R{i+1} (mm)", value=250, key=f"dc_{i}")
        area_c = math.pi * (a_r / 1000)**2 / 4
        datos_ramales.append({"id": i+1, "diam": d_r, "long": l_r, "area_c": area_c, "boca_mm": a_r})

with st.sidebar.expander("Filtro de Mangas"):
    n_mangas_act = st.number_input("Número de Mangas", value=120)
    diam_manga = st.number_input("Ø Manga (mm)", value=120)
    largo_manga = st.number_input("Largo Manga (mm)", value=2115)
    dp_filtro = st.number_input("DP Filtro (in H2O)", value=5.0)

# --- LÓGICA DE CÁLCULO ---
densidad_aire = 1.225 * math.exp(-altitud / 8500)

def calcular_sistema(obs_pct, num_ram):
    area_nominal = math.pi * (diam_ppal_mm / 1000)**2 / 4
    area_real = area_nominal * (1 - obs_pct / 100)
    v_base = (cfm_nominal * 1.699 / 3600) / max(0.01, area_real)
    p_fric = (0.022 * long_ppal / (diam_ppal_mm/1000)) * (0.5 * densidad_aire * v_base**2)
    k_obs = (obs_pct/10)**2 if obs_pct > 0 else 0
    p_total = (p_fric / 249.08) + dp_filtro + (k_obs * 0.5 * densidad_aire * v_base**2 / 249.08)
    factor_q = math.sqrt(max(0.05, sp_ventilador / p_total)) if p_total > sp_ventilador else 1.0
    return cfm_nominal * 1.699 * factor_q, p_total, area_real

q_actual_m3h, p_actual_in, area_real_ppal = calcular_sistema(pct_obstruccion, n_ramales)
hp_req = (q_actual_m3h / 1.699 * p_actual_in) / (6356 * eficiencia_fan)
v_real_ppal = (q_actual_m3h / 3600) / area_real_ppal

# --- CREACIÓN DE PESTAÑAS ---
tab1, tab2 = st.tabs(["📊 Diagnóstico y Gráficas", "💡 Recomendaciones Técnicas"])

with tab1:
    # Métricas principales
    c1, c2, c3 = st.columns(3)
    c1.metric("Carga Motor", f"{(hp_req/hp_motor_placa)*100:.1f}%")
    c2.metric("Caudal Real", f"{q_actual_m3h:.0f} m³/h")
    c3.metric("Resistencia", f"{p_actual_in:.2f} in H2O")

    # Tabla Comparativa
    st.subheader("📋 Resumen Comparativo: Real vs Ideal")
    mangas_nec = math.ceil(q_actual_m3h / (1.0 * 60 * (math.pi * (diam_manga/1000) * (largo_manga/1000))))
    data_comp = {
        "Parámetro": ["Ø Ducto Principal", "V. Transporte Principal", "Número de Mangas", "Caudal Total"],
        "Unidad": ["mm", "m/s", "u", "m³/h"],
        "Valor Real": [f"{diam_ppal_mm}", f"{v_real_ppal:.2f}", f"{n_mangas_act}", f"{q_actual_m3h:.0f}"],
        "Valor Ideal": [f"{math.sqrt(4*((q_actual_m3h/3600)/v_transp_target)/math.pi)*1000:.0f}", f"{v_transp_target:.2f}", f"{mangas_nec}", f"{v_transp_target*(math.pi*(diam_ppal_mm/1000)**2/4)*3600:.0f}"]
    }
    st.table(pd.DataFrame(data_comp))

    # Gráfica del Ventilador
    st.subheader("📈 Curva de Operación")
    q_plot = np.linspace(100, cfm_nominal * 1.5, 50)
    k_val = p_actual_in / (q_actual_m3h/1.699)**2
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(q_plot, k_val*(q_plot**2), color="#00FFAA", label="Resistencia Sistema")
    ax1.axhline(y=sp_ventilador, color='red', linestyle='--', label="Límite Ventilador")
    ax1.scatter([q_actual_m3h/1.699], [p_actual_in], color='yellow', s=100, zorder=5)
    ax1.set_xlabel("CFM"); ax1.set_ylabel("in H2O"); ax1.legend(); st.pyplot(fig1)

with tab2:
    st.subheader("🚀 Plan de Mejora para Clinker")
    
    # 1. Recomendación Motor
    if hp_req > hp_motor_placa:
        st.error(f"⚠️ **MOTOR:** Tu motor de {hp_motor_placa}HP está saturado. Necesitas un motor de al menos **{hp_req*1.15:.0f} HP**.")
    else:
        st.success("✅ **MOTOR:** La potencia actual es adecuada para el flujo.")

    # 2. Recomendación Ductos
    if v_real_ppal < v_transp_target - 2:
        st.warning(f"📐 **DUCTOS:** El diámetro de {diam_ppal_mm}mm es muy grande. Reduce a **{math.sqrt(4*((q_actual_m3h/3600)/v_transp_target)/math.pi)*1000:.0f}mm** para evitar taponamientos.")
    elif v_real_ppal > v_transp_target + 8:
        st.warning(f"📐 **DUCTOS:** El ducto es muy pequeño, genera demasiada fricción. Aumenta el diámetro.")

    # 3. Recomendación Campana
    area_nec_camp = (q_actual_m3h / n_ramales / 3600) / 12 # 12 m/s ideal
    st.info(f"📢 **DISEÑO CAMPANA:** Para captar bien el clinker (12 m/s), la boca de tus campanas debería medir **Ø {math.sqrt(4*area_nec_camp/math.pi)*1000:.0f} mm**.")

    # 4. Recomendación Mangas
    if n_mangas_act < mangas_nec:
        st.error(f"🧵 **FILTRO:** Tienes pocas mangas. Debes aumentar a **{mangas_nec} mangas** para no saturar el filtro.")
    else:
        st.success("✅ **FILTRO:** El número de mangas es correcto.")
