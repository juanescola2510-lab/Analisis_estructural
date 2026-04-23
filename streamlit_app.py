import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Simulador Succión Clinker Pro - Potencia Máxima", layout="wide")

st.title("🌪️ Ingeniería de Succión: Análisis de Carga de Motor y Ramales")
st.markdown("---")

# --- BARRA LATERAL ---
st.sidebar.header("📊 Configuración del Sistema")

with st.sidebar.expander("Ficha Técnica Ventilador (Imagen)", expanded=True):
    cfm_nominal = st.sidebar.number_input("Caudal Nominal (CFM)", value=7600)
    sp_ventilador = st.sidebar.number_input("Presión de Diseño (in H2O)", value=17.0, help="Calculado base 30HP")
    hp_motor_placa = st.sidebar.number_input("Potencia Motor Placa (HP)", value=30.0)
    eficiencia_fan = st.sidebar.slider("Eficiencia (%)", 40, 90, 65) / 100
    altitud = st.sidebar.number_input("Altitud (msnm)", value=2500)
    v_transp_target = st.sidebar.slider("Velocidad Transporte Objetivo (m/s)", 20, 40, 25)

# --- MODO TAPONAMIENTO ---
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
        wp, hp = st.number_input("Ancho (mm)", 600), st.number_input("Alto (mm)", 400)
        area_c_ppal = (wp/1000) * (hp/1000)

# --- CONFIGURACIÓN DE RAMALES ---
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
    n_mangas_act = st.number_input("Número de Mangas", value=120)
    diam_manga = st.number_input("Ø Manga (mm)", value=120)
    largo_manga = st.number_input("Largo Manga (mm)", value=2115)
    dp_filtro = st.number_input("DP Filtro Promedio (in H2O)", value=5.0)

# --- LÓGICA DE CÁLCULO ---
densidad_aire = 1.225 * math.exp(-altitud / 8500)

def calcular_desempeno(obs_pct, num_ram):
    area_nominal = math.pi * (diam_ppal_mm / 1000)**2 / 4
    area_real = area_nominal * (1 - obs_pct / 100)
    v_teorica = (cfm_nominal * 1.699 / 3600) / area_real
    p_fric = (0.022 * long_ppal / (diam_ppal_mm/1000)) * (0.5 * densidad_aire * v_teorica**2)
    k_obs = (obs_pct/10)**2 if obs_pct > 0 else 0
    p_total = (p_fric / 249.08) + dp_filtro + (k_obs * 0.5 * densidad_aire * v_teorica**2 / 249.08)
    
    # Efecto de más ramales: Menor resistencia total pero más demanda de aire
    p_total_final = p_total / (1 + (num_ram - 2) * 0.1) # Simplificación física
    factor = math.sqrt(max(0.05, sp_ventilador / p_total_final)) if p_total_final > sp_ventilador else 1.0
    q_final = cfm_nominal * 1.699 * factor * (1 + (num_ram - 2) * 0.15)
    
    return q_final, p_total_final, area_real

q_actual_m3h, p_actual_in, area_real_ppal = calcular_desempeno(pct_obstruccion, n_ramales)
hp_req = (q_actual_m3h / 1.699 * p_actual_in) / (6356 * eficiencia_fan)

# --- INTERFAZ DE RESULTADOS ---

# 1. ANALISIS DE SOBRECARGA (NUEVO)
st.subheader("⚡ Análisis de Carga del Motor")
pct_carga_motor = (hp_req / hp_motor_placa) * 100

c_hp1, c_hp2, c_hp3 = st.columns(3)
c_hp1.metric("Potencia Demandada", f"{hp_req:.1f} HP")
c_hp2.metric("Capacidad Motor", f"{hp_motor_placa} HP")
c_hp3.metric("Carga del Motor", f"{pct_carga_motor:.1f}%")

