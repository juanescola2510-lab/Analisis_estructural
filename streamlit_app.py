import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Análisis de Ingeniería: Elevador de Cangilones", layout="wide")

st.title("🏗️ Diagnóstico de Falla y Fatiga (Criterio de Goodman)")
st.sidebar.header("📊 Parámetros de Operación")

# --- INPUTS ---
tph = st.sidebar.number_input("Capacidad Real (Ton/h)", value=150)
v_ms = st.sidebar.slider("Velocidad (m/s)", 0.5, 2.0, 1.2)
altura = st.sidebar.number_input("Altura (m)", value=33.5)
p_cadena = st.sidebar.number_input("Peso Cadena (lb)", value=2400)
p_cangilones = st.sidebar.number_input("Peso Cangilones (lb)", value=11820)
d_pin = st.sidebar.slider("Diámetro del Pin (mm)", 20.0, 50.0, 34.74)
res_mpa = st.sidebar.number_input("Resistencia Tracción (Su) - MPa", value=980)

# --- CÁLCULOS TÉCNICOS ---
flujo_kgs = (tph * 1000) / 3600
p_material_lb = ((flujo_kgs / v_ms) * altura) * 2.20462
t_max_lb = p_cadena + p_cangilones + p_material_lb
f_n = t_max_lb * 4.44822

# Área Transversal (Doble Corte)
area_simple = np.pi * (d_pin / 2)**2
area_total = 2 * area_simple

# Esfuerzos Cortantes
tau_medio = f_n / area_total
# Asumimos esfuerzo alternante del 20% por vibraciones y arranque
tau_alt = tau_medio * 0.20 

# Resistencia al Corte (Von Mises)
ssu = res_mpa * 0.577 # Resistencia última al corte
sse = ssu * 0.40      # Límite de fatiga corregido (aprox)

# Criterio de Goodman para Corte
# (tau_alt / sse) + (tau_medio / ssu) = 1/FS_fatiga
fs_fatiga = 1 / ((tau_alt / sse) + (tau_medio / ssu))

# --- GRÁFICOS ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# 1. DCL SPROCKET Y PIN REALISTA
ax1.set_title("DCL: MECANISMO Y ENSAMBLE", fontweight='bold')
ax1.add_patch(plt.Circle((0.3, 0.7), 0.15, color='#454545')) # Sprocket
ax1.add_patch(plt.Rectangle((0.6, 0.4), 0.35, 0.08, color='#BDBDBD', ec='black')) # Pin
ax1.add_patch(plt.Rectangle((0.6, 0.3), 0.06, 0.3, color='#757575')) # Placa Ext
ax1.add_patch(plt.Rectangle((0.89, 0.3), 0.06, 0.3, color='#757575')) # Placa Ext
ax1.text(0.77, 0.5, "SECCIÓN TRANSVERSAL", ha='center', fontsize=8, fontweight='bold')
ax1.axis('off')

# 2. DIAGRAMA DE ESFUERZOS CORTANTES EN EL ÁREA TRANSVERSAL
ax2.set_title("ANÁLISIS DE ÁREA TRANSVERSAL Y CORTE", fontweight='bold')
circle = plt.Circle((0.5, 0.5), 0.3, color='lightgray', ec='black', lw=2)
ax2.add_patch(circle)
# Distribución de esfuerzos cortantes (Parabólica simplificada)
y = np.linspace(-0.3, 0.3, 100)
tau_dist = (1 - (y/0.3)**2)
for i in range(0, 100, 10):
    ax2.annotate('', xy=(0.5 + tau_dist[i]*0.2, 0.5 + y[i]), xytext=(0.5, 0.5 + y[i]),
                 arrowprops=dict(arrowstyle='->', color='red'))
ax2.text(0.5, 0.85, f"Área: {area_total:.1f} mm²", ha='center', fontweight='bold')
ax2.text(0.8, 0.5, "τ_max", color='red', fontweight='bold')
ax2.axis('off')

st.pyplot(fig)

# --- ANÁLISIS DE FALLA: MÉTODO DE GOODMAN ---
st.markdown("---")
st.subheader("🏁 Análisis de Seguridad por Fatiga (Método de Goodman)")

col_left, col_right = st.columns(2)

with col_left:
    st.write("**Parámetros de Fatiga (Corte):**")
    st.info(f"""
    - **Esfuerzo Cortante Medio (τm):** {tau_medio:.2f} MPa
    - **Esfuerzo Cortante Alternante (τa):** {tau_alt:.2f} MPa
    - **Resistencia Última al Corte (Ssu):** {ssu:.2f} MPa
    - **Límite de Resistencia a la Fatiga (Sse):** {sse:.2f} MPa
    """)

with col_right:
    st.write("**Resultado del Criterio de Goodman:**")
    if fs_fatiga > 1.5:
        st.success(f"### FS FATIGA: {fs_fatiga:.2f}\nDiseño Seguro contra fatiga cíclica.")
    else:
        st.error(f"### FS FATIGA: {fs_fatiga:.2f}\nFALLA INMINENTE POR FATIGA. La grieta se propagará.")

# Gráfico de Goodman
fig2, ax3 = plt.subplots(figsize=(8, 4))
ax3.plot([0, ssu], [sse, 0], 'g--', label='Línea de Goodman (Corte)')
ax3.scatter(tau_medio, tau_alt, color='red', s=100, zorder=5, label='Estado de Operación')
ax3.set_xlabel("Esfuerzo Medio (τm) [MPa]")
ax3.set_ylabel("Esfuerzo Alternante (τa) [MPa]")
ax3.set_title("Diagrama de Goodman: Seguridad vs Fatiga")
ax3.grid(True, alpha=0.3)
ax3.legend()
st.pyplot(fig2)

st.warning("**Nota técnica:** La fractura que observaste en el pin original es característica de un punto de operación que sobrepasó la línea de Goodman debido al desgaste abrasivo del clinker, lo cual redujo la sección transversal y aumentó los esfuerzos reales.")
