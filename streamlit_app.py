import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Simulador Succión Clinker Pro - Diseño Ideal", layout="wide")

st.title("🌪️ Ingeniería de Succión: Diseño de Campanas y Carga de Motor")
st.markdown("---")

# --- BARRA LATERAL ---
st.sidebar.header("📊 Configuración del Sistema")

with st.sidebar.expander("Ficha Técnica Ventilador", expanded=True):
    cfm_nominal = st.sidebar.number_input("Caudal Nominal (CFM)", value=7600)
    sp_ventilador = st.sidebar.number_input("Presión de Diseño (in H2O)", value=17.0)
    hp_motor_placa = st.sidebar.number_input("Potencia Motor Placa (HP)", value=30.0)
    eficiencia_fan = st.sidebar.slider("Eficiencia (%)", 40, 90, 65) / 100
    altitud = st.sidebar.number_input("Altitud (msnm)", value=2500)
    v_transp_target = st.sidebar.slider("Velocidad Transporte Objetivo (m/s)", 20, 40, 25)

st.sidebar.markdown("### 🛑 Simulación de Obstrucción")
pct_obstruccion = st.sidebar.slider("% Obstrucción en Ducto Principal", 0, 90, 0)

with st.sidebar.expander("Línea Principal (Hardox)"):
    diam_ppal_mm = st.number_input("Ø Ducto Principal (mm)", value=400)
    long_ppal = st.number_input("Longitud Línea Principal (m)", value=15.0)
    n_codos_ppal = st.number_input("Codos en Línea Principal", value=2)
    
    st.markdown("**Boca de Línea Principal**")
    tipo_c_ppal = st.radio("Forma Boca Ppal", ["Circular", "Rectangular"])
    if tipo_c_ppal == "Circular":
        dc_ppal = st.number_input("Ø Boca Ppal (mm)", value=500)
        area_c_ppal = math.pi * (dc_ppal / 1000)**2 / 4
    else:
        wp, hp_b = st.number_input("Ancho (mm)", 600), st.number_input("Alto (mm)", 400)
        area_c_ppal = (wp/1000) * (hp_b/1000)

st.sidebar.markdown("### 🛠️ Configuración de Ramales")
n_ramales = st.sidebar.number_input("Número de Ramales Abiertos", min_value=1, value=2)

datos_ramales = []
for i in range(n_ramales):
    with st.sidebar.expander(f"Ramal #{i+1}", expanded=False):
        d_r = st.number_input(f"Ø Ducto Ramal {i+1} (mm)", value=150, key=f"dr_{i}")
        l_r = st.number_input(f"Longitud Ramal {i+1} (m)", value=3.0, key=f"lr_{i}")
        c_r = st.number_input(f"N° Codos R{i+1}", value=2, key=f"cr_{i}")
        
        tipo_c = st.selectbox(f"Tipo Campana R{i+1}", ["Circular", "Rectangular"], key=f"tc_{i}")
        if tipo_c == "Circular":
            dc = st.number_input(f"Ø Boca R{i+1} (mm)", value=250, key=f"dc_{i}")
            a_camp = math.pi * (dc / 1000)**2 / 4
        else:
            w_c, h_c = st.number_input(f"Ancho (mm)", 300, key=f"wc_{i}"), st.number_input(f"Alto (mm)", 200, key=f"hc_{i}")
            a_camp = (w_c/1000) * (h_c/1000)
        datos_ramales.append({"id": i+1, "diam": d_r, "long": l_r, "area_c": a_camp})

with st.sidebar.expander("Filtro de Mangas"):
    n_mangas_act = st.number_input("Número de Mangas Instaladas", value=120)
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
hp_requerido = (q_actual_m3h / 1.699 * p_actual_in) / (6356 * eficiencia_fan)
porcentaje_carga = (hp_requerido / hp_motor_placa) * 100

# --- INTERFAZ DE RESULTADOS ---

