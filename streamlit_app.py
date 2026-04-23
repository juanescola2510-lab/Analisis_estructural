import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Simulador Dinámico Clinker - Taponamiento", layout="wide")

st.title("🌪️ Succión Crítica: Simulación de Taponamiento y Análisis de Curvas")
st.markdown("---")

# --- BARRA LATERAL ---
st.sidebar.header("📊 Configuración del Sistema")

with st.sidebar.expander("Ventilador y Entorno", expanded=True):
    cfm_nominal = st.sidebar.number_input("Caudal Nominal Ventilador (CFM)", value=7600)
    sp_ventilador = st.sidebar.number_input("Presión Máxima (in H2O)", value=10.0)
    eficiencia_fan = st.sidebar.slider("Eficiencia (%)", 40, 90, 65) / 100
    altitud = st.sidebar.number_input("Altitud (msnm)", value=2500)
    v_transp_target = st.sidebar.slider("Velocidad Objetivo (m/s)", 20, 40, 25)

# --- MODO TAPONAMIENTO ---
st.sidebar.markdown("### 🛑 Simulación de Obstrucción")
pct_obstruccion = st.sidebar.slider("% Obstrucción en Ducto Principal", 0, 90, 0)

with st.sidebar.expander("Línea Principal"):
    diam_ppal_mm = st.number_input("Ø Ducto Principal (mm)", value=400)
    long_ppal = st.number_input("Longitud Línea Principal (m)", value=15.0)
    n_codos_ppal = st.number_input("Codos en Línea Principal", value=2)
    
    st.markdown("**Boca Principal**")
    diam_boca_ppal = st.number_input("Ø Boca Principal (mm)", value=500)
    area_c_ppal = math.pi * (diam_boca_ppal / 1000)**2 / 4

# --- RAMALES ---
st.sidebar.markdown("### 🛠️ Configuración de Ramales")
n_ramales = st.sidebar.number_input("Número de Ramales", min_value=1, value=2)

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
            w_c = st.number_input(f"Ancho R{i+1} (mm)", value=300, key=f"wc_{i}")
            h_c = st.number_input(f"Alto R{i+1} (mm)", value=200, key=f"hc_{i}")
            a_camp = (w_c / 1000) * (h_c / 1000)
        datos_ramales.append({"id": i+1, "diam": d_r, "long": l_r, "area_c": a_camp})

with st.sidebar.expander("Filtro de Mangas"):
    n_mangas_act = st.number_input("Número de Mangas", value=120)
    diam_manga = st.number_input("Ø Manga (mm)", value=120)
    largo_manga = st.number_input("Largo Manga (mm)", value=2115)
    dp_filtro = st.number_input("DP Filtro (in H2O)", value=4.0)

# --- LÓGICA DE CÁLCULO ---
densidad_aire = 1.225 * math.exp(-altitud / 8500)

def calcular_sistema(obs_pct):
    area_real = (math.pi * (diam_ppal_mm / 1000)**2 / 4) * (1 - obs_pct / 100)
    v_base = (cfm_nominal * 1.699 / 3600) / area_real
    p_fric = (0.022 * long_ppal / (diam_ppal_mm/1000)) * (0.5 * densidad_aire * v_base**2)
    p_total = (p_fric / 249.08) + dp_filtro + ((obs_pct/10)**2 * 0.5 * densidad_aire * v_base**2 / 249.08 if obs_pct > 0 else 0)
    f_caudal = math.sqrt(max(0.05, sp_ventilador / p_total)) if p_total > sp_ventilador else 1.0
    q_real = cfm_nominal * 1.699 * f_caudal
    return q_real, p_total

q_actual, p_actual = calcular_sistema(pct_obstruccion)
q_por_ramal = q_actual / n_ramales

# --- RESULTADOS ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Caudal Real", f"{q_actual:.0f} m³/h")
c2.metric("Pérdida Sistema", f"{p_actual:.2f} inH2O")
c3.metric("Relación Aire/Tela", f"{q_actual / (n_mangas_act * math.pi * (diam_manga/1000) * (largo_manga/1000) * 60):.2f}")
c4.metric("Potencia", f"{(q_actual/1.699 * p_actual)/(6356*eficiencia_fan):.1f} HP")

# TABLA DE RAMALES
resumen = []
for r in datos_ramales:
    v_cap = (q_por_ramal / 3600) / r["area_c"]
    v_tra = (q_por_ramal / 3600) / (math.pi * (r["diam"]/1000)**2 / 4)
    resumen.append({"Ramal": f"#{r['id']}", "V. Captación (m/s)": f"{v_cap:.2f}", "V. Transporte (m/s)": f"{v_tra:.2f}", "Estado": "✅ OK" if v_tra >= v_transp_target else "🚨 SEDIMENTANDO"})
st.subheader("📋 Velocidad en Campanas y Ramales")
st.dataframe(pd.DataFrame(resumen), use_container_width=True)

# --- GRÁFICAS ---
st.subheader("📈 Análisis de Comportamiento")
g1, g2 = st.columns(2)

with g1: # GRÁFICA DEL VENTILADOR (NO BORRADA)
    st.markdown("**Curva del Ventilador vs Resistencia**")
    q_plot = np.linspace(100, cfm_nominal * 1.5, 50)
    k_actual = p_actual / (q_actual/1.699)**2
    curva_res = k_actual * (q_plot**2)
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(q_plot, curva_res, color="#00FFAA", label="Resistencia (con Taponamiento)")
    ax1.axhline(y=sp_ventilador, color='red', linestyle='--', label="Límite Ventilador")
    ax1.scatter([q_actual/1.699], [p_actual], color='yellow', s=100, zorder=5)
    ax1.set_xlabel("CFM"); ax1.set_ylabel("in H2O"); ax1.legend(); st.pyplot(fig1)

with g2: # GRÁFICA DE TENDENCIA DE VELOCIDAD
    st.markdown("**Caída de Velocidad en Campanas vs Taponamiento**")
    obs_range = np.linspace(0, 90, 20)
    v_tendencia = []
    for o in obs_range:
        q_sim, _ = calcular_sistema(o)
        v_tendencia.append((q_sim / n_ramales / 3600) / datos_ramales[0]["area_c"])
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.plot(obs_range, v_tendencia, color="orange", lw=3)
    ax2.axvline(x=pct_obstruccion, color='white', linestyle=':', label="Obstrucción Actual")
    ax2.set_xlabel("% Obstrucción Principal"); ax2.set_ylabel("V. Captación (m/s)"); ax2.legend(); st.pyplot(fig2)