if pct_carga_motor > 100:
    st.error(f"🚨 **SOBRECARGA CRÍTICA:** Al tener {n_ramales} ramales abiertos, el motor requiere {hp_req:.1f} HP. Tu motor de {hp_motor_placa} HP se va a QUEMAR.")
elif pct_carga_motor > 90:
    st.warning("⚠️ **MOTOR AL LÍMITE:** Estás usando casi toda la potencia. Evita abrir más ramales.")
else:
    st.success("✅ **MOTOR SEGURO:** La configuración actual de ramales está dentro de la capacidad de 30 HP.")

# 2. TABLA COMPARATIVA (REINTEGRADA)
st.subheader("📋 Resumen Comparativo: Real vs Ideal")
mangas_nec = math.ceil(q_actual_m3h / (1.0 * 60 * (math.pi * (diam_manga/1000) * (largo_manga/1000))))
data_comp = {
    "Parámetro": ["Ø Ducto Principal", "V. Captación Campana Ppal", "V. Transporte Principal", "Número de Mangas", "Caudal Total"],
    "Unidad": ["mm", "m/s", "m/s", "u", "m³/h"],
    "Valor Real (Actual)": [f"{diam_ppal_mm}", f"{(q_actual_m3h/3600)/area_c_ppal:.2f}", f"{(q_actual_m3h/3600)/area_real_ppal:.2f}", f"{n_mangas_act}", f"{q_actual_m3h:.0f}"],
    "Valor Ideal (Diseño)": [f"{math.sqrt(4*((q_actual_m3h/3600)/v_transp_target)/math.pi)*1000:.0f}", "10.0 - 15.0", f"{v_transp_target:.2f}", f"{mangas_nec}", f"{v_transp_target * (math.pi*(diam_ppal_mm/1000)**2/4)*3600:.0f}"]
}
st.table(pd.DataFrame(data_comp))

# 3. TABLA DE RAMALES
resumen_r = []
for r in datos_ramales:
    v_cap = (q_actual_m3h / n_ramales / 3600) / r["area_c"]
    v_tra = (q_actual_m3h / n_ramales / 3600) / (math.pi * (r["diam"]/1000)**2 / 4)
    resumen_r.append({"Ramal": f"#{r['id']}", "V. Captación (m/s)": f"{v_cap:.2f}", "V. Transporte (m/s)": f"{v_tra:.2f}", "Estado": "✅ OK" if v_tra >= v_transp_target else "🚨 SEDIMENTANDO"})
st.subheader("🌿 Detalle de Velocidades por Ramal")
st.dataframe(pd.DataFrame(resumen_r), use_container_width=True)

# 4. GRÁFICAS
st.subheader("📈 Análisis de Curvas y Tendencias")
g1, g2 = st.columns(2)
with g1: # GRÁFICA DEL VENTILADOR
    q_plot = np.linspace(100, cfm_nominal * 1.5, 50)
    k = p_actual_in / (q_actual_m3h/1.699)**2
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.plot(q_plot, k*(q_plot**2), color="#00FFAA", label="Resistencia Actual")
    ax1.axhline(y=sp_ventilador, color='red', linestyle='--', label="SP Ventilador")
    ax1.scatter([q_actual_m3h/1.699], [p_actual_in], color='yellow', s=100, zorder=5)
    ax1.set_xlabel("CFM"); ax1.set_ylabel("in H2O"); ax1.legend(); st.pyplot(fig1)

with g2: # TENDENCIA DE VELOCIDAD
    obs_range = np.linspace(0, 90, 20)
    v_t = []
    for o in obs_range:
        q_sim, _, _ = calcular_desempeno(o, n_ramales)
        v_t.append((q_sim / n_ramales / 3600) / datos_ramales["area_c"])
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.plot(obs_range, v_t, color="orange", lw=3)
    ax2.axvline(x=pct_obstruccion, color='white', linestyle=':')
    ax2.set_xlabel("% Obstrucción Principal"); ax2.set_ylabel("V. Campana (m/s)"); st.pyplot(fig2)