# 1. ESTADO DE MOTOR
st.subheader("⚡ Estado de Carga del Motor")
c_hp1, c_hp2, c_hp3 = st.columns(3)
c_hp1.metric("Potencia en Uso", f"{hp_requerido:.1f} HP")
c_hp2.metric("Límite Motor", f"{hp_motor_placa} HP")
c_hp3.metric("CARGA", f"{porcentaje_carga:.1f}%")

# 2. CALCULADOR DE DIMENSIÓN IDEAL (NUEVO)
st.subheader("📐 Recomendador de Dimensiones de Campana")
st.markdown("Si deseas una velocidad específica en la boca, estas deberían ser las medidas:")
v_deseada = st.slider("Selecciona Velocidad de Captación Deseada (m/s)", 5, 25, 12)
q_por_ramal = q_actual_m3h / n_ramales
area_necesaria = (q_por_ramal / 3600) / v_deseada
diam_sugerido = math.sqrt(4 * area_necesaria / math.pi) * 1000

col_i1, col_i2 = st.columns(2)
col_i1.info(f"**Para Campana Circular:** Ø {diam_sugerido:.0f} mm")
col_i2.info(f"**Para Campana Rectangular:** {math.sqrt(area_necesaria)*1000:.0f} x {math.sqrt(area_necesaria)*1000:.0f} mm")

# 3. TABLA COMPARATIVA
st.subheader("📋 Resumen Comparativo")
data_comp = {
    "Parámetro": ["Ø Ducto Principal", "V. Captación Campana Ppal", "V. Transporte Principal", "Caudal Sistema"],
    "Unidad": ["mm", "m/s", "m/s", "m³/h"],
    "Valor Real": [f"{diam_ppal_mm}", f"{(q_actual_m3h/3600)/area_c_ppal:.2f}", f"{(q_actual_m3h/3600)/area_real_ppal:.2f}", f"{q_actual_m3h:.0f}"],
    "Valor Ideal": [f"{math.sqrt(4*((q_actual_m3h/3600)/v_transp_target)/math.pi)*1000:.0f}", f"{v_deseada}.00", f"{v_transp_target:.2f}", f"{v_transp_target*(math.pi*(diam_ppal_mm/1000)**2/4)*3600:.0f}"]
}
st.table(pd.DataFrame(data_comp))

# 4. TABLA DE RAMALES
resumen_r = []
for r in datos_ramales:
    v_cap = (q_por_ramal / 3600) / r["area_c"]
    v_tra = (q_por_ramal / 3600) / (math.pi * (r["diam"]/1000)**2 / 4)
    resumen_r.append({"Ramal": f"#{r['id']}", "V. Captación (m/s)": f"{v_cap:.2f}", "V. Transporte (m/s)": f"{v_tra:.2f}"})
st.subheader("🌿 Detalle Individual")
st.dataframe(pd.DataFrame(resumen_r), use_container_width=True)

# 5. GRÁFICAS
g1, g2 = st.columns(2)
with g1:
    q_plot = np.linspace(100, cfm_nominal * 1.5, 50)
    k_val = p_actual_in / (q_actual_m3h/1.699)**2
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.plot(q_plot, k_val*(q_plot**2), color="#00FFAA", label="Resistencia")
    ax1.axhline(y=sp_ventilador, color='red', linestyle='--', label="SP Ventilador")
    ax1.scatter([q_actual_m3h/1.699], [p_actual_in], color='yellow', s=100)
    ax1.legend(); st.pyplot(fig1)
with g2:
    obs_range = np.linspace(0, 90, 20)
    v_t = [(calcular_sistema(o, n_ramales)[0] / n_ramales / 3600) / area_necesaria for o in obs_range]
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.plot(obs_range, v_t, color="orange", lw=3)
    ax2.set_xlabel("% Obstrucción"); ax2.set_ylabel("V. Captación (m/s)"); st.pyplot(fig2)
