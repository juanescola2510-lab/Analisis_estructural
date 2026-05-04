import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Análisis Integral de Elevador de Cangilones", layout="wide")

st.title("🏗️ Sistema Integral de Análisis de Falla: Cadena y Componentes")
st.sidebar.header("📊 Parámetros de Operación")

# --- ENTRADAS GENERALES ---
tph = st.sidebar.number_input("Capacidad Real (Ton/h)", value=150)
v_ms = st.sidebar.slider("Velocidad (m/s)", 0.5, 2.0, 1.2)
altura = st.sidebar.number_input("Altura entre centros (m)", value=33.5)
p_cadena = st.sidebar.number_input("Peso Cadena (lb)", value=2400)
p_cangilones = st.sidebar.number_input("Peso Total Cangilones (lb)", value=11820)
d_pin = st.sidebar.slider("Diámetro del Pin (mm)", 20.0, 55.0, 34.74)

# Propiedades del Acero 35CrMo
st.sidebar.subheader("🛠️ Propiedades del Material")
su_mpa = st.sidebar.number_input("Resistencia Última (Su) - MPa", value=980)
sy_mpa = st.sidebar.number_input("Límite Elástico (Sy) - MPa", value=835)

# NUEVA ENTRADA: CONDICIÓN DE LA BOTA
st.sidebar.subheader("⚠️ Estado de la Bota")
nivel_acumulacion = st.sidebar.select_slider(
    "Nivel de Atascamiento",
    options=["Limpio", "Moderado", "Crítico", "Obstrucción Total"],
    value="Limpio"
)

# --- LÓGICA DE CÁLCULO ---
flujo_kgs = (tph * 1000) / 3600
p_material_lb = ((flujo_kgs / v_ms) * altura) * 2.20462

# Cálculo de Fuerza de Excavación Extra (Fexc) por acumulación
mapeo_fexc = {"Limpio": 0.10, "Moderado": 0.50, "Crítico": 1.50, "Obstrucción Total": 3.00}
f_exc_lb = p_material_lb * mapeo_fexc[nivel_acumulacion]

# Tensión Total Real
t_total_lb = p_cadena + p_cangilones + p_material_lb + f_exc_lb
f_n = t_total_lb * 4.44822

# Esfuerzos Cortantes (Doble Corte)
area_total = 2 * (np.pi * (d_pin / 2)**2)
tau_m = f_n / area_total            # Esfuerzo medio
tau_a = tau_m * 0.25                # Esfuerzo alternante

# Propiedades de Corte (Von Mises)
ssu = su_mpa * 0.577; ssy = sy_mpa * 0.577; sse = ssu * 0.35

# Factores de Seguridad
fs_soderberg = 1 / ((tau_a / sse) + (tau_m / ssy))
fs_goodman = 1 / ((tau_a / sse) + (tau_m / ssu))
fs_gerber = 1 / ((tau_a / sse) + (tau_m / ssu)**2)

# --- BLOQUE 1: DIAGRAMAS DE CUERPO LIBRE (SPROCKET Y ENSAMBLE) ---
col_dcl1, col_dcl2 = st.columns(2)

with col_dcl1:
    st.write("### DCL: Mecanismo Superior")
    fig1, ax1 = plt.subplots(figsize=(6, 6))
    ax1.add_patch(plt.Circle((0.5, 0.6), 0.25, color='#454545', zorder=2)) # Sprocket
    for i in range(12):
        angle = np.deg2rad(i * 30); x = 0.5 + 0.27 * np.cos(angle); y = 0.6 + 0.27 * np.sin(angle)
        ax1.add_patch(plt.Circle((x, y), 0.04, color='#454545'))
    ax1.annotate('', xy=(0.78, 0.1), xytext=(0.78, 0.6), arrowprops=dict(facecolor='red', width=4))
    ax1.text(0.8, 0.35, f"T_Total: {t_total_lb:,.0f} lb", color='red', fontweight='bold')
    ax1.axis('off'); st.pyplot(fig1)

