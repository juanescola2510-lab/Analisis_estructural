import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Simulador Succión Clinker Pro", layout="wide")

st.title("🌪️ Ingeniería de Succión Detallada: Control Total por Ramal")
st.markdown("---")

# --- BARRA LATERAL ---
st.sidebar.header("📊 Configuración del Sistema")

with st.sidebar.expander("Ventilador y Entorno", expanded=True):
    cfm_entrada = st.sidebar.number_input("Caudal Nominal Ventilador (CFM)", value=7600)
    sp_ventilador = st.sidebar.number_input("Presión Estática de Placa (in H2O)", value=10.0)
    eficiencia_fan = st.sidebar.slider("Eficiencia (%)", 40, 90, 65) / 100
    altitud = st.sidebar.number_input("Altitud (msnm)", value=2500)
    v_transp_target = st.sidebar.slider("Velocidad de Transporte Objetivo (m/s)", 20, 40, 25)

with st.sidebar.expander("Línea Principal y su Campana"):
    diam_principal_instalado_mm = st.number_input("Diámetro Principal INSTALADO (mm)", value=400)
    long_ducto_ppal = st.number_input("Longitud Línea Principal (m)", value=15.0)
    n_codos_ppal = st.number_input("Codos en Línea Principal", value=2)
    
    st.markdown("**📐 Boca de la Línea Principal**")
    tipo_camp_ppal = st.radio("Forma Campana Principal", ["Circular", "Rectangular"], key="tcpp")
    if tipo_camp_ppal == "Circular":
        dc_ppal = st.number_input("Ø Boca Principal (mm)", value=500)
        area_c_ppal = math.pi * (dc_ppal / 1000)**2 / 4
    else:
        w_ppal = st.number_input("Ancho Boca Principal (mm)", value=600)
        h_ppal = st.number_input("Alto Boca Principal (mm)", value=400)
        area_c_ppal = (w_ppal / 1000) * (h_ppal / 1000)

# --- CONFIGURACIÓN INDIVIDUAL DE RAMALES ---
st.sidebar.markdown("### 🛠️ Configuración de Ramales")
n_ramales = st.sidebar.number_input("Número de Ramales", min_value=1, max_value=20, value=2)

datos_ramales = []
for i in range(n_ramales):
    with st.sidebar.expander(f"Ramal #{i+1}", expanded=False):
        d_r = st.number_input(f"Ø Ducto Ramal {i+1} (mm)", value=150, key=f"dr_{i}")
        l_r = st.number_input(f"Longitud Ramal {i+1} (m)", value=3.0, key=f"lr_{i}")
        c_r = st.number_input(f"N° Codos Ramal {i+1}", value=2, key=f"cr_{i}")
        a_r = st.selectbox(f"Ángulo Codos R{i+1}", [90, 60, 45, 30], key=f"ar_{i}")
        
        tipo_c = st.selectbox(f"Tipo Campana R{i+1}", ["Circular", "Rectangular"], key=f"tc_{i}")
        if tipo_c == "Circular":
            dc = st.number_input(f"Ø Boca R{i+1} (mm)", value=250, key=f"dc_{i}")
            area_c = math.pi * (dc / 1000)**2 / 4
        else:
            w_c = st.number_input(f"Ancho Boca R{i+1} (mm)", value=300, key=f"wc_{i}")
            h_c = st.number_input(f"Alto Boca R{i+1} (mm)", value=200, key=f"hc_{i}")
            area_c = (w_c / 1000) * (h_c / 1000)
            
        datos_ramales.append({
            "id": i+1, "diam": d_r, "long": l_r, "codos": c_r, 
            "angulo": a_r, "area_campana": area_c, "tipo": tipo_c
        })

with st.sidebar.expander("Filtro de Mangas"):
    n_mangas_act = st.number_input("Número de Mangas Instaladas", value=120)
    diam_manga = st.number_input("Ø Manga (mm)", value=120)
    largo_manga = st.number_input("Largo Manga (mm)", value=2115)
    dp_filtro = st.number_input("Pérdida en Mangas (in H2O)", value=4.0)

# --- LÓGICA DE CÁLCULO ---
densidad_aire = 1.225 * math.exp(-altitud / 8500)
caudal_total_m3h = cfm_entrada * 1.699
caudal_por_ramal_m3h = caudal_total_m3h / n_ramales

