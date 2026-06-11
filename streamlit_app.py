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
# NÚCLEO MATEMÁTICO: MODELADO COMBINADO DE ÁNGULO Y RADIO
# ==============================================================================
nx, ny = 200, 200
x = np.linspace(0.1, 4.9, nx)
y = np.linspace(0.1, 4.9, ny)
X, Y = np.meshgrid(x, y)

# Factores de ponderación independientes
factor_angulo = (angulo_deg - 90) / 90.0
factor_radio = radio_mm / 250.0

# Flujo base que se ve afectado por ambos parámetros
U_base = 2.4 * X * (Y**0.15) * (1.0 - 0.3 * factor_angulo)
V_base = -1.8 * (Y**1.05)

# Posicionamiento dinámico de los núcleos de recirculación
vortex1_x = 1.3 - (0.4 * factor_angulo) + (0.2 * factor_radio)
vortex1_y = 1.8 - (0.2 * factor_angulo) + (0.2 * factor_radio)
vortex2_x = 1.7 + (0.3 * factor_angulo) - (0.1 * factor_radio)
vortex2_y = 1.4 - (0.3 * factor_angulo) + (0.1 * factor_radio)

r1_sq = (X - vortex1_x)**2 + (Y - vortex1_y)**2
r2_sq = (X - vortex2_x)**2 + (Y - vortex2_y)**2

# Ley física combinada: El ángulo AGRANDA el vórtice, el radio lo DISMINUYE
intensidad_vortex = 4.5 * (1.0 + 2.0 * factor_angulo) * (1.0 - factor_radio) * (v_periferica / 98.02)
# Evitar intensidades negativas
if intensidad_vortex < 0: 
    intensidad_vortex = 0

core = 0.25 + (0.4 * factor_angulo)

U_vortex1 = -intensidad_vortex * (Y - vortex1_y) / (r1_sq + core)
V_vortex1 =  intensidad_vortex * (X - vortex1_x) / (r1_sq + core)

U_vortex2 =  (intensidad_vortex * 0.8) * (Y - vortex2_y) / (r2_sq + core)
V_vortex2 = -(intensidad_vortex * 0.8) * (X - vortex2_x) / (r2_sq + core)

ancho_turbulento = (1.2 + (1.8 * factor_angulo)) * (1.0 - 0.8 * factor_radio)
zona_turbulenta = np.exp(-((X - 1.5)**2 + (Y - 1.7)**2) / max(ancho_turbulento, 0.1))

# Campo de velocidades final acoplado
U_final = U_base + (U_vortex1 + U_vortex2) * zona_turbulenta
V_final = V_base + (V_vortex1 + V_vortex2) * zona_turbulenta

Vel_magnitud = np.sqrt(U_final**2 + V_final**2)

# ==============================================================================
# DESPLIEGUE GRÁFICO (CENTRAJE REQUERIDO POR STREAMLIT CLOUD)
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

# --- DIBUJO DINÁMICO DE LA GEOMETRÍA COMBINADA ---
angulo_rad = np.radians(angulo_deg)
x0, y0 = 1.8, 5.0
x_esquina, y_esquina = 1.8, 2.2

if radio_mm == 0:
    # Si el radio es cero, dibuja la chapa con quiebre angular recto dinámico
    y_salida_recta = y_esquina - (2.2 * factor_angulo)
    ax.plot([x0, x_esquina, 5.0], [y0, y_esquina, y_salida_recta], color='#ff3333', linewidth=5)
    ax.plot(x_esquina, y_esquina, 'ro', markersize=10)
else:
    # Si hay radio, calcula la curva adaptada al ángulo actual del slider
    theta = np.linspace(np.pi, np.pi + angulo_rad - np.pi/2, 50)
    r_dinamico = 0.3 + 2.5 * factor_radio
    
    x_centro = x_esquina + r_dinamico
    y_centro = y_esquina + r_dinamico
    
    x_curva = x_centro + r_dinamico * np.cos(theta)
    y_curva = y_centro + r_dinamico * np.sin(theta)
    
    y_salida_curva = y_esquina - (2.2 * factor_angulo)
    x_pared = np.concatenate(([x0], x_curva, [5.0]))
    y_pared = np.concatenate(([y0], y_curva, [y_salida_curva]))
    
    color_perfil = '#00ffcc' if radio_mm >= 150 and angulo_deg <= 110 else '#ffaa00'
    ax.plot(x_pared, y_pared, color=color_perfil, linewidth=5)

# Anotaciones dinámicas de texto dentro del lienzo
if intensidad_vortex > 0.5:
    ax.text(0.4, 0.4, "⚠️ VÓRTICES DE RECIRCULACIÓN PRESENTES", color='#ffaa00', weight='bold', fontsize=9)
else:
    ax.text(0.4, 0.4, "✅ FLUJO ENCAPSULADO / AERODINÁMICO", color='#00ffcc', weight='bold', fontsize=9)

ax.set_xlim(0.2, 4.8)
ax.set_ylim(0.2, 4.8)
ax.axis('off')
fig.colorbar(strm.lines, ax=ax, label='Velocidad del Fluido (m/s)', pad=0.02)

# Despliegue seguro en tres columnas para evitar el TypeError en la línea 156
col_izq, col_centro, col_der = st.columns([1, 4, 1])
with col_centro:
    st.pyplot(fig)

# ==============================================================================
# DIAGNÓSTICO TÉCNICO COMPUESTO
# ==============================================================================
st.markdown("---")
st.header("📋 Evaluación de Ingeniería en Tiempo Real")

# Matriz de conclusiones lógicas según la posición de ambos sliders
if angulo_deg == 90 and radio_mm == 0:
    st.error("""
    **Condición Crítica Localizada:** Estado actual del rodete en el taller. Ángulo recto de 90° sin radio de transición. 
    Los remolinos cerrados están confinados con fuerza en la esquina. La chapa sufrirá erosión localizada por el impacto cíclico del polvo.
    """)
elif angulo_deg > 135 and radio_mm == 0:
    st.error(f"""
    **Condición Crítica Masiva:** Chapa expandida a {angulo_deg}° sin radio de amortiguación. El aire impacta perpendicularmente contra una placa que tiende a ser plana. 
    Los vórtices bloquean el área neumática útil, restando succión al separador e incrementando la temperatura y el amperaje en el variador de frecuencia.
    """)
elif radio_mm >= 150 and angulo_deg == 90:
    st.success(f"""
    **Condición Optimizada por Mantenimiento:** Chapa estructural a 90° pero con un robusto filete de soldadura de {radio_mm} mm. 
    Aunque la chapa exterior es recta, el material de aporte dura (Vautid) ha redondeado internamente el codo. Los vórtices se han disipado por completo. ¡Excelente estrategia de reparación!
    """)
else:
    st.warning(f"""
    **Condición Intermedia Combinada:** Ángulo de {angulo_deg}° con un radio de mitigación de {radio_mm} mm. 
    El radio contrarresta parcialmente el efecto nocivo del ángulo abierto, ayudando a disminuir la velocidad de rotación del remolino, pero se recomienda incrementar el aporte de soldadura en el taller para estabilizar por completo la capa límite.
    """)
