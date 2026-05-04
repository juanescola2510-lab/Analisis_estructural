import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Simulador Profesional de Elevadores", layout="wide")
st.title("🔩 Análisis de Ingeniería: Componentes y Fatiga")

# --- SIDEBAR INPUTS ---
st.sidebar.header("📊 Parámetros de Operación")
tph = st.sidebar.number_input("Capacidad (Ton/h)", value=150)
v_ms = st.sidebar.slider("Velocidad (m/s)", 0.5, 2.0, 1.2)
altura = st.sidebar.number_input("Altura (m)", value=33.5)
d_pin = st.sidebar.slider("Diámetro del Pin (mm)", 20.0, 55.0, 34.74)

st.sidebar.header("⚠️ Estado de la Bota")
nivel_acum = st.sidebar.select_slider("Atascamiento", 
    options=["Limpio", "Moderado", "Crítico", "Total"], value="Limpio")

# --- LÓGICA DE CÁLCULO ---
flujo_kgs = (tph * 1000) / 3600
p_mat_lb = ((flujo_kgs / v_ms) * altura) * 2.20462
p_cad_lb, p_cang_lb = 2400, 11820
f_exc_map = {"Limpio": 0.1, "Moderado": 0.5, "Crítico": 1.5, "Total": 3.0}
f_exc_lb = p_mat_lb * f_exc_map[nivel_acum]

t_total_lb = p_cad_lb + p_cang_lb + p_mat_lb + f_exc_lb
f_n = t_total_lb * 4.44822
reaccion_n = f_n / 2 # Reacción en cada placa lateral

# --- GRÁFICOS ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# 1. SPROCKET CON DIENTES INDUSTRIALES
ax1.set_title("DCL: Sprocket y Tensión de Cadena", fontsize=14, fontweight='bold')
# Cuerpo del sprocket
cuerpo = plt.Circle((0.5, 0.6), 0.22, color='#333333', zorder=2)
ax1.add_patch(cuerpo)
# Dibujo de dientes trapezoidales
for i in range(12):
    ang = np.deg2rad(i * 30)
    # Puntos para formar un diente trapezoidal
    p1 = [0.5 + 0.22*np.cos(ang-0.1), 0.6 + 0.22*np.sin(ang-0.1)]
    p2 = [0.5 + 0.30*np.cos(ang-0.05), 0.6 + 0.30*np.sin(ang-0.05)]
    p3 = [0.5 + 0.30*np.cos(ang+0.05), 0.6 + 0.30*np.sin(ang+0.05)]
    p4 = [0.5 + 0.22*np.cos(ang+0.1), 0.6 + 0.22*np.sin(ang+0.1)]
    ax1.add_patch(patches.Polygon([p1, p2, p3, p4], color='#333333', zorder=1))

# Vector T_total y desglose
ax1.annotate('', xy=(0.8, 0.1), xytext=(0.8, 0.6), arrowprops=dict(facecolor='red', width=4))
ax1.text(0.82, 0.4, f"T_Total: {t_total_lb:,.0f} lb", color='red', fontweight='bold', fontsize=12)
ax1.text(0.82, 0.3, f"• Mat: {p_mat_lb:,.0f} lb\n• Bota: {f_exc_lb:,.0f} lb\n• Cang: {p_cang_lb:,.0f} lb\n• Cad: {p_cad_lb:,.0f} lb", color='#555', fontsize=10)
ax1.axis('off')

# 2. DCL DEL PIN CON REACCIONES Y VALORES
ax2.set_title("DCL: Esfuerzos y Reacciones en el Pin", fontsize=14, fontweight='bold')
# Pin y Placas
ax2.add_patch(plt.Rectangle((0.1, 0.45), 0.8, 0.1, color='#BDBDBD', ec='black', zorder=4))
ax2.add_patch(plt.Rectangle((0.1, 0.3), 0.12, 0.4, color='#757575', alpha=0.9)) # Placa Izq
ax2.add_patch(plt.Rectangle((0.78, 0.3), 0.12, 0.4, color='#757575', alpha=0.9)) # Placa Der
ax2.add_patch(plt.Rectangle((0.32, 0.35), 0.36, 0.3, color='#9E9E9E', hatch='//')) # Buje/Carga

# Vectores de Reacción (Hacia Arriba)
ax2.annotate('', xy=(0.16, 0.9), xytext=(0.16, 0.7), arrowprops=dict(facecolor='blue', width=3))
ax2.annotate('', xy=(0.84, 0.9), xytext=(0.84, 0.7), arrowprops=dict(facecolor='blue', width=3))
ax2.text(0.16, 0.95, f"R/2: {reaccion_n/1000:.1f} kN", color='blue', ha='center', fontweight='bold')
ax2.text(0.84, 0.95, f"R/2: {reaccion_n/1000:.1f} kN", color='blue', ha='center', fontweight='bold')

# Vector de Carga (Hacia Abajo)
ax2.annotate('', xy=(0.5, 0.1), xytext=(0.5, 0.45), arrowprops=dict(facecolor='red', width=5))
ax2.text(0.52, 0.15, f"Carga: {f_n/1000:.1f} kN", color='red', fontweight='bold')

ax2.axis('off')
st.pyplot(fig)

# --- RESUMEN TÉCNICO ---
st.markdown("---")
st.write("### Análisis Transversal del Pin")
col_t1, col_t2 = st.columns(2)
area_mm2 = 2 * (np.pi * (d_pin/2)**2)
tau_mpa = f_n / area_mm2

with col_t1:
    st.info(f"**Área de Doble Corte:** {area_mm2:.2f} mm²")
    st.info(f"**Esfuerzo Cortante Real:** {tau_mpa:.2f} MPa")

with col_t2:
    st.write("**Resumen de Fuerzas en el Pin:**")
    st.write(f"- Fuerza aplicada (Carga): {f_n:,.0f} N")
    st.write(f"- Reacción en soportes laterales: {reaccion_n:,.0f} N cada uno")