with col_dcl2:
    st.write("### DCL: Ensamble del Pin (Placas)")
    fig2, ax2 = plt.subplots(figsize=(6, 6))
    ax2.add_patch(plt.Rectangle((0.1, 0.45), 0.8, 0.1, color='#BDBDBD', ec='black', zorder=4)) # Pin
    ax2.add_patch(plt.Rectangle((0.1, 0.3), 0.12, 0.4, color='#757575', alpha=0.9)) # Placa Ext
    ax2.add_patch(plt.Rectangle((0.78, 0.3), 0.12, 0.4, color='#757575', alpha=0.9)) # Placa Ext
    ax2.add_patch(plt.Rectangle((0.32, 0.35), 0.36, 0.3, color='#9E9E9E', hatch='//')) # Placa Int
    ax2.axvline(0.27, color='red', ls='--'); ax2.axvline(0.73, color='red', ls='--')
    ax2.axis('off'); st.pyplot(fig2)

# --- BLOQUE 2: ANÁLISIS DE LA BOTA Y ÁREA TRANSVERSAL ---
st.markdown("---")
col_bota, col_trans = st.columns(2)

with col_bota:
    st.write(f"### DCL: Resistencia en Bota ({nivel_acumulacion})")
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    ax3.add_patch(plt.Rectangle((0.1, 0.1), 0.8, 0.3, color='#D2B48C', alpha=0.7)) # Material
    ax3.add_patch(plt.Rectangle((0.45, 0.3), 0.1, 0.2, color='gray', ec='black')) # Cangilón
    ax3.annotate('', xy=(0.55, 0.35), xytext=(0.85, 0.35), arrowprops=dict(facecolor='red', width=3))
    ax3.text(0.6, 0.45, f"F_Excavación: {f_exc_lb:,.0f} lb", color='red', fontweight='bold')
    ax3.axis('off'); st.pyplot(fig3)

with col_trans:
    st.write("### Distribución de Esfuerzo Cortante (τ)")
    fig4, ax4 = plt.subplots(figsize=(6, 6))
    ax4.add_patch(plt.Circle((0.5, 0.5), 0.4, color='#BDBDBD', ec='black', lw=2))
    y_vals = np.linspace(0.15, 0.85, 15)
    for yv in y_vals:
        l = 0.35 * (1 - ((yv-0.5)/0.35)**2)
        ax4.annotate('', xy=(0.5 + l, yv), xytext=(0.5, yv), arrowprops=dict(arrowstyle='->', color='red'))
    ax4.text(0.5, 0.5, f"τ_max = {tau_m:.2f} MPa", ha='center', color='red', fontweight='bold')
    ax4.axis('off'); st.pyplot(fig4)

# --- BLOQUE 3: COMPARATIVA DE FATIGA (SODERBERG, GOODMAN, GERBER) ---
st.markdown("---")
st.write("### Comparativa de Criterios de Falla")
fig5, ax5 = plt.subplots(figsize=(10, 6))
tm_range = np.linspace(0, ssu, 100)
ax5.plot([0, ssy], [sse, 0], 'green', label='SODERBERG (Fluencia)')
ax5.plot([0, ssu], [sse, 0], 'blue', ls='--', label='GOODMAN (Fractura)')
ax5.plot(tm_range, sse*(1-(tm_range/ssu)**2), 'orange', label='GERBER (Parabólico)')
ax5.scatter(tau_m, tau_a, color='red', s=150, edgecolor='black', zorder=10, label='Punto de Operación')
ax5.set_xlabel("τ_medio (MPa)"); ax5.set_ylabel("τ_alternante (MPa)"); ax5.legend(); ax5.grid(True, alpha=0.3)
st.pyplot(fig5)

# TABLA FINAL
st.table({
    "Criterio": ["Soderberg", "Goodman", "Gerber"],
    "Factor de Seguridad": [f"{fs_soderberg:.2f}", f"{fs_goodman:.2f}", f"{fs_gerber:.2f}"],
    "Resultado": ["Seguro" if fs_soderberg > 1.2 else "Riesgo" for _ in range(3)]
})
