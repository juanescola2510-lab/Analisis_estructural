import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Simulador Dinámico Clinker", layout="wide")

st.title("🌪️ Succión Dinámica: Simulación de Obstrucción y Taponamiento")
st.markdown("---")

# --- BARRA LATERAL ---
st.sidebar.header("📊 Configuración del Sistema")

with st.sidebar.expander("Ventilador y Entorno", expanded=True):
    cfm_nominal = st.sidebar.number_input("Caudal Nominal Ventilador (CFM)", value=7600)
    sp_ventilador = st.sidebar.number_input("Presión Máxima (in H2O)", value=10.0)
    eficiencia_fan = st.sidebar.slider("Eficiencia (%)", 40, 90, 65) / 100
    altitud = st.sidebar.number_input("Altitud (msnm)", value=2500)
    v_transp_target = st.sidebar.slider("Velocidad Objetivo (m/s)", 20, 40, 25)

# --- NUEVO: MODO TAPONAMIENTO ---
st.sidebar.markdown("### 🛑 Modo Taponamiento (Obstrucción)")
pct_obstruccion = st.sidebar.slider("% de Obstrucción en Ducto Principal", 0, 90, 0, help="Simula la acumulación de clinker que reduce el área de paso")

with st.sidebar.expander("Línea Principal"):
    diam_ppal_mm = st.number_input("Ø Ducto Principal (mm)", value=400)
    long_ppal = st.number_input("Longitud Línea Principal (m)", value=15.0)
    n_codos_ppal = st.number_input("Codos en Línea Principal", value=2)
    
    st.markdown("**Boca Principal**")
    diam_boca_ppal = st.number_input("Ø Boca Principal (mm)", value=500)
    area_c_ppal = math.pi * (diam_boca_ppal / 1000)**2 / 4

# --- RAMALES INDEPENDIENTES ---
st.sidebar.markdown("### 🛠️ Configuración de Ramales")
n_ramales = st.sidebar.number_input("Número de Ramales", min_value=1, max_value=20, value=2)

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
        datos_ramales.append({"id": i+1, "diam": d_r, "long": l_r, "codos": c_r, "area_c": a_camp})

with st.sidebar.expander("Filtro de Mangas"):
    n_mangas_act = st.number_input("Número de Mangas", value=120)
    diam_manga = st.number_input("Ø Manga (mm)", value=120)
    largo_manga = st.number_input("Largo Manga (mm)", value=2115)
    dp_filtro_limpio = st.number_input("DP Filtro (in H2O)", value=4.0)

# --- LÓGICA DE CÁLCULO DINÁMICO ---
densidad_aire = 1.225 * math.exp(-altitud / 8500)

# 1. Ajuste de área por obstrucción
area_nominal_ppal = math.pi * (diam_ppal_mm / 1000)**2 / 4
area_real_ppal = area_nominal_ppal * (1 - pct_obstruccion / 100)

# 2. Resistencia incrementada (La obstrucción aumenta la velocidad local y la fricción)
# k_obs representa la pérdida por el cambio de sección del tapón
k_obs = (pct_obstruccion / 10)**2 if pct_obstruccion > 0 else 0
v_en_obstruccion = (cfm_nominal * 1.699 / 3600) / area_real_ppal

presion_friccion_pa = (0.022 * long_ppal / (diam_ppal_mm/1000)) * (0.5 * densidad_aire * v_en_obstruccion**2)
perdida_total_inH2O = (presion_friccion_pa / 249.08) + dp_filtro_limpio + (k_obs * 0.5 * densidad_aire * v_en_obstruccion**2 / 249.08)

# 3. Ajuste de Caudal Real del Ventilador
# A mayor resistencia, el ventilador entrega menos CFM
factor_caudal = math.sqrt(max(0.05, sp_ventilador / perdida_total_inH2O)) if perdida_total_inH2O > sp_ventilador else 1.0
caudal_real_m3h = cfm_nominal * 1.699 * factor_caudal
caudal_por_ramal = caudal_real_m3h / n_ramales

# 4. Velocidades Resultantes
resumen_final = []
for r in datos_ramales:
    area_ducto_r = math.pi * (r["diam"]/1000)**2 / 4
    v_cap = (caudal_por_ramal / 3600) / r["area_c"]
    v_tra = (caudal_por_ramal / 3600) / area_ducto_r
    resumen_final.append({
        "Ramal": f"#{r['id']}",
        "Ø Ducto (mm)": r['diam'],
        "V. Captación (m/s)": f"{v_cap:.2f}",
        "V. Transporte (m/s)": f"{v_tra:.2f}",
        "Estado": "✅ OK" if v_tra >= v_transp_target else "🚨 SEDIMENTANDO"
    })

# --- INTERFAZ DE RESULTADOS ---

if pct_obstruccion > 0:
    st.warning(f"⚠️ **SIMULACIÓN DE TAPONAMIENTO ACTIVA:** El ducto principal está obstruido al {pct_obstruccion}%.")

# Métricas Clave
c1, c2, c3, c4 = st.columns(4)
c1.metric("Caudal Real Sistema", f"{caudal_real_m3h:.0f} m³/h", delta=f"{caudal_real_m3h - (cfm_nominal*1.699):.0f}")
c2.metric("V. Principal (Real)", f"{(caudal_real_m3h/3600)/area_real_ppal:.2f} m/s")
c3.metric("Resistencia Total", f"{perdida_total_inH2O:.2f} inH2O")
c4.metric("Potencia Requerida", f"{(caudal_real_m3h/1.699 * perdida_total_inH2O)/(6356*eficiencia_fan):.1f} HP")

st.subheader("📋 Velocidad en Campanas de Ramales (Efecto del Taponamiento)")
st.dataframe(pd.DataFrame(resumen_final), use_container_width=True)

# Sección de Mangas (Sin cambios)
area_total_f = n_mangas_act * (math.pi * (diam_manga/1000) * (largo_manga/1000))
relacion_at = caudal_real_m3h / (area_total_f * 60)
st.subheader("🧵 Capacidad del Filtro de Mangas")
st.write(f"Con el caudal actual, la Relación Aire/Tela es de: **{relacion_at:.2f} m/min**.")

# Diagnóstico Final
if factor_caudal < 0.8:
    st.error("🚨 **SISTEMA COLAPSADO:** La obstrucción en el ducto principal ha reducido el caudal a niveles críticos. La succión en los ramales es insuficiente.")
elif pct_obstruccion > 30:
    st.info("💡 **Dato Técnico:** Las acumulaciones de clinker suelen ser autoperpetuantes; al bajar la velocidad por el tapón, más material se cae en el mismo lugar.")
