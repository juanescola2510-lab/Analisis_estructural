import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- CONFIGURACIÓN Y CÁLCULOS (Mantenemos tu lógica anterior) ---
st.set_page_config(page_title="Elevador de Cangilones Pro", layout="wide")
st.title("⚙️ Análisis Avanzado de Componentes: Elevador de Cangilones")

# Barra lateral para inputs
tph = st.sidebar.slider("Capacidad (Ton/h)", 50, 500, 150)
v_ms = st.sidebar.slider("Velocidad (m/s)", 0.5, 2.0, 1.2)
altura = st.sidebar.slider("Altura (m)", 10.0, 50.0, 33.5)
p_cadena = st.sidebar.number_input("Peso Cadena (lb)", value=2400)
p_cangilones = st.sidebar.number_input("Peso Cangilones (lb)", value=11820)
d_pin = st.sidebar.slider("Diámetro Pin (mm)", 20.0, 50.0, 34.74)

# Cálculos de carga
flujo_kgs = (tph * 1000) / 3600
p_material_lb = ((flujo_kgs / v_ms) * altura) * 2.20462
t_max = p_cadena + p_cangilones + p_material_lb

# --- GENERACIÓN DE GRÁFICOS DETALLADOS ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# 1. DCL SPROCKET REALISTA (Con dientes y fuerzas desglosadas)
ax1.set_title("DCL: Ensamble Sprocket Superior", fontsize=14, fontweight='bold')
# Dibujo del cuerpo del sprocket
cuerpo = plt.Circle((0.5, 0.6), 0.25, color='#454545', zorder=2)
centro = plt.Circle((0.5, 0.6), 0.05, color='black', zorder=3)
ax1.add_patch(cuerpo)
ax1.add_patch(centro)

# Dibujo de dientes (representación visual)
for i in range(12):
    angle = np.deg2rad(i * 30)
    x = 0.5 + 0.28 * np.cos(angle)
    y = 0.6 + 0.28 * np.sin(angle)
    ax1.add_patch(plt.Circle((x, y), 0.04, color='#454545'))

# Vectores de carga desglosados
ax1.annotate('', xy=(0.78, 0.1), xytext=(0.78, 0.6), arrowprops=dict(facecolor='red', width=4, headwidth=10))
ax1.text(0.8, 0.45, f"T_max: {t_max:,.0f} lb", color='red', fontweight='bold', fontsize=12)

# Desglose de fuerzas al lado de la flecha
ax1.text(0.8, 0.35, f"↳ Mat: {p_material_lb:,.0f} lb", color='gray')
ax1.text(0.8, 0.30, f"↳ Cang: {p_cangilones:,.0f} lb", color='gray')
ax1.text(0.8, 0.25, f"↳ Cadena: {p_cadena:,.0f} lb", color='gray')

ax1.set_xlim(0, 1.2); ax1.set_ylim(0, 1); ax1.axis('off')

# 2. DCL PIN REALISTA (Con Placas Laterales y Doble Corte)
ax2.set_title("DCL: Detalle de Ensamble y Corte en Pin", fontsize=14, fontweight='bold')

# Dibujo del Pin (Cilíndrico)
ax2.add_patch(plt.Rectangle((0.1, 0.45), 0.8, 0.1, color='#BDBDBD', ec='black', zorder=4)) 
ax2.text(0.5, 0.57, f"PIN Ø{d_pin}mm (35CrMo)", ha='center', fontweight='bold')

# Placas Externas (Soporte)
ax2.add_patch(plt.Rectangle((0.1, 0.3), 0.15, 0.4, color='#757575', alpha=0.7, label='Placas Ext'))
ax2.add_patch(plt.Rectangle((0.75, 0.3), 0.15, 0.4, color='#757575', alpha=0.7))
# Reacciones en placas externas
ax2.annotate('', xy=(0.17, 0.7), xytext=(0.17, 0.9), arrowprops=dict(facecolor='blue', width=2))
ax2.annotate('', xy=(0.82, 0.7), xytext=(0.82, 0.9), arrowprops=dict(facecolor='blue', width=2))
ax2.text(0.5, 0.92, "REACCIÓN SOPORTE (R/2)", color='blue', ha='center')

# Placa Interna / Buje (Carga central)
ax2.add_patch(plt.Rectangle((0.35, 0.35), 0.3, 0.3, color='#9E9E9E', hatch='//', alpha=0.8))
ax2.text(0.5, 0.3, "ESLABÓN INTERNO / CARGA", ha='center', fontsize=9)
# Fuerza central T_max
ax2.annotate('', xy=(0.5, 0.45), xytext=(0.5, 0.1), arrowprops=dict(facecolor='red', width=5))

# Planos de Falla (Doble Cortadura)
ax2.axvline(0.3, color='red', ls='--', lw=2)
ax2.axvline(0.7, color='red', ls='--', lw=2)
ax2.text(0.3, 0.75, "PLANO A", color='red', ha='center', fontweight='bold', rotation=90)
ax2.text(0.7, 0.75, "PLANO B", color='red', ha='center', fontweight='bold', rotation=90)

ax2.set_xlim(0, 1); ax2.set_ylim(0, 1); ax2.axis('off')

st.pyplot(fig)

# --- PANEL DE ALERTAS ---
st.markdown("---")
if t_max > 20000:
    st.warning(f"🚨 **ALERTA DE TENSIÓN:** La carga actual de **{t_max:,.0f} lb** es crítica para un sistema de ramal único. Revise la fatiga de los pines.")
