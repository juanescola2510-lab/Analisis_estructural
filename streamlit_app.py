import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

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
    v_transp_target = st.sidebar.slider("Velocidad de Transporte Objetivo (m/s)", 20, 40, 25, help="Clinker requiere velocidades altas (>25 m/s)")

with st.sidebar.expander("Red de Ductos y Ramales"):
    # Rugosidad ajustada para Acero Hardox / Abrasivos
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

# 1. Comparativa Ducto Principal
area_ideal_m2 = (caudal_total_m3h / 3600) / v_transp_target
diam_ideal_mm = math.sqrt(4 * area_ideal_m2 / math.pi) * 1000
area_instalada_m2 = math.pi * (diam_principal_instalado_mm / 1000)**2 / 4
v_real_principal_ms = (caudal_total_m3h / 3600) / area_instalada_m2

# 2. Velocidades en Ramales
area_ducto_ramal_m2 = math.pi * (diam_ramal_mm / 1000)**2 / 4
v_transporte_ramal_ms = (caudal_por_ramal_m3h / 3600) / area_ducto_ramal_m2
v_captacion_ms = (caudal_por_ramal_m3h / 3600) / area_campana_m2

# 3. Pérdidas de Presión
d_m_inst = diam_principal_instalado_mm / 1000
ld_dict = {"Codo": 25, "Union Y": 20, "Campana": 30} # Valores más conservadores para abrasivos
total_codos = n_codos_ppal + (n_ramales * codos_por_ramal)
long_virtual = (long_ducto_ppal + (n_ramales * long_ramal_m)) + \
               (total_codos * ld_dict["Codo"] * d_m_inst) + \
               (n_ramales * ld_dict["Union Y"] * d_m_inst)

f = 0.022 # Factor de fricción ligeramente mayor por rugosidad de Hardox
presion_din_pa = 0.5 * densidad_aire * v_real_principal_ms**2
p_friccion_pa = (f * long_virtual / d_m_inst) * presion_din_pa
total_perdidas_inH2O = (p_friccion_pa / 249.08) + dp_filtro

# 4. Mangas
area_total_f = n_mangas_act * (math.pi * (diam_manga/1000) * (largo_manga/1000))
relacion_at = caudal_total_m3h / (area_total_f * 60)
mangas_nec = math.ceil(caudal_total_m3h / (1.0 * 60 * (math.pi * (diam_manga/1000) * (largo_manga/1000)))) # Carga clinker: 1.0 m/min

# --- INTERFAZ DE RESULTADOS ---

st.subheader("📏 Diagnóstico de Ductería Principal")
col_d1, col_d2, col_d3 = st.columns(3)
col_d1.metric("Ø Ideal (Clinker)", f"{diam_ideal_mm:.0f} mm")
col_d2.metric("Ø Instalado Hardox", f"{diam_principal_instalado_mm} mm")
col_d3.metric("Velocidad Principal", f"{v_real_principal_ms:.2f} m/s")

# Alertas Clinker
if v_real_principal_ms < 25:
    st.error("🚨 **CRÍTICO:** El clinker es pesado. Velocidad < 25 m/s causará obstrucción inmediata.")

st.subheader("🎯 Velocidades y Filtrado")
v1, v2, v3, v4 = st.columns(4)
v1.metric("V. Captación", f"{v_captacion_ms:.2f} m/s")
v2.metric("V. Ramal", f"{v_transporte_ramal_ms:.2f} m/s")
v3.metric("Aire/Tela", f"{relacion_at:.2f} m/min")
v4.metric("Mangas Necesarias", f"{mangas_nec}")

# --- GRÁFICA DEL VENTILADOR ---
st.subheader("📈 Curva de Operación del Sistema")
q_range = np.linspace(100, cfm_entrada * 1.4, 50)
# Curva de resistencia: P = k * Q^2
k = total_perdidas_inH2O / (cfm_entrada**2)
curva_resistencia = k * (q_range**2)

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(q_range, curva_resistencia, label="Resistencia del Sistema (Ductos+Filtro)", color="#00FFAA", lw=2)
ax.axhline(y=sp_ventilador, color='red', linestyle='--', label=f"Capacidad Max Ventilador ({sp_ventilador} inH2O)")
ax.scatter([cfm_entrada], [total_perdidas_inH2O], color='yellow', s=100, zorder=5, label="Punto Actual")

ax.set_xlabel("Caudal (CFM)")
ax.set_ylabel("Presión Estática (in H2O)")
ax.set_ylim(0, max(sp_ventilador, total_perdidas_inH2O) * 1.2)
ax.grid(alpha=0.3)
ax.legend()
st.pyplot(fig)

# Diagnóstico de Potencia
st.subheader("📊 Potencia y Resistencia")
res1, res2, res3 = st.columns(3)
res1.metric("Resistencia Total", f"{total_perdidas_inH2O:.2f} inH2O")
hp_op = (cfm_entrada * total_perdidas_inH2O) / (6356 * eficiencia_fan)
res2.metric("Potencia Requerida", f"{hp_op:.1f} HP")

balance = sp_ventilador - total_perdidas_inH2O
if balance >= 0:
    st.success(f"✅ **SISTEMA ESTABLE:** Reserva de {balance:.2f} in H2O.")
else:
    st.error(f"❌ **SOBRECARGA:** La resistencia supera al ventilador por {abs(balance):.2f} in H2O.")
