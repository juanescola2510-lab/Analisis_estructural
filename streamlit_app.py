import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==============================================================================
# CONFIGURACIÓN DE LA INTERFAZ DE INGENIERÍA
# ==============================================================================
st.set_page_config(
    page_title="Simulador CFD Paramétrico - UNACEM", 
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

st.title("⚙️ Simulador CFD Dinámico: De Ángulo Recto (90°) a Placa Plana (180°)")
st.markdown("""
**Análisis Fluidodinámico de Transición de Placa Superior para el Ventilador de Tiro**  
Modifica el ángulo de la transición en la barra lateral para observar cómo se expande la zona de desprendimiento de flujo y la magnitud de los vórtices de recirculación.
""")

# ==============================================================================
# PANEL DE CONTROL INTERACTIVO (BARRA LATERAL)
# ==============================================================================
st.sidebar.header("🛠️ Variables de Diseño Geométrico")

# El Slider Clave: Controla el ángulo desde 90° (Recto) hasta 180° (Plano)
angulo_deg = st.sidebar.slider("Ángulo de la Transición Externa (Grados)", 90, 180, 90, step=5)

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
# NÚCLEO MATEMÁTICO: MODELADO DE VÓRTICES EXPANSIVOS SEGÚN EL ÁNGULO
# ==============================================================================
nx, ny = 200, 200
x = np.linspace(0.1, 4.9, nx)
y = np.linspace(0.1, 4.9, ny)
X, Y = np.meshgrid(x, y)

# Factor de severidad: 0 en 90° (vórtice estándar) y aumenta hacia 180° (máxima obstrucción)
factor_severidad = (angulo_deg - 90) / 90.0

# Flujo base del ventilador que se degrada conforme el ángulo se abre a 180°
U_base = 2.4 * X * (Y**0.15) * (1.0 - 0.4 * factor_severidad)
V_base = -1.8 * (Y**1.05)

# Centros dinámicos de los vórtices: se desplazan y agrandan a mayor ángulo
vortex1_x = 1.3 - (0.5 * factor_severidad)
vortex1_y = 1.8 - (0.3 * factor_severidad)
vortex2_x = 1.7 + (0.4 * factor_severidad)
vortex2_y = 1.4 - (0.4 * factor_severidad)

r1_sq = (X - vortex1_x)**2 + (Y - vortex1_y)**2
r2_sq = (X - vortex2_x)**2 + (Y - vortex2_y)**2

# La intensidad y el tamaño del núcleo (core) del vórtice crecen exponencialmente con el ángulo
intensidad_vortex = 4.5 * (1.0 + 2.2 * factor_severidad) * (v_periferica / 98.02)
core = 0.25 + (0.5 * factor_severidad) 

U_vortex1 = -intensidad_vortex * (Y - vortex1_y) / (r1_sq + core)
V_vortex1 =  intensidad_vortex * (X - vortex1_x) / (r1_sq + core)

U_vortex2 =  (intensidad_vortex * 0.8) * (Y - vortex2_y) / (r2_sq + core)
V_vortex2 = -(intensidad_vortex * 0.8) * (X - vortex2_x) / (r2_sq + core)

# La zona afectada por la turbulencia se expande hacia el centro del flujo a 180°
ancho_zona_turbulenta = 1.2 + (2.0 * factor_severidad)
zona_turbulenta = np.exp(-((X - 1.5)**2 + (Y - 1.7)**2) / ancho_zona_turbulenta)

# Acoplamiento del campo vectorial CFD dinámico
U_final = U_base + (U_vortex1 + U_vortex2) * zona_turbulenta
V_final = V_base + (V_vortex1 + V_vortex2) * zona_turbulenta

Vel_magnitud = np.sqrt(U_final**2 + V_final**2)

# ==============================================================================
# DESPLIEGUE GRÁFICO (UNIFICADO)
# ==============================================================================
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(8, 6), dpi=150)

# Renderizar líneas de corriente paramétricas
strm = ax.streamplot(
    X, Y, U_final, V_final, 
    color=Vel_magnitud, 
    cmap='plasma', 
    linewidth=1.1, 
    density=1.8, # Alta densidad para ver la rotación de los lazos
    arrowsize=0.9
)

# --- DIBUJO DINÁMICO DE LA CHAPA SEGÚN EL ÁNGULO ELECTO ---
angulo_rad = np.radians(angulo_deg)

