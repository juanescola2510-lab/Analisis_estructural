import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==============================================================================
# CONFIGURACIÓN DE LA INTERFAZ DE INGENIERÍA
# ==============================================================================
st.set_page_config(
    page_title="Simulador CFD Campana Completa - UNACEM", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .reportview-container { background: #0e1117; }
    h1 { color: #f0f2f6; font-family: 'Helvetica Neue', sans-serif; font-weight: 700; }
    h2, h3 { color: #1f77b4; font-family: 'Helvetica Neue', sans-serif; }
    .stAlert { background-color: #1e293b; border-left: 5px solid #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚙️ Simulador CFD: Vista Frontal de la Campana de Succión Completa")
st.markdown("""
**Análisis de Distribución de Flujo Simétrico y Doble Vórtice en el Ingreso del Ventilador**  
Ajusta la geometría en la barra lateral para observar cómo el aire entra por el centro y se divide hacia ambos extremos del rodete.
""")

# ==============================================================================
# PANEL DE CONTROL INTERACTIVO (BARRA LATERAL)
# ==============================================================================
st.sidebar.header("🛠️ Variables de Diseño Geométrico")

# CONTROL 1: El ángulo de la chapa de la campana
angulo_deg = st.sidebar.slider("Ángulo de la Transición Externa (Grados)", 90, 180, 90, step=5)

# CONTROL 2: El radio de curvatura o suavizado de la campana
radio_mm = st.sidebar.slider("Radio de Suavizado de la Campana (mm)", 0, 250, 0, step=25)

st.sidebar.markdown("---")
st.sidebar.header("📋 Parámetros de Operación")
rpm = st.sidebar.slider("Velocidad de Rotación (RPM)", 500, 1200, 1040, step=10)
d_entrada = st.sidebar.slider("Diámetro Boca Aspiración / Cuello (mm)", 400, 1400, 950, step=50)
diametro = st.sidebar.number_input("Diámetro Exterior Placa (mm)", value=1800)
ancho_perif = st.sidebar.slider("Ancho de Periferia / Salida (mm)", 100, 300, 200, step=10)
densidad_gas = st.sidebar.number_input("Densidad del Gas (kg/m³)", value=0.95, step=0.05)

# Cálculos mecánicos y fluidodinámicos rápidos
radio_ext = diametro / 2000 
omega = (2 * np.pi * rpm) / 60
v_periferica = omega * radio_ext
reynolds = (densidad_gas * v_periferica * (ancho_perif / 1000)) / 1.81e-5

st.sidebar.markdown("---")
st.sidebar.header("📈 Telemetría Calculada")
st.sidebar.metric(label="Velocidad en la Punta del Álabe", value=f"{v_periferica:.2f} m/s", delta=f"{v_periferica*3.6:.1f} km/h")

try:
    st.sidebar.image("https://unacem.com.pe", width=180)
except Exception:
    st.sidebar.subheader("🏢 UNACEM - Área Técnica")

# ==============================================================================
# NÚCLEO MATEMÁTICO: MODELADO SIMÉTRICO CON CAMPANA DIVERGENTE CORREGIDA
# ==============================================================================
nx, ny = 190, 180  
x = np.linspace(0.1, 4.9, nx)
y = np.linspace(0.1, 4.9, ny)
X, Y = np.meshgrid(x, y)

factor_angulo = (angulo_deg - 90) / 90.0
factor_radio = radio_mm / 250.0

x_centro = 2.5
ancho_boca_visual = 3.4 * (d_entrada / diametro)

x_izq_entrada = x_centro - ancho_boca_visual / 2  
x_der_entrada = x_centro + ancho_boca_visual / 2  
y_quiebre = 2.8  

angulo_rad = np.radians(angulo_deg)
alpha_giro = np.pi - angulo_rad  

if angulo_deg == 90 or angulo_deg == 180:
    y_fin = y_quiebre
    x_fin_izq = 0.2
    x_fin_der = 4.8
else:
    y_fin = max(0.6, y_quiebre - 1.8 * np.sin(alpha_giro))
    x_fin_izq = max(0.2, x_izq_entrada - 1.8 * np.cos(alpha_giro))
    x_fin_der = min(4.8, x_der_entrada + 1.8 * np.cos(alpha_giro))

U_base = 2.8 * (X - x_centro) / (Y + 0.3)
V_base = -2.5 * (Y**0.95)

vortex_izq_x = x_izq_entrada - 0.45 * (1.0 + factor_angulo)
vortex_izq_y = y_quiebre - 0.60
r_izq_sq = (X - vortex_izq_x)**2 + (Y - vortex_izq_y)**2

vortex_der_x = x_der_entrada + 0.45 * (1.0 + factor_angulo)
vortex_der_y = y_quiebre - 0.60
r_der_sq = (X - vortex_der_x)**2 + (Y - vortex_der_y)**2

intensidad_vortex = 9.0 * (1.0 - factor_radio)
if intensidad_vortex < 0: intensidad_vortex = 0

core = 0.16  
eps = 1e-5

U_v_izq = -intensidad_vortex * (Y - vortex_izq_y) / (r_izq_sq + core + eps)
V_v_izq =  intensidad_vortex * (X - vortex_izq_x) / (r_izq_sq + core + eps)

U_v_der =  intensidad_vortex * (Y - vortex_der_y) / (r_der_sq + core + eps)
V_v_der = -intensidad_vortex * (X - vortex_der_x) / (r_der_sq + core + eps)

zona_turb_izq = np.exp(-((X - vortex_izq_x)**2 + (Y - vortex_izq_y)**2) / 0.8)
zona_turb_der = np.exp(-((X - vortex_der_x)**2 + (Y - vortex_der_y)**2) / 0.8)

U_final = U_base * (1.0 - 0.95 * (zona_turb_izq + zona_turb_der) * (1.0 - factor_radio)) + U_v_izq * zona_turb_izq + U_v_der * zona_turb_der
V_final = V_base * (1.0 - 0.95 * (zona_turb_izq + zona_turb_der) * (1.0 - factor_radio)) + V_v_izq * zona_turb_izq + V_v_der * zona_turb_der

Vel_magnitud = np.sqrt(U_final**2 + V_final**2)

# ==============================================================================
# DESPLIEGUE GRÁFICO FRONTAL COMPACTO (CON CORRECCIÓN DE TRAYECTORIA CÓNCAVA)
# ==============================================================================
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(9, 4.8), dpi=100)  

strm = ax.streamplot(
    X, Y, U_final, V_final, 
    color=Vel_magnitud, 
    cmap='turbo', 
    linewidth=1.1, 
    density=1.9, 
    arrowsize=0.9
)

if radio_mm == 0:
    ax.plot([x_izq_entrada, x_izq_entrada, x_fin_izq], [5.0, y_quiebre, y_fin], color='#df00ff', linewidth=5)
    ax.plot(x_izq_entrada, y_quiebre, 'ro', markersize=6)
    ax.plot([x_der_entrada, x_der_entrada, x_fin_der], [5.0, y_quiebre, y_fin], color='#df00ff', linewidth=5)
    ax.plot(x_der_entrada, y_quiebre, 'ro', markersize=6)
else:
    # ESCALA REFORZADA CORREGIDA PARA BAJAR Y ABRIRSE EN PARÁBOLA CONTINUA
    r_diseno = 0.15 + 1.1 * factor_radio
    
    # 1. Curva Lado Izquierdo: Corregida para nacer vertical y suavizar hacia el costado bajo
    theta_izq = np.linspace(0, -np.pi/2 * factor_angulo if angulo_deg > 90 else -np.pi/2, 40)
    x_centro_izq = x_izq_entrada - r_diseno
    y_centro_izq = y_quiebre + r_diseno
    
    x_c_izq = x_centro_izq + r_diseno * np.cos(theta_izq)
    y_c_izq = y_centro_izq + r_diseno * np.sin(theta_izq) - (r_diseno * factor_angulo)
    
    if angulo_deg == 180: y_c_izq = np.ones_like(x_c_izq) * y_quiebre
    
    x_pared_izq = np.concatenate(([x_izq_entrada, x_izq_entrada], x_c_izq, [x_fin_izq]))
    y_pared_izq = np.concatenate(([5.0, y_quiebre], y_c_izq, [y_fin]))
    ax.plot(x_pared_izq, y_pared_izq, color='#df00ff', linewidth=6)
    
    # 2. Curva Lado Derecho (Espejo exacto hacia abajo y afuera)
    theta_der = np.linspace(np.pi, np.pi + np.pi/2 * factor_angulo if angulo_deg > 90 else np.pi + np.pi/2, 40)
    x_centro_der = x_der_entrada + r_diseno
    y_centro_der = y_quiebre + r_diseno
    
    x_c_der = x_centro_der + r_diseno * np.cos(theta_der)
    y_c_der = y_centro_der + r_diseno * np.sin(theta_der) - (r_diseno * factor_angulo)
    
    if angulo_deg == 180: y_c_der = np.ones_like(x_c_der) * y_quiebre
    
    x_pared_der = np.concatenate(([x_der_entrada, x_der_entrada], x_c_der, [x_fin_der]))
    y_pared_der = np.concatenate(([5.0, y_quiebre], y_c_der, [y_fin]))
    ax.plot(x_pared_der, y_pared_der, color='#df00ff', linewidth=6)

# Indicadores fijos en el lienzo
ax.text(4.6, 4.6, f"Reynolds (Re): {reynolds:.2e}", 
        color='#ffffff', fontsize=9, weight='bold', ha='right', va='top',
        bbox=dict(facecolor='#1e293b', alpha=0.7, edgecolor='#3b82f6', boxstyle='round,pad=0.5'))

if intensidad_vortex > 0.6:
    estado_flujo = "🔴 FLUX: TURBULENTO (RECIRCULACIÓN)"
    color_caja = '#ff3333'
else:
    estado_flujo = "🟢 FLUX: LAMINAR / GUIADO"
    color_caja = '#00ffcc'

ax.text(0.4, 0.4, estado_flujo, 
        color=color_caja, fontsize=8.5, weight='bold', ha='left', va='bottom',
        bbox=dict(facecolor='#0e1117', alpha=0.8, edgecolor=color_caja, boxstyle='round,pad=0.6'))

ax.text(2.5, 4.6, f"↔️ Diámetro Real: {d_entrada} mm", 
        color='#ff3344', fontsize=9, weight='bold', ha='center', va='top',
        bbox=dict(facecolor='#0e1117', alpha=0.8, edgecolor='#ff3344', boxstyle='round,pad=0.4'))

ax.set_xlim(0.1, 4.9)
ax.set_ylim(0.2, 4.8)
ax.axis('off')
fig.colorbar(strm.lines, ax=ax, label='Velocidad del Fluido (m/s)', pad=0.02)

col_izq, col_centro, col_der = st.columns(3)
with col_centro:
    st.pyplot(fig)

# ==============================================================================
# DIAGNÓSTICO TÉCNICO INFERIOR 
# ==============================================================================
st.markdown("---")
st.header("📋 Evaluación de Ingeniería en Tiempo Real")
st.write(f"**Configuración Frontal**: Ángulo de {angulo_deg}° con un Radio de {radio_mm} mm y Boca de {d_entrada} mm.")
if intensidad_vortex > 0.6:
    st.warning("El estrechamiento del flujo central incrementa la velocidad de succión. Al chocar contra las esquinas ortogonales, se induce una severa recirculación bifásica simétrica.")
else:
    st.success("La campana simétrica se expande hacia los extremos de manera divergente, encauzando y distribuyendo el aire en paralelo a las paredes cóncavas moradas.")