# Velocidades y Pérdidas Individuales
resumen_ramales = []
suma_long_virtual = 0

for r in datos_ramales:
    d_m = r["diam"] / 1000
    v_cap = (caudal_por_ramal_m3h / 3600) / r["area_campana"]
    v_tra = (caudal_por_ramal_m3h / 3600) / (math.pi * d_m**2 / 4)
    
    le_codos = r["codos"] * (25 * d_m * (r["angulo"]/90))
    suma_long_virtual += (r["long"] + le_codos + (30 * d_m))
    
    resumen_ramales.append({
        "Ramal": f"#{r['id']}",
        "Ø Ducto (mm)": r['diam'],
        "V. Captación (m/s)": f"{v_cap:.2f}",
        "V. Transporte (m/s)": f"{v_tra:.2f}",
        "Estado": "✅ OK" if v_tra >= v_transp_target else "⚠️ BAJA"
    })

# Cálculos Línea Principal
d_m_ppal = diam_principal_instalado_mm / 1000
v_real_ppal = (caudal_total_m3h / 3600) / (math.pi * d_m_ppal**2 / 4)
v_cap_ppal = (caudal_total_m3h / 3600) / area_c_ppal

long_virtual_total = long_ducto_ppal + (n_codos_ppal * 25 * d_m_ppal) + (suma_long_virtual / n_ramales)
p_friccion_pa = (0.022 * long_virtual_total / d_m_ppal) * (0.5 * densidad_aire * v_real_ppal**2)
total_perdidas_inH2O = (p_friccion_pa / 249.08) + dp_filtro

# Mangas
area_f = n_mangas_act * (math.pi * (diam_manga/1000) * (largo_manga/1000))
mangas_nec = math.ceil(caudal_total_m3h / (1.0 * 60 * (math.pi * (diam_manga/1000) * (largo_manga/1000))))

# --- INTERFAZ DE RESULTADOS ---

# TABLA COMPARATIVA PRINCIPAL
st.subheader("📋 Resumen Comparativo: Línea Principal")
data_comp = {
    "Parámetro": ["Ø Ducto Principal", "V. Captación Campana Principal", "V. Transporte Ducto Principal", "Número de Mangas", "Caudal Total"],
    "Unidad": ["mm", "m/s", "m/s", "u", "m³/h"],
    "Valor Real": [f"{diam_principal_instalado_mm}", f"{v_cap_ppal:.2f}", f"{v_real_ppal:.2f}", f"{n_mangas_act}", f"{caudal_total_m3h:.0f}"],
    "Valor Ideal": [f"{math.sqrt(4*((caudal_total_m3h/3600)/v_transp_target)/math.pi)*1000:.0f}", "7.0 - 12.0", f"{v_transp_target:.2f}", f"{mangas_nec}", f"{v_transp_target * (math.pi*(d_m_ppal**2)/4)*3600:.0f}"]
}
st.table(pd.DataFrame(data_comp))

# DETALLE DE RAMALES (VALORES INDIVIDUALES)
st.subheader("🌿 Detalle de Velocidades por Ramal")
st.dataframe(pd.DataFrame(resumen_ramales), use_container_width=True)

# GRÁFICA Y DIAGNÓSTICO
st.subheader("📈 Análisis de Presión")
c_g, c_d = st.columns([2, 1])

with c_g:
    q_range = np.linspace(100, cfm_entrada * 1.3, 50)
    curva = (total_perdidas_inH2O / (cfm_entrada**2)) * (q_range**2)
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(q_range, curva, color="#00FFAA", label="Curva Sistema")
    ax.axhline(y=sp_ventilador, color='red', linestyle='--', label="SP Ventilador")
    ax.scatter([cfm_entrada], [total_perdidas_inH2O], color='yellow', s=100)
    ax.set_ylabel("in H2O"); ax.legend()
    st.pyplot(fig)

with c_d:
    hp_op = (cfm_entrada * total_perdidas_inH2O) / (6356 * eficiencia_fan)
    st.metric("Resistencia Total", f"{total_perdidas_inH2O:.2f} inH2O")
    st.metric("Potencia Necesaria", f"{hp_op:.1f} HP")
    balance = sp_ventilador - total_perdidas_inH2O
    if balance > 0:
        st.success(f"Reserva: {balance:.2f} inH2O")
    else:
        st.error(f"Déficit: {abs(balance):.2f} inH2O")
