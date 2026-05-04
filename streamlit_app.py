import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Análisis de Fatiga: Criterio de Soderberg", layout="wide")

st.title("🛡️ Seguridad Crítica: Análisis de Fatiga (Criterio de Soderberg)")
st.sidebar.header("📊 Parámetros del Sistema")

# --- ENTRADAS ---
tph = st.sidebar.number_input("Capacidad Real (Ton/h)", value=150)
v_ms = st.sidebar.slider("Velocidad (m/s)", 0.5, 2.0, 1.2)
altura = st.sidebar.number_input("Altura (m)", value=33.5)
p_cadena = st.sidebar.number_input("Peso Cadena (lb)", value=2400)
p_cangilones = st.sidebar.number_input("Peso Total Cangilones (lb)", value=11820)
d_pin = st.sidebar.slider("Diámetro del Pin (mm)", 20.0, 55.0, 34.74)

# Propiedades del Acero 35CrMo (Tratado)
st.sidebar.subheader("🛠️ Propiedades del Material")
su_mpa = st.sidebar.number_input("Resistencia Última (Su) - MPa", value=980)
sy_mpa = st.sidebar.number_input("Límite Elástico (Sy) - MPa", value=835)

# --- CÁLCULOS TÉCNICOS ---
flujo_kgs = (tph * 1000) / 3600
p_material_lb = ((flujo_kgs / v_ms) * altura) * 2.20462
t_max_lb = p_cadena + p_cangilones + p_material_lb
f_n = t_max_lb * 4.44822

# Área Transversal y Esfuerzos Cortantes
area_total = 2 * (np.pi * (d_pin / 2)**2)
tau_m = f_n / area_total            # Esfuerzo medio
tau_a = tau_m * 0.25                # Esfuerzo alternante (25% por impactos de clinker)

# Propiedades de Corte (Von Mises)
ssy = sy_mpa * 0.577                # Límite elástico al corte
sse = su_mpa * 0.577 * 0.35         # Límite de fatiga corregido para ambiente agresivo

# Criterio de Soderberg
# (tau_a / sse) + (tau_m / ssy) = 1/FS_soderberg
fs_soderberg = 1 / ((tau_a / sse) + (tau_m / ssy))

# --- VISUALIZACIÓN ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.write("### Área Transversal y Distribución de Corte")
    fig1, ax1 = plt.subplots(figsize=(6, 6))
    # Pin
    pin = plt.Circle((0.5, 0.5), 0.4, color='#BDBDBD', ec='black', lw=3)
    ax1.add_patch(pin)
    # Vectores de esfuerzo cortante
    y_vals = np.linspace(0.2, 0.8, 15)
    for y in y_vals:
        # Perfil de esfuerzo parabólico
        length = 0.3 * (1 - ((y-0.5)/0.3)**2)
        ax1.annotate('', xy=(0.5 + length, y), xytext=(0.5, y),
                     arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
    ax1.text(0.5, 0.5, "τ_medio", color='red', ha='center', fontweight='bold')
    ax1.axis('off')
    st.pyplot(fig1)

with col_graf2:
    st.write("### Diagrama de Soderberg")
    fig2, ax2 = plt.subplots(figsize=(6, 6))
    # Línea de Soderberg: Une Se con Sy
    ax2.plot([0, ssy], [sse, 0], 'b-', lw=3, label='Línea de Soderberg (Seguridad)')
    ax2.fill_between([0, ssy], [sse, 0], color='blue', alpha=0.1)
    # Punto de operación
    ax2.scatter(tau_m, tau_a, color='red', s=150, edgecolor='black', zorder=5, label='Estado de Carga Real')
    
    ax2.set_xlabel("Esfuerzo Medio τ_m (MPa)")
    ax2.set_ylabel("Esfuerzo Alternante τ_a (MPa)")
    ax2.set_xlim(0, ssy * 1.1)
    ax2.set_ylim(0, sse * 1.2)
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    st.pyplot(fig2)

# --- PANEL DE RESULTADOS ---
st.markdown("---")
st.subheader("📋 Diagnóstico Final bajo Soderberg")

res1, res2 = st.columns(2)
with res1:
    st.info(f"""
    **Análisis de Tensiones:**
    - Esfuerzo Medio (τm): `{tau_m:.2f} MPa`
    - Esfuerzo Alternante (τa): `{tau_a:.2f} MPa`
    - Resistencia Fluencia Corte (Ssy): `{ssy:.2f} MPa`
    """)

with res2:
    if fs_soderberg > 1.2:
        st.success(f"### FS SODERBERG: {fs_soderberg:.2f}\nDISEÑO SEGURO. No hay fluencia ni fatiga.")
    else:
        st.error(f"### FS SODERBERG: {fs_soderberg:.2f}\nRIESGO DE DEFORMACIÓN. El pin sufrirá elongación permanente.")

st.markdown("""
> **Diferencia Técnica:** A diferencia de Goodman, **Soderberg** no permite que el esfuerzo medio supere el límite elástico. Esto es fundamental en elevadores de una sola cadena, pues evita que los agujeros de las placas se ovalen y los pines se deformen antes de romperse.
""")
