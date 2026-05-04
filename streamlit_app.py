import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Análisis de Atascamiento en Bota", layout="wide")
st.title("🚜 Análisis de Sobrecarga por Acumulación en la Bota")

# --- SIDEBAR ---
st.sidebar.header("⚙️ Parámetros de Operación")
tph = st.sidebar.number_input("Capacidad Real (Ton/h)", value=150)
v_ms = st.sidebar.slider("Velocidad (m/s)", 0.5, 2.0, 1.2)
altura = st.sidebar.number_input("Altura (m)", value=33.5)
d_pin = st.sidebar.slider("Diámetro del Pin (mm)", 20.0, 55.0, 34.74)

st.sidebar.header("⚠️ Condición de la Bota")
nivel_acumulacion = st.sidebar.select_slider(
    "Nivel de Acumulación/Atascamiento",
    options=["Limpio", "Moderado", "Crítico", "Obstrucción Total"],
    value="Limpio"
)

# Definición de la fuerza de excavación extra (Fexc)
# En ingeniería, esto se estima como un % extra de la carga de material
mapeo_fexc = {"Limpio": 0.10, "Moderado": 0.50, "Crítico": 1.50, "Obstrucción Total": 3.00}
factor_fexc = mapeo_fexc[nivel_acumulacion]

# --- CÁLCULOS ---
flujo_kgs = (tph * 1000) / 3600
p_material_lb = ((flujo_kgs / v_ms) * altura) * 2.20462
# Fuerza de excavación extra producida por el atascamiento
f_excavacion_lb = p_material_lb * factor_fexc 

t_estatica_lb = 2400 + 11820 + p_material_lb # Cadena + Cangilones + Material
t_total_lb = t_estatica_lb + f_excavacion_lb
f_n = t_total_lb * 4.44822 # Convertir a Newtons

# Esfuerzo Cortante Transversal
area_total = 2 * (np.pi * (d_pin / 2)**2)
tau_real = f_n / area_total

# --- INTERFAZ ---
c1, c2, c3 = st.columns(3)
c1.metric("Tensión por Atascamiento", f"{f_excavacion_lb:,.0f} lb", delta=f"+{factor_fexc*100:.0f}%")
c2.metric("Tensión Total Real", f"{t_total_lb:,.0f} lb")
c3.metric("Esfuerzo Cortante (τ)", f"{tau_real:.2f} MPa")

# --- GRÁFICO DCL DE LA BOTA (NUEVO) ---
st.write("### DCL: Resistencia en la Bota por Acumulación")
fig_bota, ax_b = plt.subplots(figsize=(10, 4))
# Dibujo de la bota y material
ax_b.add_patch(plt.Rectangle((0.1, 0.1), 0.8, 0.2, color='#D2B48C', alpha=0.6)) # Material acumulado
# Cangilón entrando
ax_b.add_patch(plt.Rectangle((0.45, 0.2), 0.1, 0.15, color='gray', ec='black'))
# Vectores
ax_b.annotate('', xy=(0.55, 0.25), xytext=(0.8, 0.25), arrowprops=dict(facecolor='red', width=3))
ax_b.text(0.6, 0.3, f"F_exc: {f_excavacion_lb:,.0f} lb", color='red', fontweight='bold')
ax_b.axis('off')
st.pyplot(fig_bota)

# --- ANÁLISIS DE ESFUERZO CORTANTE TRANSVERSAL ---
st.write("### Análisis de Distribución de Esfuerzo Cortante en el Pin")
fig_tau, ax_t = plt.subplots(figsize=(6, 6))
pin = plt.Circle((0.5, 0.5), 0.4, color='#BDBDBD', ec='black', lw=2)
ax_t.add_patch(pin)
# Gradiente de esfuerzo cortante (Parabólico)
y = np.linspace(0.15, 0.85, 20)
for val_y in y:
    # tau = (V * Q) / (I * t) -> simplificado parabólico
    l = 0.35 * (1 - ((val_y-0.5)/0.35)**2)
    ax_t.annotate('', xy=(0.5 + l, val_y), xytext=(0.5, val_y), arrowprops=dict(arrowstyle='->', color='red'))
ax_t.text(0.5, 0.5, f"τ_max = {tau_real:.2f} MPa", ha='center', color='red', fontweight='bold', bbox=dict(facecolor='white', alpha=0.7))
ax_t.axis('off')
st.pyplot(fig_tau)

st.error(f"**Nota de Falla:** Con un nivel de **{nivel_acumulacion}**, el esfuerzo cortante en el pin ha subido a **{tau_real:.2f} MPa**. Si este valor se acerca al límite de fatiga (~180-200 MPa), el pin se romperá instantáneamente ante cualquier obstrucción sólida de clinker.")
