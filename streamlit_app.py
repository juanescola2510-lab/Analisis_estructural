import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==============================================================================
# CONFIGURACIÓN DE LA INTERFAZ DE INGENIERÍA
# ==============================================================================
st.set_page_config(
    page_title="Simulador CFD Ventilador Completo - UNACEM", 
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

st.title("🌀 Simulador CFD 2D: Ventilador Centrífugo de Tiro Completo")
st.markdown("""
**Modelado Global del Campo de Flujo: Aspiración, Rodete y Carcasa (Voluta)**  
Analiza cómo el aire ingresa axialmente por el centro, es impulsado radialmente por los álabes y se expande en la voluta para ganar presión estática.
""")

# ==============================================================================
# PANEL DE CONTROL (BARRA LATERAL)
# ==============================================================================
st.sidebar.header("🛠️ Parámetros del Ventilador")
rpm = st.sidebar.slider("Velocidad del Rodete (RPM)", 500, 1200, 1040, step=10)
num_alabes = st.sidebar.slider("Número de Álabes (Aletas)", 6, 16, 11, step=1)
angulo_giro = st.sidebar.slider("Animar Giro del Rodete (Grados)", 0, 360, 0, step=10)

st.sidebar.markdown("---")
st.sidebar.header("📋 Dimensiones Físicas")
d_entrada = st.sidebar.slider("Diámetro Boca Aspiración (mm)", 500, 1200, 940, step=20)
d_externo = st.sidebar.slider("Diámetro Exterior Rodete (mm)", 1500, 2100, 1800, step=50)

# Cálculos dinámicos de telemetría
r_ext = d_externo / 2000
omega = (2 * np.pi * rpm) / 60
v_periferica = omega * r_ext

st.sidebar.markdown("---")
st.sidebar.subheader("📈 Telemetría en la Punta")
st.sidebar.metric(label="Velocidad Periférica Lineal", value=f"{v_periferica:.2f} m/s", delta=f"{v_periferica*3.6:.1f} km/h")

try:
    st.sidebar.image("https://unacem.com.pe", width=180)
except Exception:
    st.sidebar.subheader("🏢 UNACEM - Área Técnica")

# ==============================================================================
# NÚCLEO MATEMÁTICO: MODELADO DE FLUJO EN VOLUTA Y ESPIRAL
# ==============================================================================
# Crear malla cartesiana centrada en (0,0)
nx, ny = 160, 160
x = np.linspace(-2.5, 3.5, nx)
y = np.linspace(-2.5, 3.0, ny)
X, Y = np.meshgrid(x, y)

# Convertir a coordenadas polares locales para facilitar el modelo del giro
R = np.sqrt(X**2 + Y**2)
THETA = np.arctan2(Y, X)
THETA[THETA < 0] += 2 * np.pi  # Rango de 0 a 2pi

# Definición de Radios de control basados en los sliders (en metros)
r_in = d_entrada / 2000
r_out = r_ext

# --- CAMPO DE VELOCIDADES 2D DEL VENTILADOR ---
# Componente Radial (Vr): El aire se acelera desde el centro hacia afuera
Vr = np.zeros_like(R)
# Zona de aspiración interior
Vr[R <= r_in] = 1.5 * (R[R <= r_in] / r_in)
# Zona de álabes y voluta exterior (Efecto de expulsión centrífuga)
Vr[R > r_in] = 1.5 * (r_in / (R[R > r_in] + 1e-5)) + 0.8 * (R[R > r_in] - r_in)

# Componente Tangencial (Vt): Velocidad de rotación provocada por las RPM del rodete
Vt = np.zeros_like(R)
# El aire gira solidario al rodete dentro de la zona de álabes
Vt[R <= r_out] = omega * R[R <= r_out] * 0.4
# El aire libre conserva el momento angular en la voluta exterior
Vt[R > r_out] = (omega * r_out * 0.4) * (r_out / (R[R > r_out] + 1e-5))

# Convertir las velocidades polares (Vr, Vt) de vuelta a cartesianas (U, V)
U_final = Vr * np.cos(THETA) - Vt * np.sin(THETA)
V_final = Vr * np.sin(THETA) + Vt * np.cos(THETA)

# Forzar la salida de aire tangencial hacia la boquilla de descarga (abajo a la derecha)
zona_descarga = (X > 1.5) & (Y < -0.5)
U_final[zona_descarga] = 2.5 * v_periferica * 0.3
V_final[zona_descarga] = -0.5

Vel_magnitud = np.sqrt(U_final**2 + V_final**2)

# ==============================================================================
# DESPLIEGUE GRÁFICO 2D DEL VENTILADOR COMPLETO
# ==============================================================================
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(9, 6), dpi=110) # Formato compacto sin scroll

