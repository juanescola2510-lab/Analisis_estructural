import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# CONFIGURACIÓN DE LA INTERFAZ DE INGENIERÍA
st.set_page_config(
    page_title="Simulador CFD Dual con Encapsulador - UNACEM", 
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

st.title("⚙️ Simulador CFD: Efecto de Encapsulador Concéntrico")
st.markdown("""
**Evaluación Dinámica del Flujo Atrapado en el Canal de Succión Externo**  
Modifica la holgura del encapsulador en la barra lateral para observar el incremento de velocidad en el canal anular y el cambio en los vórtices de ingreso.
""")

# ==============================================================================
# PANEL DE CONTROL INTERACTIVO (BARRA LATERAL)
# ==============================================================================
st.sidebar.header("🛠️ Variables del Ventilador")
angulo_deg = st.sidebar.slider("Ángulo de la Transición Externa (Grados)", 90, 180, 125, step=5)
radio_mm = st.sidebar.slider("Radio de Suavizado de la Campana (mm)", 0, 250, 0, step=25)

# --- NUEVOS CONTROLES DEL ENCAPSULADOR (TRAZOS ROJOS) ---
st.sidebar.markdown("---")
st.sidebar.header("📦 Geometría del Encapsulador")
usar_encapsulador = st.sidebar.checkbox("Activar Encapsulador Externo", value=True)
holgura_mm = st.sidebar.slider("Distancia de Holgura / Canal (mm)", 50, 400, 150, step=25)
alto_ext_mm = st.sidebar.slider("Extensión Vertical del Encapsulador (mm)", 500, 2500, 1800, step=100)

st.sidebar.markdown("---")
st.sidebar.header("📋 Parámetros de Operación")
rpm = st.sidebar.slider("Velocidad de Rotación (RPM)", 500, 1200, 1040, step=10)
d_entrada = st.sidebar.slider("Diámetro Boca Aspiración / Cuello (mm)", 400, 1400, 950, step=50)
diametro = st.sidebar.number_input("Diámetro Exterior Placa (mm)", value=1800)
densidad_gas = st.sidebar.number_input("Densidad del Gas (kg/m³)", value=0.95, step=0.05)

# Cálculos mecánicos rápidos
radio_ext = diametro / 2000 
omega = (2 * np.pi * rpm) / 60
v_periferica = omega * radio_ext

st.sidebar.markdown("---")
st.sidebar.header("📈 Telemetría de Canal")
# Efecto Venturi simplificado para la barra lateral
v_estimada_canal = (rpm / 1040.0) * (200.0 / float(holgura_mm)) * 8.5
st.sidebar.metric(label="Velocidad Est. en Canal Anular", value=f"{v_estimada_canal:.2f} m/s")

# MESHGRID MATEMÁTICO
nx, ny = 160, 150  
x = np.linspace(0.1, 4.9, nx)
y = np.linspace(0.1, 4.9, ny)
X, Y = np.meshgrid(x, y)

factor_angulo = (angulo_deg - 90) / 90.0
factor_radio = radio_mm / 250.0

x_centro = 2.5
ancho_boca_visual = 3.4 * (d_entrada / diametro)

x_izq_entrada = x_centro - ancho_boca_visual / 2  
x_der_entrada = x_centro + ancho_boca_visual / 2  
y_quiebre = 2.8 - (1.3 * factor_angulo)  

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

# --- GENERACIÓN DEL FLUJO BASE ---
U_final = 2.8 * (X - x_centro) / (Y + 0.3)
V_final = -2.5 * (Y**0.95)

# --- ACOPLAMIENTO MATEMÁTICO DEL ENCAPSULADOR (CANAL ROJO) ---
# Escalar la holgura introducida por el usuario a coordenadas del mapa
delta_x_holgura = 1.2 * (holgura_mm / 400.0)
alto_visual_enc = 1.0 + 3.5 * (alto_ext_mm / 2500.0)

# Coordenadas de las paredes rojas del encapsulador
x_enc_izq = x_izq_entrada - delta_x_holgura
x_enc_der = x_der_entrada + delta_x_holgura

if usar_encapsulador:
    # 1. Definir la zona del canal (entre el cuello del ventilador y el encapsulador)
    dentro_canal_izq = (X >= x_enc_izq) & (X <= x_izq_entrada) & (Y >= y_quiebre)
    dentro_canal_der = (X >= x_der_entrada) & (X <= x_enc_der) & (Y >= y_quiebre)
    
    # Factor de aceleración por angostamiento (Efecto Venturi real)
    factor_venturi = 1.0 + (300.0 / float(holgura_mm))
    
    # Forzar al fluido a SUBIR por los canales laterales (V_final positivo)
    V_final = np.where(dentro_canal_izq | dentro_canal_der, 3.5 * factor_venturi * (Y/4.0), V_final)
    U_final = np.where(dentro_canal_izq, 1.2 * (x_izq_entrada - X), U_final)
    U_final = np.where(dentro_canal_der, -1.2 * (X - x_der_entrada), U_final)
    
    # 2. Bloqueo de flujo externo (El aire exterior es succionado desde abajo de las placas)
    zona_bloqueada_externa = (Y > y_quiebre + 0.3) & ((X < x_enc_izq) | (X > x_enc_der))
    U_final[zona_bloqueada_externa] *= 0.15
    V_final[zona_bloqueada_externa] *= -0.2  # Succión descendente lenta por fuera

# MODELADO DE VÓRTICES INTERNOS (Se atenúan o desplazan por el cambio de flujo)
factor_rpm = 1040.0 / float(rpm)
core_dinamico = 0.15 * factor_rpm  
radio_dispersion = 0.6 * factor_rpm 
intensidad_vortex = 8.5 * (1.0 - factor_radio) * (float(rpm) / 1040.0)
if intensidad_vortex < 0: intensidad_vortex = 0.0
eps = 1e-5

v_izq_centros = [(x_izq_entrada + 0.42, y_quiebre - 0.60, 1.0), (x_izq_entrada + 0.22, y_quiebre - 0.95, 0.45)]
for vx, vy, peso in v_izq_centros:
    r_sq = (X - vx)**2 + (Y - vy)**2
    U_v = (intensidad_vortex * peso) * (Y - vy) / (r_sq + core_dinamico + eps)
    V_v = -(intensidad_vortex * peso) * (X - vx) / (r_sq + core_dinamico + eps)
    zona_turb = np.exp(-(r_sq) / (radio_dispersion * peso))
    U_final = U_final * (1.0 - 0.95 * zona_turb) + U_v * zona_turb
    V_final = V_final * (1.0 - 0.95 * zona_turb) + V_v * zona_turb

v_der_centros = [(x_der_entrada - 0.42, y_quiebre - 0.60, 1.0), (x_der_entrada - 0.22, y_quiebre - 0.95, 0.45)]
for vx, vy, peso in v_der_centros:
    r_sq = (X - vx)**2 + (Y - vy)**2
    U_v = -(intensidad_vortex * peso) * (Y - vy) / (r_sq + core_dinamico + eps)
    V_v = (intensidad_vortex * peso) * (X - vx) / (r_sq + core_dinamico + eps)
    zona_turb = np.exp(-(r_sq) / (radio_dispersion * peso))
    U_final = U_final * (1.0 - 0.95 * zona_turb) + U_v * zona_turb
    V_final = V_final * (1.0 - 0.95 * zona_turb) + V_v * zona_turb

# Magnitud total del campo de velocidades resultante
Vel_magnitud = np.sqrt(U_final**2 + V_final**2)

# --- MODELADO DE PRESIÓN RELATIVA CON CAÍDA EN EL CANAL ---
Presion_Relativa = -3500.0 * (Y / 4.8) - 0.5 * densidad_gas * (Vel_magnitud**2)
if usar_encapsulador:
    # Alta succión (caída de presión severa) dentro del canal estrecho debido a la aceleración
    Presion_Relativa = np.where(dentro_canal_izq | dentro_canal_der, Presion_Relativa - (1500.0 * (200.0/float(holgura_mm))), Presion_Relativa)

Presion_Relativa = np.clip(Presion_Relativa, -4200, 2000)

# GEOMETRÍA DE LA CAMPANA (CHAPA MORADA)
r_diseno = 0.15 + 1.1 * factor_radio
theta_izq = np.linspace(0, -np.pi/2 * factor_angulo if angulo_deg > 90 else -np.pi/2, 40)
x_c_izq = (x_izq_entrada - r_diseno) + r_diseno * np.cos(theta_izq)
y_c_izq = (y_quiebre + r_diseno) + r_diseno * np.sin(theta_izq) - (r_diseno * factor_angulo)
x_pared_izq = np.hstack(([x_izq_entrada, x_izq_entrada], x_c_izq, [x_fin_izq]))
y_pared_izq = np.hstack(([5.0, y_quiebre], y_c_izq, [y_fin]))

theta_der = np.linspace(np.pi, np.pi + np.pi/2 * factor_angulo if angulo_deg > 90 else np.pi + np.pi/2, 40)
x_c_der = (x_der_entrada + r_diseno) + r_diseno * np.cos(theta_der)
y_c_der = (y_quiebre + r_diseno) + r_diseno * np.sin(theta_der) - (r_diseno * factor_angulo)
x_pared_der = np.hstack(([x_der_entrada, x_der_entrada], x_c_der, [x_fin_der]))
y_pared_der = np.hstack(([5.0, y_quiebre], y_c_der, [y_fin]))


# RENDEREADO GRÁFICO EN MATPLOTLIB (DOS COLUMNAS)
plt.style.use('dark_background')
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 1. Dinámica de Fluidos (Vectores e Ingreso)")
    fig_vel, ax_vel = plt.subplots(figsize=(7, 5.2), dpi=110)
    
    # Dibujar las líneas de flujo dinámicas
    strm_vel = ax_vel.streamplot(X, Y, U_final, V_final, color=Vel_magnitud, cmap='turbo', linewidth=1.1, density=1.9, arrowsize=0.8)
    
    # Dibujar Estructura Fija del Ventilador (Líneas moradas)
    ax_vel.plot(x_pared_izq, y_pared_izq, color='#df00ff', linewidth=4, label="Campana Ventilador")
    ax_vel.plot(x_pared_der, y_pared_der, color='#df00ff', linewidth=4)
    
    # --- DIBUJAR ENCAPSULADOR (LÍNEAS ROJAS SOLICITADAS) ---
    if usar_encapsulador:
        # Placa izquierda roja
        ax_vel.plot([x_enc_izq, x_enc_izq], [y_quiebre + 0.3, 5.0], color='#ff1744', linewidth=4.5)
        # Placa derecha roja
        ax_vel.plot([x_enc_der, x_enc_der], [y_quiebre + 0.3, 5.0], color='#ff1744', linewidth=4.5)
        
        # Anotación del canal de flujo atrapado
        ax_vel.text(x_enc_izq - 0.15, 4.0, "Flujo\nAscendente", color='#ff1744', fontsize=8, ha='right', weight='bold')
        ax_vel.text(x_enc_der + 0.15, 4.0, "Flujo\nAscendente", color='#ff1744', fontsize=8, ha='left', weight='bold')

    ax_vel.set_xlim(0, 5)
    ax_vel.set_ylim(0, 5)
    ax_vel.axis('off')
    st.pyplot(fig_vel)

with col2:
    st.subheader("📊 2. Distribución de Presión Estática Relativa")
    fig_pres, ax_pres = plt.subplots(figsize=(7, 5.2), dpi=110)
    
    cont_pres = ax_pres.contourf(X, Y, Presion_Relativa, levels=45, cmap='coolwarm')
    
    # Estructura del ventilador morada
    ax_pres.plot(x_pared_izq, y_pared_izq, color='#df00ff', linewidth=4)
    ax_pres.plot(x_pared_der, y_pared_der, color='#df00ff', linewidth=4)
    
    # Encapsulador en el mapa de presiones (Líneas blancas para contraste)
    if usar_encapsulador:
        ax_pres.plot([x_enc_izq, x_enc_izq], [y_quiebre + 0.3, 5.0], color='#ffffff', linewidth=3.5, linestyle='-')
        ax_pres.plot([x_enc_der, x_enc_der], [y_quiebre + 0.3, 5.0], color='#ffffff', linewidth=3.5, linestyle='-')

    ax_pres.set_xlim(0, 5)
    ax_pres.set_ylim(0, 5)
    ax_pres.axis('off')
    st.pyplot(fig_pres)

st.info("💡 **Conclusión de Ingeniería:** Al reducir la 'Distancia de Holgura', el aire se ve obligado a acelerarse drásticamente en el canal entre las chapas, aumentando la energía cinética y provocando una caída pronunciada en la presión estática local (zona azul en el canal).")
