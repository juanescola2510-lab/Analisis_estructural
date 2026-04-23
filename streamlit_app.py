import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

# Configuración de página
st.set_page_config(page_title="Simulador de Succión Pro", layout="wide")

st.title("🌪️ Ingeniería de Succión y Capacidad de Sistema")
st.markdown("---")

# --- BARRA LATERAL ---
st.sidebar.header("📊 Configuración del Sistema")

with st.sidebar.expander("Ventilador y Entorno", expanded=True):
    cfm_entrada = st.number_input("Caudal Nominal (CFM)", value=7600)
    sp_ventilador = st.number_input("Presión Estática de Placa (in H2O)", value=10.0)
    altitud = st.number_input("Altitud del Sitio (msnm)", value=0, help="Afecta la densidad del aire")
    v_diseno = st.slider("Velocidad de Transporte (m/s)", 10, 35, 20)

with st.sidebar.expander("Filtro de Mangas"):
    n_mangas_act = st.number_input("Número de Mangas", value=120)
    diam_manga = st.number_input("Diámetro Manga (mm)", value=120)
    largo_manga = st.number_input("Largo Manga (mm)", value=2115)
    dp_filtro = st.number_input("DP del Filtro (in H2O)", value=4.0)

with st.sidebar.expander("Red de Ductos"):
    materiales = {
        "Acero Galvanizado": 0.00015,
        "PVC / Plástico": 0.0000015,
        "Acero Inoxidable": 0.000045,
        "Ducto Flexible": 0.003
    }
    tipo_mat = st.selectbox("Material", list(materiales.keys()))
    long_ducto = st.number_input("Longitud Recta Total (m)", value=20.0)
    n_ramales = st.number_input("Nuevos Ramales / Uniones Y", value=2)
    n_codos = st.number_input("Cantidad de Codos", value=3)
    tipo_codo = st.radio("Tipo de Codo", ["Radio Corto (R=1D)", "Radio Largo (R=2.5D)"])

# --- LÓGICA DE CÁLCULO ---

# 1. Propiedades del Aire
densidad_aire = 1.225 * math.exp(-altitud / 8500)
viscosidad = 1.5e-5

# 2. Caudales y Dimensionamiento
m3h_base = cfm_entrada * 1.699
area_ramal_u = math.pi * (0.200)**2 / 4
caudal_nuevos = n_ramales * (area_ramal_u * v_diseno * 3600)
caudal_total = max(m3h_base, caudal_nuevos)
cfm_total = caudal_total / 1.699

area_req = (caudal_total / 3600) / v_diseno
d_m = math.sqrt(4 * area_req / math.pi)
diam_principal_mm = d_m * 1000

# 3. Longitudes Equivalentes (Accesorios)
ld_dict = {"Radio Corto (R=1D)": 30, "Radio Largo (R=2.5D)": 15, "Union Y": 20, "Campana": 25}
le_accesorios = (n_codos * ld_dict[tipo_codo] * d_m) + (n_ramales * ld_dict["Union Y"] * d_m) + (ld_dict["Campana"] * d_m)
long_virtual = long_ducto + le_accesorios

# 4. Fricción Dinámica (Swamee-Jain)
reynolds = (v_diseno * d_m) / viscosidad
rugosidad = materiales[tipo_mat]
f = 0.25 / (math.log10((rugosidad / (3.7 * d_m)) + (5.74 / reynolds**0.9)))**2
presion_din_pa = 0.5 * densidad_aire * v_diseno**2

p_friccion_pa = (f * long_virtual / d_m) * presion_din_pa
total_perdidas_inH2O = (p_friccion_pa / 249.08) + dp_filtro

# 5. Aire/Tela
area_manga = math.pi * (diam_manga/1000) * (largo_manga/1000)
area_total_f = n_mangas_act * area_manga
relacion_at = caudal_total / (area_total_f * 60)

# --- INTERFAZ DE RESULTADOS ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Ducto Principal", f"{diam_principal_mm:.0f} mm")
c2.metric("Relación Aire/Tela", f"{relacion_at:.2f} m/min")
c3.metric("Pérdida de Carga", f"{total_perdidas_inH2O:.2f} inH2O")
c4.metric("Longitud Virtual", f"{long_virtual:.1f} m")

# Diagnóstico
balance = sp_ventilador - total_perdidas_inH2O
if balance > 1.0:
    st.success(f"✅ **SISTEMA ESTABLE:** Reserva de {balance:.2f} in H2O.")
elif balance >= 0:
    st.warning(f"⚠️ **SISTEMA CRÍTICO:** Solo sobran {balance:.2f} in H2O. Flujo inestable.")
else:
    st.error(f"🚨 **SISTEMA COLAPSADO:** Faltan {abs(balance):.2f} in H2O de presión.")

# --- GRÁFICA DE OPERACIÓN ---
st.subheader("📈 Punto de Operación")
caudales_plot = np.linspace(0, cfm_total * 1.5, 50)
curva_sistema = [(total_perdidas_inH2O / (cfm_total**2)) * (q**2) for q in caudales_plot]

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(caudales_plot, curva_sistema, label="Resistencia del Sistema", color="#00FFAA")
ax.axhline(y=sp_ventilador, color='red', linestyle='--', label="Límite Ventilador")
ax.scatter([cfm_total], [total_perdidas_inH2O], color='white', edgecolor='black', s=100, zorder=5)
ax.set_xlabel("Caudal (CFM)")
ax.set_ylabel("Presión (in H2O)")
ax.grid(alpha=0.2)
ax.legend()
st.pyplot(fig)

if tipo_mat == "Ducto Flexible":
    st.info("💡 **Nota:** El ducto flexible multiplica la fricción. Considera cambiar a Acero si la pérdida es muy alta.")
