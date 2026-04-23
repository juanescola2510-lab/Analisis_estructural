import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Simulador Succión Clinker Pro", layout="wide")

st.title("🌪️ Ingeniería de Succión Detallada: Ramales Independientes")
st.markdown("---")

# --- BARRA LATERAL ---
st.sidebar.header("📊 Configuración del Sistema")

with st.sidebar.expander("Ventilador y Entorno", expanded=True):
    cfm_entrada = st.sidebar.number_input("Caudal Nominal Ventilador (CFM)", value=7600)
    sp_ventilador = st.sidebar.number_input("Presión Estática de Placa (in H2O)", value=10.0)
    eficiencia_fan = st.sidebar.slider("Eficiencia (%)", 40, 90, 65) / 100
    altitud = st.sidebar.number_input("Altitud (msnm)", value=2500)
    v_transp_target = st.sidebar.slider("Velocidad de Transporte Objetivo (m/s)", 20, 40, 25)

with st.sidebar.expander("Línea Principal (Hardox)"):
    diam_principal_instalado_mm = st.number_input("Diámetro Principal INSTALADO (mm)", value=400)
    long_ducto_ppal = st.number_input("Longitud Línea Principal (m)", value=15.0)
    n_codos_ppal = st.number_input("Codos en Línea Principal", value=2)
    materiales = {"Acero Hardox": 0.0002, "Acero Galvanizado": 0.00015}
    tipo_mat = st.selectbox("Material", list(materiales.keys()))

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

# --- LÓGICA DE CÁLCULO ACUMULATIVA ---
densidad_aire = 1.225 * math.exp(-altitud / 8500)
caudal_total_m3h = cfm_entrada * 1.699
caudal_por_ramal_m3h = caudal_total_m3h / n_ramales

# Pérdidas en ramales (promediadas para el sistema)
perdida_accesorios_total_m = 0
v_captacion_lista = []
v_transp_ramal_lista = []

for r in datos_ramales:
    d_m = r["diam"] / 1000
    # Cálculo de longitud equivalente por ángulo de codo
    factor_angulo = r["angulo"] / 90
    le_codos = r["codos"] * (25 * d_m * factor_angulo) 
    le_campana = 30 * d_m # Entrada campana
    perdida_accesorios_total_m += (r["long"] + le_codos + le_campana)
    
    # Velocidades individuales
    v_cap = (caudal_por_ramal_m3h / 3600) / r["area_campana"]
    v_tra = (caudal_por_ramal_m3h / 3600) / (math.pi * d_m**2 / 4)
    v_captacion_lista.append(v_cap)
    v_transp_ramal_lista.append(v_tra)

# Pérdida en línea principal
d_m_ppal = diam_principal_instalado_mm / 1000
le_codos_ppal = n_codos_ppal * 25 * d_m_ppal
long_virtual_total = long_ducto_ppal + le_codos_ppal + (perdida_accesorios_total_m / n_ramales)

v_real_ppal = (caudal_total_m3h / 3600) / (math.pi * d_m_ppal**2 / 4)
f = 0.022
p_friccion_pa = (f * long_virtual_total / d_m_ppal) * (0.5 * densidad_aire * v_real_ppal**2)
total_perdidas_inH2O = (p_friccion_pa / 249.08) + dp_filtro

# Mangas
area_f = n_mangas_act * (math.pi * (diam_manga/1000) * (largo_manga/1000))
relacion_at = caudal_total_m3h / (area_f * 60)
mangas_nec = math.ceil(caudal_total_m3h / (1.0 * 60 * (math.pi * (diam_manga/1000) * (largo_manga/1000))))

# --- INTERFAZ DE RESULTADOS ---

# TABLA COMPARATIVA
st.subheader("📋 Resumen Comparativo de Sistema")
data_comp = {
    "Parámetro": ["Ø Ducto Principal", "Velocidad Promedio Captación", "Velocidad en Ducto Principal", "Número de Mangas", "Caudal Total"],
    "Unidad": ["mm", "m/s", "m/s", "u", "m³/h"],
    "Valor Real": [f"{diam_principal_instalado_mm}", f"{np.mean(v_captacion_lista):.2f}", f"{v_real_ppal:.2f}", f"{n_mangas_act}", f"{caudal_total_m3h:.0f}"],
    "Valor Ideal": [f"{math.sqrt(4*((caudal_total_m3h/3600)/v_transp_target)/math.pi)*1000:.0f}", "5.0 - 10.0", f"{v_transp_target:.2f}", f"{mangas_nec}", f"{v_transp_target * (math.pi*(d_m_ppal**2)/4)*3600:.0f}"]
}
st.table(pd.DataFrame(data_comp))

# DESGLOSE POR RAMAL
st.subheader("🌿 Detalle Individual de Ramales")
df_ramales = pd.DataFrame({
    "Ramal": [f"#{r['id']}" for r in datos_ramales],
    "Ø Ducto (mm)": [r['diam'] for r in datos_ramales],
    "Codos (Ang)": [f"{r['codos']} ({r['angulo']}°)" for r in datos_ramales],
    "V. Captación (m/s)": [f"{v:.2f}" for v in v_captacion_lista],
    "V. Transporte (m/s)": [f"{v:.2f}" for v in v_transp_ramal_lista]
})
st.dataframe(df_ramales, use_container_width=True)

# GRÁFICA
st.subheader("📈 Curva de Operación")
q_range = np.linspace(100, cfm_entrada * 1.3, 50)
curva = (total_perdidas_inH2O / (cfm_entrada**2)) * (q_range**2)
fig, ax = plt.subplots(figsize=(10, 3))
ax.plot(q_range, curva, color="#00FFAA", label="Resistencia")
ax.axhline(y=sp_ventilador, color='red', linestyle='--', label="Límite Ventilador")
ax.scatter([cfm_entrada], [total_perdidas_inH2O], color='yellow', s=80)
st.pyplot(fig)

# DIAGNÓSTICO
hp_op = (cfm_entrada * total_perdidas_inH2O) / (6356 * eficiencia_fan)
st.info(f"⚡ **Potencia Requerida:** {hp_op:.1f} HP | **Balance de Presión:** {sp_ventilador - total_perdidas_inH2O:.2f} inH2O")