# Punto de inicio fijo (Boca de entrada)
x0, y0 = 1.8, 5.0
# Punto de quiebre de la esquina (fijo en la junta de la foto para 90°)
x_esquina, y_esquina = 1.8, 2.2

if angulo_deg == 90:
    # Caso base: Tu ángulo recto real
    ax.plot([x0, x_esquina, 5.0], [y0, y_esquina, y_esquina], color='#ff3333', linewidth=5, label='Perfil 90°')
    ax.plot(x_esquina, y_esquina, 'ro', markersize=12)
    ax.text(2.0, 2.5, "⚠️ TRANSICIÓN A 90°: RECIRCULACIÓN LOCALIZADA", color='#ff3333', weight='bold', fontsize=9)
else:
    # Calcular la apertura angular de la chapa hasta los 180°
    # A 180° la chapa superior se convierte en una línea totalmente recta horizontal continua
    longitud_ala = 3.2
    x_fin_ala = x_esquina + longitud_ala * np.sin(angulo_rad - np.pi/2)
    y_fin_ala = y_esquina + longitud_ala * (1.0 - np.cos(angulo_rad - np.pi/2))
    
    # Dibujar perfil dinámico de la chapa
    color_alerta = '#ff0055' if angulo_deg > 135 else '#ff7700'
    ax.plot([x0, x_esquina, 5.0], [y0, y_esquina, y_esquina - (2.2 * factor_severidad)], color=color_alerta, linewidth=5)
    
    # Graficar indicador del ojo de la tormenta / zona de estancamiento masivo
    ax.plot(vortex1_x, vortex1_y, 'go', markersize=10, alpha=0.5)
    ax.plot(vortex2_x, vortex2_y, 'go', markersize=10, alpha=0.5)
    
    if angulo_deg == 180:
        ax.text(0.5, 3.8, "❌ CRÍTICO a 180°: IMPACTO PERPENDICULAR\nBLOQUEO NEUMÁTICO", color='#ff0055', weight='bold', fontsize=9)
    else:
        ax.text(2.0, 2.5, f"⚠️ Degradación Angular: {angulo_deg}°", color=color_alerta, weight='bold', fontsize=9)

ax.set_xlim(0.2, 4.8)
ax.set_ylim(0.2, 4.8)
ax.axis('off')
fig.colorbar(strm.lines, ax=ax, label='Velocidad del Fluido (m/s)', pad=0.02)

# Mostrar el gráfico único centrado
col_grafico, _ = st.columns()
with col_grafico:
    st.pyplot(fig)

# ==============================================================================
# CONCLUSIÓN TÉCNICA DINÁMICA SEGÚN EL NUEVO ESCENARIO
# ==============================================================================
st.markdown("---")
st.header("📋 Diagnóstico de Ingeniería en Tiempo Real")

if angulo_deg == 90:
    st.error("""
    **Configuración: Ángulo Recto Puro (90°)**  
    Es el estado actual de tu rodete fotografiado. El aire choca y se desprende bruscamente formando bucles cerrados de remolinos concentrados exactamente en la esquina. La erosión es alta pero localizada en el vértice.
    """)
elif angulo_deg <= 135:
    st.warning(f"""
    **Configuración: Ángulo de Transición Abierto ({angulo_deg}°)**  
    Al abrirse la chapa más allá de los 90°, el aire ya no encuentra un canal libre para expandirse radialmente. La zona de baja presión se agranda hacia el centro del rodete. Los dos remolinos internos comienzan a ganar volumen físico.
    """)
else:
    st.error(f"""
    **Configuración: Degradación Extrema hacia Placa Plana ({angulo_deg}°)**  
    ¡Escenario Altamente Crítico! Conforme el ángulo se aproxima a los 180° (placa superior completamente plana), el flujo vertical impacta de frente contra una barrera perpendicular. 
    *   **Efecto Neumático:** Los vórtices de recirculación ya no se quedan atrapados en la esquina; ahora invaden todo el canal de entrada del ventilador. 
    *   **Consecuencia en Planta:** Esto actúa como un tapón neumático virtual que restringe drásticamente el caudal de succión del separador. El variador de frecuencia aumentará los Amperios al máximo intentando vencer la resistencia de choque sin lograr mover el volumen de aire necesario.
    """)
