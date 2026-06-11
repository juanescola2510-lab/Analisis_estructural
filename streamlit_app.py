import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==============================================================================
# CONFIGURACIÓN DE LA INTERFAZ DE INGENIERÍA
# ==============================================================================
st.set_page_config(
    page_title="Simulador CFD Dual - UNACEM", 
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

st.title("⚙️ Simulador CFD Co-axial: Análisis Dual del Ingreso")
st.markdown("""
**Evaluación Simultánea de Dinámica de Fluidos: Campos de Velocidad y Gradientes de Presión Estática**  
Modifica la geometría en la barra lateral para observar en paralelo cómo se disipan los microvórtices y cómo se homogenizan las presiones en la campana.
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
# NÚCLEO MATEMÁTICO: MODELADO CFD MULTIVÓRTICE Y BERNOULLI
# ==============================================================================
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

# Flujo base simétrico descendente
U_final = 2.8 * (X - x_centro) / (Y + 0.3)
V_final = -2.5 * (Y**0.95)

factor_rpm = 1040.0 / float(rpm)
core_dinamico = 0.15 * factor_rpm  
radio_dispersion = 0.6 * factor_rpm 

intensidad_vortex = 8.5 * (1.0 - factor_radio) * (float(rpm) / 1040.0)
if intensidad_vortex < 0: 
    intensidad_vortex = 0.0

eps = 1e-5

# LADO IZQUIERDO TRASLADABLE (Vórtices internos)
v_izq_centros = [
    (x_izq_entrada + 0.42, y_quiebre - 0.60, 1.0),      
    (x_izq_entrada + 0.22, y_quiebre - 0.95, 0.45),     
    (x_izq_entrada + 0.65, y_quiebre - 0.40, 0.35)      
]

for vx, vy, peso in v_izq_centros:
    r_sq = (X - vx)**2 + (Y - vy)**2
    U_v = (intensidad_vortex * peso) * (Y - vy) / (r_sq + core_dinamico + eps)
    V_v = -(intensidad_vortex * peso) * (X - vx) / (r_sq + core_dinamico + eps)
    
    zona_turb = np.exp(-(r_sq) / (radio_dispersion * peso))
    U_final = U_final * (1.0 - 0.95 * zona_turb * (1.0 - factor_radio)) + U_v * zona_turb
    V_final = V_final * (1.0 - 0.95 * zona_turb * (1.0 - factor_radio)) + V_v * zona_turb

# LADO DERECHO TRASLADABLE (Vórtices internos en espejo)
v_der_centros = [
    (x_der_entrada - 0.42, y_quiebre - 0.60, 1.0),      
    (x_der_entrada - 0.22, y_quiebre - 0.95, 0.45),     
    (x_der_entrada - 0.65, y_quiebre - 0.40, 0.35)      
]

for vx, vy, peso in v_der_centros:
    r_sq = (X - vx)**2 + (Y - vy)**2
    U_v = -(intensidad_vortex * peso) * (Y - vy) / (r_sq + core_dinamico + eps)
    V_v = (intensidad_vortex * peso) * (X - vx) / (r_sq + core_dinamico + eps)
    
    zona_turb = np.exp(-(r_sq) / (radio_dispersion * peso))
    U_final = U_final * (1.0 - 0.95 * zona_turb * (1.0 - factor_radio)) + U_v * zona_turb
    V_final = V_final * (1.0 - 0.95 * zona_turb * (1.0 - factor_radio)) + V_v * zona_turb

Vel_magnitud = np.sqrt(U_final**2 + V_final**2)

# Simulación matemática de presiones (Ecuación de Bernoulli deductiva)
Presion_Relativa = 4000.0 * (Y / 4.8) - 0.5 * densidad_gas * (Vel_magnitud**2)
for vx, vy, peso in v_izq_centros + v_der_centros:
    r_sq = (X - vx)**2 + (Y - vy)**2
    Presion_Relativa += 1500.0 * np.exp(-r_sq / 0.5) * (1.0 - factor_radio)

# ==============================================================================
# PROCESAMIENTO GEOMÉTRICO ADAPTATIVO DE LA CHAPA MORADA
# ==============================================================================
r_diseno = 0.15 + 1.1 * factor_radio
alfa = angulo_rad - np.pi/2

# Coordenadas lado izquierdo redondeado
theta_izq = np.linspace(0, -np.pi/2 * factor_angulo if angulo_deg > 90 else -np.pi/2, 40)
x_c_izq = (x_izq_entrada - r_diseno) + r_diseno * np.cos(theta_izq)
y_c_izq = (y_quiebre + r_diseno) + r_diseno * np.sin(theta_izq) - (r_diseno * factor_angulo)
if angulo_deg == 180: y_c_izq = np.ones_like(x_c_izq) * y_quiebre
x_pared_izq = np.hstack(([x_izq_entrada, x_izq_entrada], x_c_izq, [x_fin_izq]))
y_pared_izq = np.hstack(([5.0, y_quiebre], y_c_izq, [y_fin]))

# Coordenadas lado derecho redondeado
theta_der = np.linspace(np.pi, np.pi + np.pi/2 * factor_angulo if angulo_deg > 90 else np.pi + np.pi/2, 40)
x_centro_der = x_der_entrada + r_diseno
y_centro_der = y_quiebre + r_diseno
x_c_der = x_centro_der + r_diseno * np.cos(theta_der)
y_c_der = y_centro_der + r_diseno * np.sin(theta_der) - (r_diseno * factor_angulo)
if angulo_deg == 180: y_c_der = np.ones_like(x_c_der) * y_quiebre
x_pared_der = np.hstack(([x_der_entrada, x_der_entrada], x_c_der, [x_fin_der]))
y_pared_der = np.hstack(([5.0, y_quiebre], y_c_der, [y_fin]))

# ==============================================================================
# DESPLIEGUE EN DOS COLUMNAS PARALELAS UNIFICADAS DE STREAMLIT
# ==============================================================================
plt.style.use('dark_background')

# Declaración explícita de las dos columnas de visualización en el lienzo principal
col_grafico_izq, col_grafico_der = st.columns(2)

with col_grafico_izq:
    st.subheader("📊 1. Líneas de Flujo (Campos de Velocidad)")
    fig_vel, ax_vel = plt.subplots(figsize=(7, 5.2), dpi=110)
    
    strm_vel = ax_vel.streamplot(X, Y, U_final, V_final, color=Vel_magnitud, cmap='turbo', linewidth=1.1, density=1.8, arrowsize=0.8)
    
    if radio_mm == 0:
        ax_vel.plot([x_izq_entrada, x_izq_entrada, x_fin_izq], [5.0, y_quiebre, y_fin], color='#df00ff', linewidth=4)
        ax_vel.plot([x_der_entrada, x_der_entrada, x_fin_der], [5.0, y_quiebre, y_fin], color='#df00ff', linewidth=4)
    else:
        ax_vel.plot(x_pared_izq, y_pared_izq, color='#df00ff', linewidth=4)
        ax_vel.plot(x_pared_der, y_pared_der, color='#df00ff', linewidth=4)
        
    ax_vel.text(4.6, 4.6, f"Reynolds (Re): {reynolds:.2e}", color='#ffffff', fontsize=8, weight='bold', ha='right', va='top', bbox=dict(facecolor='#1e293b', alpha=0.7, edgecolor='#3b82f6', boxstyle='round,pad=0.4'))
    
    if intensidad_vortex > 0.6:
        estado_flujo_izq = "🔴 FLUX: TURBULENTO (CASCADA)"
        color_caja_izq = '#ff3333'
    else:
        estado_flujo_izq = "🟢 FLUX: LAMINAR / GUIADO"
        color_caja_izq = '#00ffcc'
        
    ax_vel.text(0.4, 0.4, estado_flujo_izq, color=color_caja_izq, fontsize=8, weight='bold', ha='left', va='bottom', bbox=dict(facecolor='#0e1117', alpha=0.8, edgecolor=color_caja_izq, boxstyle='round,pad=0.5'))
    ax_vel.text(2.5, 4.6, f"↔️ Diámetro Real: {d_entrada} mm", color='#ff3344', fontsize=8, weight='bold', ha='center', va='top', bbox=dict(facecolor='#0e1117', alpha=0.8, edgecolor='#ff3344', boxstyle='round,pad=0.4'))
    
    ax_vel.set_xlim(0.1, 4.9)
    ax_vel.set_ylim(0.2, 4.8)
    ax_vel.axis('off')
    fig_vel.colorbar(strm_vel.lines, ax=ax_vel, label='Velocidad del Fluido (m/s)', pad=0.02, orientation='horizontal')
    st.pyplot(fig_vel)

with col_grafico_der:
    st.subheader("🌡️ 2. Gradientes de Presión Estática Relativa")
    fig_pres, ax_pres = plt.subplots(figsize=(7, 5.2), dpi=110)
    
    cont_pres = ax_pres.contourf(X, Y, Presion_Relativa, levels=35, cmap='coolwarm')
    
    if radio_mm == 0:
        ax_pres.plot([x_izq_entrada, x_izq_entrada, x_fin_izq], [5.0, y_quiebre, y_fin], color='#df00ff', linewidth=4)
        ax_pres.plot([x_der_entrada, x_der_entrada, x_fin_der], [5.0, y_quiebre, y_fin], color='#df00ff', linewidth=4)
    else:
        ax_pres.plot(x_pared_izq, y_pared_izq, color='#df00ff', linewidth=4)
        ax_pres.plot(x_pared_der, y_pared_der, color='#df00ff', linewidth=4)
        
    ax_pres.text(4.6, 4.6, f"Reynolds (Re): {reynolds:.2e}", color='#ffffff', fontsize=8, weight='bold', ha='right', va='top', bbox=dict(facecolor='#1e293b', alpha=0.7, edgecolor='#3b82f6', boxstyle='round,pad=0.4'))
    
    if intensidad_vortex > 0.6:
        estado_flujo_der = "🔴 FLUX: TURBULENTO (CASCADA)"
        color_caja_der = '#ff3333'
    else:
        estado_flujo_der = "🟢 FLUX: LAMINAR / GUIADO"
        color_caja_der = '#00ffcc'
        
    ax_pres.text(0.4, 0.4, estado_flujo_der, color=color_caja_der, fontsize=8, weight='bold', ha='left', va='bottom', bbox=dict(facecolor='#0e1117', alpha=0.8, edgecolor=color_caja_der, boxstyle='round,pad=0.5'))
    ax_pres.text(2.5, 4.6, f"↔️ Diámetro Real: {d_entrada} mm", color='#ff3344', fontsize=8, weight='bold', ha='center', va='top', bbox=dict(facecolor='#0e1117', alpha=0.8, edgecolor='#ff3344', boxstyle='round,pad=0.4'))
    
    ax_pres.set_xlim(0.1, 4.9)
    ax_pres.set_ylim(0.2, 4.8)
    ax_pres.axis('off')
    fig_pres.colorbar(cont_pres, ax=ax_pres, label='Presión Estática Relativa (Pa)', pad=0.02, orientation='horizontal')
    st.pyplot(fig_pres)

# ==============================================================================
# DIAGNÓSTICO TÉCNICO INFERIOR 
# ==============================================================================
st.markdown("---")
st.header("📋 Evaluación de Ingeniería en Tiempo Real")
st.write(f"**Configuración Frontal**: Ángulo de {angulo_deg}° con un Radio de {radio_mm} mm, Boca de {d_entrada} mm a {rpm} RPM.")

if intensidad_vortex > 0.6:
    st.warning("El estrechamiento del flujo central incrementa la velocidad de succión. Al chocar contra las esquinas ortogonales, se induce una severa recirculación bifásica simétrica con formación de microvórtices secundarios.")
else:
    st.success("La campana simétrica se expande hacia los extremos de manera divergente, encauzando y distribuyendo el aire en paralelo a las paredes cóncavas moradas.")
