import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Análisis de Esfuerzo Transversal - Elevador", layout="wide")
st.title("🛡️ Sistema de Diagnóstico: Esfuerzo Cortante en Sección Transversal")

# --- SIDEBAR: DATOS DE ENTRADA ---
st.sidebar.header("📊 Operación y Cargas")
tph = st.sidebar.number_input("Capacidad (Ton/h)", value=150)
v_ms = st.sidebar.slider("Velocidad (m/s)", 0.5, 2.0, 1.2)
altura = st.sidebar.number_input("Altura entre centros (m)", value=33.5)

st.sidebar.header("⚙️ Geometría y Material")
d_pin = st.sidebar.slider("Diámetro del Pin (mm)", 20.0, 60.0, 34.74)
su_mpa = st.sidebar.number_input("Resistencia Última Su (MPa)", value=980)
sy_mpa = st.sidebar.number_input("Límite Elástico Sy (MPa)", value=835)

st.sidebar.header("⚠️ Condición de la Bota")
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
reaccion_n = f_n / 2

# ÁREA DE LA SECCIÓN TRANSVERSAL (SIN MULTIPLICAR X2)
area_pin = (np.pi * (d_pin/2)**2)
tau_m = f_n / area_pin  # Esfuerzo en el plano de corte
tau_a = tau_m * 0.25    # Esfuerzo alternante

# Propiedades de Corte
ssu, ssy = su_mpa * 0.577, sy_mpa * 0.577
sse = ssu * 0.35 

# --- BLOQUE 1: DIAGRAMAS REALISTAS (DCL) ---
col1, col2 = st.columns(2)

with col1:
    st.write("### DCL: Sprocket con Desglose de Pesos")
    fig1, ax1 = plt.subplots(figsize=(8, 8))
    ax1.add_patch(plt.Circle((0.5, 0.6), 0.22, color='#333333', zorder=2))
    for i in range(12):
        ang = np.deg2rad(i * 30)
        p = [[0.5 + 0.22*np.cos(ang-0.1), 0.6 + 0.22*np.sin(ang-0.1)],
             [0.5 + 0.30*np.cos(ang-0.06), 0.6 + 0.30*np.sin(ang-0.06)],
             [0.5 + 0.30*np.cos(ang+0.06), 0.6 + 0.30*np.sin(ang+0.06)],
             [0.5 + 0.22*np.cos(ang+0.1), 0.6 + 0.22*np.sin(ang+0.1)]]
        ax1.add_patch(patches.Polygon(p, color='#333333', zorder=1))
    ax1.annotate('', xy=(0.8, 0.1), xytext=(0.8, 0.6), arrowprops=dict(facecolor='red', width=4))
    ax1.text(0.82, 0.45, f"T_Total: {t_total_lb:,.0f} lb", color='red', fontweight='bold', fontsize=12)
    ax1.text(0.82, 0.15, f"• Mat: {p_mat_lb:,.0f} lb\n• Bota: {f_exc_lb:,.0f} lb\n• Cang: {p_cang_lb:,.0f} lb\n• Cad: {p_cad_lb:,.0f} lb", color='gray', fontsize=9)
    ax1.axis('off'); st.pyplot(fig1)

with col2:
    st.write("### DCL: Pin con Reacciones y Sección de Corte")
    fig2, ax2 = plt.subplots(figsize=(8, 8))
    ax2.add_patch(plt.Rectangle((0.1, 0.45), 0.8, 0.1, color='#BDBDBD', ec='black', zorder=4))
    ax2.add_patch(plt.Rectangle((0.1, 0.3), 0.12, 0.4, color='#757575', alpha=0.9)) # Placa Izq
    ax2.add_patch(plt.Rectangle((0.78, 0.3), 0.12, 0.4, color='#757575', alpha=0.9)) # Placa Der
    ax2.add_patch(plt.Rectangle((0.32, 0.35), 0.36, 0.3, color='#9E9E9E', hatch='//')) # Carga
    # Vectores Reacción y Carga
    ax2.annotate('', xy=(0.16, 0.9), xytext=(0.16, 0.7), arrowprops=dict(facecolor='blue', width=3))
    ax2.annotate('', xy=(0.84, 0.9), xytext=(0.84, 0.7), arrowprops=dict(facecolor='blue', width=3))
    ax2.text(0.16, 0.93, f"R/2: {reaccion_n:,.0f} N", color='blue', ha='center', fontsize=9)
    ax2.text(0.84, 0.93, f"R/2: {reaccion_n:,.0f} N", color='blue', ha='center', fontsize=9)
    ax2.annotate('', xy=(0.5, 0.1), xytext=(0.5, 0.45), arrowprops=dict(facecolor='red', width=5))
    ax2.text(0.52, 0.15, f"Carga: {f_n:,.0f} N", color='red', fontweight='bold')
    # Plano de análisis (Donde ocurre el esfuerzo tau)
    ax2.axvline(0.27, color='orange', ls='-', lw=3, label='Plano de Análisis')
    ax2.text(0.27, 0.8, "PLANO DE\nESFUERZO", color='orange', ha='center', fontweight='bold')
    ax2.axis('off'); st.pyplot(fig2)

# --- BLOQUE 2: COMPARATIVA DE CRITERIOS DE FALLA ---
st.markdown("---")
st.write("### Análisis de Fatiga en el Plano de Corte")
col_graf, col_tab = st.columns([2, 1])

with col_graf:
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    tm_range = np.linspace(0, ssu, 100)
    ax3.plot([0, ssy], [sse, 0], 'green', label='SODERBERG (Fluencia)', lw=2)
    ax3.plot([0, ssu], [sse, 0], 'blue', ls='--', label='GOODMAN (Fractura)', lw=2)
    ax3.plot(tm_range, sse*(1-(tm_range/ssu)**2), 'orange', label='GERBER (Parabólico)', lw=2)
    ax3.scatter(tau_m, tau_a, color='red', s=200, edgecolor='black', zorder=10, label='Punto de Operación')
    ax3.set_xlabel("τ_medio (MPa)"); ax3.set_ylabel("τ_alternante (MPa)"); ax3.legend(); ax3.grid(True, alpha=0.3)
    st.pyplot(fig3)

with col_tab:
    fs_sod = 1 / ((tau_a/sse) + (tau_m/ssy))
    fs_goo = 1 / ((tau_a/sse) + (tau_m/ssu))
    fs_ger = 1 / ((tau_a/sse) + (tau_m/ssu)**2)
    st.write("**Resultados (Área Simple):**")
    st.info(f"Área Seccional: {area_pin:.2f} mm²")
    st.table({
        "Criterio": ["Soderberg", "Goodman", "Gerber"],
        "FS": [f"{fs_sod:.2f}", f"{fs_goo:.2f}", f"{fs_ger:.2f}"],
        "Estado": ["OK" if fs_sod > 1.0 else "FALLA" for _ in range(3)]
    })

st.warning(f"**Nota:** Al usar el **área simple** de {area_pin:.2f} mm², el esfuerzo cortante calculado es de **{tau_m:.2f} MPa**. Este es el valor de esfuerzo real que experimenta el material en cada plano de unión de la cadena.")
