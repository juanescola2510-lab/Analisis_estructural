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
# NÚCLEO MATEMÁTICO: MODELADO COMBINADO DE ÁNGULO Y RADIO REACALIBRADO
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

# --- DETECCIÓN DINÁMICA DEL PUNTO DE QUIEBRE / ESCALÓN ---
# Si el ángulo es grande y el radio es grande, el quiebre se desplaza hacia abajo a la derecha
x_esquina, y_esquina = 1.8, 2.2
r_dinamico = 0.3 + 2.5 * factor_radio

# Ubicación matemática del final del radio (donde se corta el flujo en tu imagen)
if radio_mm == 0:
    vortex_centro_x = x_esquina
    vortex_centro_y = y_esquina - (2.2 * factor_angulo)
else:
    # Coordenadas exactas del final del arco cóncavo
    angulo_rad = np.radians(angulo_deg)
    vortex_centro_x = x_esquina + r_dinamico + r_dinamico * np.cos(np.pi + angulo_rad - np.pi/2)
    vortex_centro_y = y_esquina + r_dinamico + r_dinamico * np.sin(np.pi + angulo_rad - np.pi/2)

# Centros dinámicos de los 2 vórtices acoplados a ese nuevo punto crítico
vortex1_x = vortex_centro_x - 0.3
vortex1_y = vortex_centro_y - 0.4
vortex2_x = vortex_centro_x + 0.2
vortex2_y = vortex_centro_y - 0.7

r1_sq = (X - vortex1_x)**2 + (Y - vortex1_y)**2
r2_sq = (X - vortex2_x)**2 + (Y - vortex2_y)**2

# NUEVA REGLA FÍSICA: Si hay quiebre angular extremo (ej. 180°), el radio NO elimina el vórtice,
# solo lo traslada de lugar (vórtice de estela o de escalón).
# La intensidad disminuye con el radio SOLO si el ángulo acompaña de forma suave (cercano a 90°)
es_angulo_critico = 1.0 if angulo_deg > 135 else (1.0 - factor_radio)
intensidad_vortex = 4.5 * (1.0 + 2.5 * factor_angulo) * es_angulo_critico * (v_periferica / 98.02)

if intensidad_vortex < 0: 
    intensidad_vortex = 0

core = 0.25 + (0.4 * factor_angulo)

U_vortex1 = -intensidad_vortex * (Y - vortex1_y) / (r1_sq + core)
V_vortex1 =  intensidad_vortex * (X - vortex1_x) / (r1_sq + core)

U_vortex2 =  (intensidad_vortex * 0.8) * (Y - vortex2_y) / (r2_sq + core)
V_vortex2 = -(intensidad_vortex * 0.8) * (X - vortex2_x) / (r2_sq + core)

# Desplazar la máscara de la zona turbulenta hacia el final del radio
ancho_turbulento = (1.2 + (2.2 * factor_angulo)) * (1.0 - 0.5 * factor_radio if angulo_deg <= 135 else 1.0)
zona_turbulenta = np.exp(-((X - vortex_centro_x)**2 + (Y - vortex_centro_y)**2) / max(ancho_turbulento, 0.1))

# Campo de velocidades final acoplado
U_final = U_base + (U_vortex1 + U_vortex2) * zona_turbulenta
V_final = V_base + (V_vortex1 + V_vortex2) * zona_turbulenta

# Condición de frontera estricta: Bloqueo neumático detrás de la pared vertical de caída
for i in range(nx):
    for j in range(ny):
        if X[i,j] > vortex_centro_x and Y[i,j] < vortex_centro_y:
            U_final[i,j] *= 0.1
            V_final[i,j] *= 0.3

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
    density=1.8, 
    arrowsize=0.9
)

# --- DIBUJO DINÁMICO DE LA GEOMETRÍA COMBINADA ---
angulo_rad = np.radians(angulo_deg)
x0, y0 = 1.8, 5.0

if radio_mm == 0:
    y_salida_recta = y_esquina - (2.2 * factor_angulo)
    ax.plot([x0, x_esquina, 5.0], [y0, y_esquina, y_salida_recta], color='#ff3333', linewidth=5)
    ax.plot(x_esquina, y_esquina, 'ro', markersize=10)
