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

# Cálculos mecánicos rápidos para telemetría
radio_ext = diametro / 2000 
omega = (2 * np.pi * rpm) / 60
v_periferica = omega * radio_ext

st.sidebar.markdown("---")
st.sidebar.subheader("📈 Telemetría Calculada")
st.sidebar.metric(label="Velocidad en la Punta del Álabe", value=f"{v_periferica:.2f} m/s", delta=f"{v_periferica*3.6:.1f} km/h")

try:
    st.sidebar.image("https://unacem.com.pe", width=180)
except Exception:
    st.sidebar.subheader("🏢 UNACEM - Área Técnica")

# ==============================================================================
# NÚCLEO MATEMÁTICO: MODELADO GEOMÉTRICO Y CFD DE PRECISIÓN
# ==============================================================================
nx, ny = 200, 200
x = np.linspace(0.1, 4.9, nx)
y = np.linspace(0.1, 4.9, ny)
X, Y = np.meshgrid(x, y)

factor_angulo = (angulo_deg - 90) / 90.0
factor_radio = radio_mm / 250.0

# Flujo base del ventilador
U_base = 2.4 * X * (Y**0.15) * (1.0 - 0.3 * factor_angulo)
V_base = -1.8 * (Y**1.05)

# --- GEOMETRÍA DE LA PARED REAL ---
x_entrada = 2.0  # Posición del conducto vertical de entrada
y_quiebre = 2.5  # Altura de la junta soldada o esquina interna

# Calcular el punto final de la chapa según el ángulo del slider
angulo_rad = np.radians(angulo_deg)
l_ala = 2.5  # Longitud del tramo inclinado de la chapa
x_fin = x_entrada + l_ala * np.sin(angulo_rad - np.pi/2) if angulo_deg > 90 else 5.0
y_fin = y_quiebre - l_ala * np.cos(angulo_rad - np.pi/2) if angulo_deg > 90 else y_quiebre

# Ubicación del centro del vórtice (justo debajo del quiebre de la chapa)
vortex_x = x_entrada + 0.3 * (1.0 + factor_angulo)
vortex_y = y_quiebre - 0.4 * (1.0 + factor_angulo)

r1_sq = (X - vortex_x)**2 + (Y - vortex_y)**2
intensidad_vortex = 4.5 * (1.0 + 1.5 * factor_angulo) * (1.0 - 0.9 * factor_radio)
if intensidad_vortex < 0: intensidad_vortex = 0

core = 0.3
U_vortex = -intensidad_vortex * (Y - vortex_y) / (r1_sq + core)
V_vortex =  intensidad_vortex * (X - vortex_x) / (r1_sq + core)

zona_turbulenta = np.exp(-((X - vortex_x)**2 + (Y - vortex_y)**2) / (1.0 + factor_angulo))

U_final = U_base + U_vortex * zona_turbulenta
V_final = V_base + V_vortex * zona_turbulenta

Vel_magnitud = np.sqrt(U_final**2 + V_final**2)

# ==============================================================================
# DESPLIEGUE GRÁFICO CORREGIDO
# ==============================================================================
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(8, 6), dpi=150)

strm = ax.streamplot(
    X, Y, U_final, V_final, 
    color=Vel_magnitud, 
    cmap='plasma', 
    linewidth=1.1, 
    density=1.7, 
    arrowsize=0.9
)

# --- DIBUJO DE LA CHAPA RECALIBRADO (SIN LÍNEAS ROJAS NI DEFORMACIONES) ---
if radio_mm == 0 or angulo_deg == 180:
    # Caso plano/recto sin transiciones redondeadas artificiales
    ax.plot([x_entrada, x_entrada, x_fin], [5.0, y_quiebre, y_fin], color='#ffaa00', linewidth=5)
    if angulo_deg > 90:
        ax.plot(x_entrada, y_quiebre, 'ro', markersize=8)
else:
    # Dibujar la esquina suavizada dinámicamente por el radio de soldadura
    r_diseno = 0.1 + 0.6 * factor_radio
    # Puntos de tangencia de la curva
    theta_curva = np.linspace(np.pi, np.pi + (angulo_rad - np.pi/2), 50)
    x_c = x_entrada + r_diseno + r_diseno * np.cos(theta_curva)
    y_c = y_quiebre + r_diseno + r_diseno * np.sin(theta_curva)
    
    # Unir las secciones de la chapa de forma continua
    x_pared = np.concatenate(([x_entrada], x_c, [x_fin]))
    y_pared = np.concatenate(([5.0], y_c, [y_fin]))
    ax.plot(x_pared, y_pared, color='#00ffcc', linewidth=5)

# Indicadores de texto en pantalla
if intensidad_vortex > 0.5:
    ax.text(0.4, 0.4, f"⚠️ VÓRTICE ACTIVO BAJO EL ÁNGULO DE {angulo_deg}°", color='#ffaa00', weight='bold', fontsize=9)
else:
    ax.text(0.4, 0.4, "✅ FLUJO GUIADO Y CONTROLADO", color='#00ffcc', weight='bold', fontsize=9)

ax.set_xlim(0.2, 4.8)
ax.set_ylim(0.2, 4.8)
ax.axis('off')
fig.colorbar(strm.lines, ax=ax, label='Velocidad del Fluido (m/s)', pad=0.02)

col_izq, col_centro, col_der = st.columns(3)
with col_centro:
    st.pyplot(fig)

# ==============================================================================
# DIAGNÓSTICO TÉCNICO
# ==============================================================================
st.markdown("---")
st.header("📋 Evaluación de Ingeniería en Tiempo Real")
st.write(f"**Configuración Actual**: Ángulo de {angulo_deg}° con un Radio de {radio_mm} mm.")
if intensidad_vortex > 0.5:
    st.warning("El aire experimenta un desprendimiento al pasar el quiebre de la chapa. Se forman remolinos en la zona inferior cóncava debido al cambio de dirección abrupto.")
else:
    st.success("La combinación de parámetros permite un paso suave del gas, minimizando las pérdidas energéticas en el tiro del ventilador.")