# 1. Renderizar las líneas de flujo en paleta TURBO
strm = ax.streamplot(
    X, Y, U_final, V_final, 
    color=Vel_magnitud, 
    cmap='turbo', 
    linewidth=0.9, 
    density=1.6, 
    arrowsize=0.8
)

# 2. DIBUJO DE LA VOLUTA EXTERIOR (Carcasa en Espiral Logarítmica - Color Morado)
# Ecuación real de expansión de carcasa centrífuga: R = R0 * e^(b*theta)
theta_voluta = np.linspace(0, 2 * np.pi, 200)
r0_voluta = r_out + 0.2
b_voluta = 0.08  # Factor de apertura de la caracola
r_voluta = r0_voluta * np.exp(b_voluta * theta_voluta)

x_voluta = r_voluta * np.cos(theta_voluta)
y_voluta = r_voluta * np.sin(theta_voluta)

# Ajustar tramo final para la boquilla recta de salida
x_voluta = np.append(x_voluta, [3.2, 3.2])
y_voluta = np.append(y_voluta, [-r_voluta[-1], -2.5])

ax.plot(x_voluta, y_voluta, color='#df00ff', linewidth=5, label='Carcasa (Voluta)')

# 3. DIBUJO DE LA BOCA DE ASPIRACIÓN CENTRAL (Línea discontinua morada)
theta_boca = np.linspace(0, 2 * np.pi, 100)
ax.plot(r_in * np.cos(theta_boca), r_in * np.sin(theta_boca), color='#df00ff', linewidth=2, linestyle='--', label='Boca de Succión')

# 4. DIBUJO DE LOS ÁLABES DEL RODETE EN ROTACIÓN
ang_rad_offset = np.radians(angulo_giro)
for i in range(num_alabes):
    # Ángulo base de cada álabe distribuido uniformemente
    alpha = 2 * np.pi * i / num_alabes + ang_rad_offset
    
    # Dibujar álabe inclinado hacia atrás (Backward Inclined como el tuyo)
    # Nace en el radio interno y se extiende al externo con una ligera curva o inclinación
    x_alabe = [r_in * np.cos(alpha), r_out * np.cos(alpha + 0.25)]
    y_alabe = [r_in * np.sin(alpha), r_out * np.sin(alpha + 0.25)]
    
    ax.plot(x_alabe, y_alabe, color='#00ffcc', linewidth=3, alpha=0.9)

# Anotaciones de texto internas estilizadas
ax.text(-2.3, 2.7, f"Reynolds (Re): {reynolds:.2e}", 
        color='#ffffff', fontsize=9, weight='bold',
        bbox=dict(facecolor='#1e293b', alpha=0.7, edgecolor='#3b82f6', boxstyle='round,pad=0.5'))

ax.text(-2.3, -2.3, "🟢 OPERACIÓN GLOBAL: EQUILIBRADA", 
        color='#00ffcc', fontsize=8.5, weight='bold',
        bbox=dict(facecolor='#0e1117', alpha=0.8, edgecolor='#00ffcc', boxstyle='round,pad=0.6'))

# Ajustes del lienzo
ax.set_xlim(-2.5, 3.5)
ax.set_ylim(-2.5, 3.0)
ax.axis('off')
fig.colorbar(strm.lines, ax=ax, label='Velocidad Relativa del Flujo (m/s)', pad=0.02)

# Despliegue en la pantalla principal de Streamlit
st.pyplot(fig)

# ==============================================================================
# EXPLICACIÓN TÉCNICA
# ==============================================================================
st.markdown("---")
st.header("📋 Análisis de Funcionamiento del Conjunto")
st.write(f"""
Este modelo representa el comportamiento completo del ventilador trabajando a **{rpm} RPM**:
1. **Zona de Succión Central (Círculo segmentado):** El aire ingresa perpendicular a la pantalla, mostrando velocidades iniciales bajas (zonas azules/celestes).
2. **Zona de Álabes ({num_alabes} paletas curvas):** Al rotar el rodete, los álabes transfieren energía mecánica directamente al gas. El aire se acelera fuertemente y es expulsado hacia la periferia.
3. **Zona de Carcasa (Línea morada en espiral):** La forma de 'caracola' expande el área de paso del flujo de forma controlada. Esto disminuye la velocidad dinámica del aire saliente para transformarla en la **presión estática** requerida por los ductos de la planta.
""")