else:
    theta = np.linspace(np.pi, np.pi + angulo_rad - np.pi/2, 50)
    x_centro = x_esquina + r_dinamico
    y_centro = y_esquina + r_dinamico
    
    x_curva = x_centro + r_dinamico * np.cos(theta)
    y_curva = y_centro + r_dinamico * np.sin(theta)
    
    # Línea de caída vertical o salida hacia el borde exterior del rodete (el escalón)
    y_salida_curva = y_esquina - (2.2 * factor_angulo)
    x_pared = np.concatenate(([x0], x_curva, [v_periferica*0.02 + vortex_centro_x, 5.0]))
    y_pared = np.concatenate(([y0], y_curva, [0.1, 0.1]))
    
    # Dibujar la chapa en color de advertencia si hay un escalón peligroso
    color_perfil = '#ff0055' if angulo_deg > 135 else ('#00ffcc' if radio_mm >= 150 else '#ffaa00')
    ax.plot(x_pared[:len(x_curva)+1], y_pared[:len(y_curva)+1], color=color_perfil, linewidth=5)
    # Línea vertical del escalón de caída
    ax.plot([vortex_centro_x, vortex_centro_x], [vortex_centro_y, 0.2], color='#ff3333', linewidth=4, linestyle='--')

# Anotaciones de diagnóstico dinámicas en el lienzo
if intensidad_vortex > 0.8:
    if angulo_deg > 135 and radio_mm > 0:
        ax.text(0.4, 0.4, "⚠️ VÓRTICE DE DESPRENDIMIENTO EN ESCALÓN (PUNTA DEL RADIO)", color='#ff0055', weight='bold', fontsize=9)
    else:
        ax.text(0.4, 0.4, "⚠️ VÓRTICES DE RECIRCULACIÓN PRESENTES EN LA ESQUINA", color='#ffaa00', weight='bold', fontsize=9)
else:
    ax.text(0.4, 0.4, "✅ FLUJO ENCAPSULADO / AERODINÁMICO", color='#00ffcc', weight='bold', fontsize=9)

ax.set_xlim(0.2, 4.8)
ax.set_ylim(0.2, 4.8)
ax.axis('off')
fig.colorbar(strm.lines, ax=ax, label='Velocidad del Fluido (m/s)', pad=0.02)

col_izq, col_centro, col_der = st.columns([1, 4, 1])
with col_centro:
    st.pyplot(fig)

# ==============================================================================
# DIAGNÓSTICO TÉCNICO COMPUESTO
# ==============================================================================
st.markdown("---")
st.header("📋 Evaluación de Ingeniería en Tiempo Real")

if angulo_deg > 135 and radio_mm >= 150:
    st.error(f"""
    **Condición Crítica: Vórtice por Efecto Escalón ({angulo_deg}° + {radio_mm} mm)**  
    ¡Excelente análisis! Al combinar una inclinación extrema de {angulo_deg}° con un radio amplio, la geometría genera un 'escalón de caída' abrupto al finalizar la curva. 
    *   **Física del Error Corregido:** El aire sigue la curva, pero al llegar a la punta vertical, la velocidad experimenta un desprendimiento de capa límite masivo por la caída muerta.
    *   **Impacto Real:** Se genera un gran vórtice de estela justo debajo del final del radio. Esto demuestra que un radio grande **no sirve de nada si al final de la trayectoria obligas al aire a realizar un quiebre recto de caída**. Toda la ganancia aerodinámica de la curva se destruye en el escalón.
    """)
elif angulo_deg == 90 and radio_mm == 0:
    st.error("""
    **Condición Crítica Localizada:** Estado de ángulo recto a 90° sin radio. Los remolinos están confinados en la esquina.
    """)
elif radio_mm >= 150 and angulo_deg == 90:
    st.success("""
    **Condición Optimizada de Diseño:** Transición recta estándar a 90° suavizada internamente de forma completa por el radio. El flujo descarga horizontalmente de manera limpia hacia los álabes sin escalones de desprendimiento.
    """)
else:
    st.warning("""
    **Condición Intermedia Combinada:** El radio mitiga parcialmente el remolino en el vértice, pero vigilar los puntos de desprendimiento en las salidas.
    """)
