import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==============================================================================
# CONFIGURACIÓN DE LA INTERFAZ DE INGENIERÍA
# ==============================================================================
st.set_page_config(
    page_title="Simulador CFD Multi-Variable - UNACEM", 
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

st.title("⚙️ Simulador CFD Co-axial: Control de Ángulo y Radio de Esquina")
st.markdown("""
**Optimización Geométrica Avanzada para la Placa Superior del Ventilador de Tiro**  
Modifica simultáneamente el ángulo de inclinación y el radio del filete de soldadura para analizar el comportamiento dinámico de los vórtices.
""")

# ==============================================================================
# PANEL DE CONTROL INTERACTIVO (BARRA LATERAL)
# ==============================================================================
st.sidebar.header("🛠️ Variables de Diseño Geométrico")

# CONTROL 1: El ángulo de la chapa
angulo_deg = st.sidebar.slider("Ángulo de la Transición Externa (Grados)", 90, 180, 90, step=5)

# CONTROL 2: El radio de curvatura o filete de aporte
radio_mm = st.sidebar.slider("Radio de Suavizado / Filete de Soldadura (mm)", 0, 250, 0, step=25)

st.sidebar.markdown("---")
st.sidebar.header("📋 Parámetros de Operación")
rpm = st.sidebar.slider("Velocidad de Rotación (RPM)", 500, 1200, 1040, step=10)
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
# NÚCLEO MATEMÁTICO: MODELADO ULTRA-PRECISO DEL REMOLINO (SIN CAMBIOS)
# ==============================================================================
nx, ny = 180, 180  
x = np.linspace(0.1, 4.9, nx)
y = np.linspace(0.1, 4.9, ny)
X, Y = np.meshgrid(x, y)

factor_angulo = (angulo_deg - 90) / 90.0
factor_radio = radio_mm / 250.0

x_entrada = 2.0  
y_quiebre = 2.5 - (1.3 * factor_angulo)  
x_fin = 4.8

angulo_rad = np.radians(angulo_deg)
if angulo_deg == 90 or angulo_deg == 180:
    y_fin = y_quiebre
else:
    y_fin = y_quiebre - (x_fin - x_entrada) * np.tan(angulo_rad - np.pi/2)
    if y_fin < 0.4: y_fin = 0.4 

U_base = 2.0 * X * (Y**0.15)
V_base = -1.6 * (Y**1.05)

vortex_x = x_entrada + 0.45
vortex_y = y_quiebre - 0.60

r1_sq = (X - vortex_x)**2 + (Y - vortex_y)**2

intensidad_vortex = 8.5 * (1.0 + 1.5 * factor_angulo) * (1.0 - factor_radio)
if intensidad_vortex < 0: intensidad_vortex = 0

core = 0.15  
eps = 1e-5

U_vortex = -intensidad_vortex * (Y - vortex_y) / (r1_sq + core + eps)
V_vortex =  intensidad_vortex * (X - vortex_x) / (r1_sq + core + eps)

zona_turbulenta = np.exp(-((X - vortex_x)**2 + (Y - vortex_y)**2) / 0.8)

U_final = U_base * (1.0 - 0.9 * zona_turbulenta * (1.0 - factor_radio)) + U_vortex * zona_turbulenta
V_final = V_base * (1.0 - 0.9 * zona_turbulenta * (1.0 - factor_radio)) + V_vortex * zona_turbulenta

Vel_magnitud = np.sqrt(U_final**2 + V_final**2)

# ==============================================================================
# DESPLIEGUE GRÁFICO (REDUCIDO A FORMATO MONITOR COMPACTO)
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
    ax.plot([x_entrada, x_entrada, x_fin], [5.0, y_quiebre, y_fin], color='#df00ff', linewidth=5)
    ax.plot(x_entrada, y_quiebre, 'ro', markersize=8)
else:
    r_diseno = 0.15 + 1.1 * factor_radio
    alfa = angulo_rad - np.pi/2
    theta_curva = np.linspace(np.pi, np.pi + alfa, 50)
    
    x_centro_r = x_entrada + r_diseno
    y_centro_r = y_quiebre + r_diseno
    
    x_c = x_centro_r + r_diseno * np.cos(theta_curva)
    y_c = y_centro_r + r_diseno * np.sin(theta_curva)
    
    if angulo_deg == 180:
        y_c = np.ones_like(x_c) * y_quiebre
        
    x_curva_real = np.concatenate((x_tramo1:=[x_entrada, x_entrada], x_c, x_tramo3:=[x_tangencia_inclinada:=x_entrada + r_diseno + r_diseno * np.cos(np.pi + alfa) if angulo_deg != 180 else x_entrada + r_diseno * 2.0, x_fin]))
    y_curva_real = np.concatenate((y_tramo1:=[5.0, y_quiebre + r_diseno], y_c, y_tramo3:=[y_quiebre + r_diseno + r_diseno * np.sin(np.pi + alfa) if angulo_deg != 180 else y_quiebre, y_fin]))
    
    ax.plot(x_curva_real, y_curva_real, color='#df00ff', linewidth=6)

# Indicadores fijos en el lienzo
ax.text(4.6, 4.6, f"Reynolds (Re): {reynolds:.2e}", 
        color='#ffffff', fontsize=9, weight='bold',
        ha='right', va='top',
        bbox=dict(facecolor='#1e293b', alpha=0.7, edgecolor='#3b82f6', boxstyle='round,pad=0.5'))

if intensidad_vortex > 0.6:
    estado_flujo = "🔴 FLUX: TURBULENTO (RECIRCULACIÓN)"
    color_caja = '#ff3333'
else:
    estado_flujo = "🟢 FLUX: LAMINAR / GUIADO"
    color_caja = '#00ffcc'

ax.text(0.4, 0.4, estado_flujo, 
        color=color_caja, fontsize=8.5, weight='bold',
        ha='left', va='bottom',
        bbox=dict(facecolor='#0e1117', alpha=0.8, edgecolor=color_caja, boxstyle='round,pad=0.6'))

ax.set_xlim(0.2, 4.8)
ax.set_ylim(0.2, 4.8)
ax.axis('off')
fig.colorbar(strm.lines, ax=ax, label='Velocidad del Fluido (m/s)', pad=0.02)

# Carga directa en la pantalla principal
st.pyplot(fig)

# ==============================================================================
# DIAGNÓSTICO TÉCNICO INFERIOR 
# ==============================================================================
st.markdown("---")
st.header("📋 Evaluación de Ingeniería en Tiempo Real")
st.write(f"**Configuración Actual**: Ángulo de {angulo_deg}° con un Radio de {radio_mm} mm.")
if intensidad_vortex > 0.6:
    st.warning("El aire experimenta un desprendimiento al pasar el quiebre de la chapa. Se forman remolinos en la zona inferior cóncava debido al cambio de dirección abrupto.")
else:
    st.success("La combinación de parámetros permite un paso suave del gas, minimizando las pérdidas energéticas en el tiro del ventilador.")
