import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Calculador de Elevador de Cangilones", layout="wide")

st.title("🏗️ Simulación de Esfuerzos en Cadena de Elevador")
st.sidebar.header("Parámetros de Entrada")

# --- ENTRADAS EN LA BARRA LATERAL ---
tph = st.sidebar.slider("Capacidad (Ton/h)", 50, 500, 150)
v_ms = st.sidebar.slider("Velocidad de Cadena (m/s)", 0.5, 2.0, 1.2)
altura = st.sidebar.slider("Altura entre Centros (m)", 10.0, 50.0, 33.5)
p_cadena = st.sidebar.number_input("Peso Total Cadena (lb)", value=2400)
p_cangilones = st.sidebar.number_input("Peso Total Cangilones (lb)", value=11820)
d_pin = st.sidebar.slider("Diámetro del Pin (mm)", 20.0, 50.0, 34.74)
res_mpa = st.sidebar.number_input("Resistencia Tracción Acero (MPa)", value=980)

# --- CÁLCULOS LÓGICOS ---
# 1. Peso del material
flujo_kgs = (tph * 1000) / 3600
carga_kgm = flujo_kgs / v_ms
p_material_lb = (carga_kgm * altura) * 2.20462

# 2. Tensiones
tension_total_lb = p_cadena + p_cangilones + p_material_lb
fuerza_n = tension_total_lb * 4.44822

# 3. Esfuerzos en el Pin (Doble Corte)
area_doble_mm2 = 2 * (np.pi * (d_pin / 2)**2)
esfuerzo_mpa = fuerza_n / area_doble_mm2
res_corte = res_mpa * 0.577
fs = res_corte / esfuerzo_mpa

# --- INTERFAZ DE RESULTADOS ---
col1, col2, col3 = st.columns(3)
col1.metric("Tensión Total", f"{tension_total_lb:,.0f} lb")
col2.metric("Esfuerzo en Pin", f"{esfuerzo_mpa:.2f} MPa")
col3.metric("Factor Seguridad", f"{fs:.2f}", delta=None, delta_color="normal")

if fs < 8:
    st.error(f"⚠️ PELIGRO: Factor de Seguridad ({fs:.2f}) bajo para Clinker/Puzolana. Se recomienda FS > 10.")
else:
    st.success(f"✅ DISEÑO SEGURO: El Factor de Seguridad ({fs:.2f}) es adecuado.")

# --- GRÁFICOS ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Gráfico 1: DCL Sprocket
ax1.set_title("DCL: Sprocket Superior")
ax1.add_patch(plt.Circle((0.5, 0.7), 0.15, color='gray', alpha=0.3))
ax1.annotate('', xy=(0.65, 0.1), xytext=(0.65, 0.7), arrowprops=dict(facecolor='red', shrink=0.05))
ax1.text(0.68, 0.3, f"T_max: {tension_total_lb:,.0f} lb", color='red', fontweight='bold')
ax1.text(0.1, 0.8, f"Material: {p_material_lb:.0f} lb", fontsize=8)
ax1.set_xlim(0, 1); ax1.set_ylim(0, 1); ax1.axis('off')

# Gráfico 2: Corte en el Pin
ax2.set_title("DCL: Corte Doble en el Pin")
ax2.add_patch(plt.Rectangle((0.2, 0.4), 0.6, 0.2, color='silver', ec='black'))
ax2.axvline(0.35, color='red', ls='--')
ax2.axvline(0.65, color='red', ls='--')
ax2.annotate('', xy=(0.5, 0.4), xytext=(0.5, 0.1), arrowprops=dict(facecolor='red', shrink=0.05))
ax2.text(0.4, 0.7, "Planos de Corte", color='red', fontsize=9)
ax2.set_xlim(0, 1); ax2.set_ylim(0, 1); ax2.axis('off')

st.pyplot(fig)

# Tabla de detalles
st.write("### Detalle de Cargas")
st.table({
    "Concepto": ["Material Suspendido", "Cangilones", "Cadena", "Total"],
    "Peso (lb)": [f"{p_material_lb:.2f}", f"{p_cangilones:.2f}", f"{p_cadena:.2f}", f"{tension_total_lb:.2f}"]
})
