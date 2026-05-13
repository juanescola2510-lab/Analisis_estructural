import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Análisis de Falla y Concentración de Esfuerzos", layout="wide")
st.title("🛡️ Diagnóstico de Ingeniería: Análisis de Falla con Concentradores de Esfuerzo")

# --- SIDEBAR: DATOS DE ENTRADA ---
st.sidebar.header("📊 Operación y Cargas")
tph = st.sidebar.number_input("Capacidad Real (Ton/h)", value=150)
altura = st.sidebar.number_input("Altura entre centros (m)", value=33.5)

st.sidebar.header("⚙️ Geometría del Sprocket y Cadena")
paso_pulg = st.sidebar.number_input("Paso de la Cadena (pulgadas)", value=6.0, min_value=0.1)
num_dientes = st.sidebar.number_input("Número de Dientes del Sprocket", value=12, min_value=1)

# SE MODIFICA: Los pesos ahora se ingresan y rotulan directamente en Kilogramos (kg)
st.sidebar.header("⚖️ Pesos del Sistema (kg)")
p_cad_kg = st.sidebar.number_input("Peso Total de la Cadena (kg)", value=1089)
p_cang_kg = st.sidebar.number_input("Peso Total de los Cangilones (kg)", value=5361)

st.sidebar.header("⚙️ Geometría y Material del Pin")
d_pin = st.sidebar.slider("Diámetro del Pin (mm)", 20.0, 60.0, 34.74)
su_mpa = st.sidebar.number_input("Resistencia Última Su (MPa)", value=920)
sy_mpa = st.sidebar.number_input("Límite Elástico Sy (MPa)", value=840)

st.sidebar.header("🔍 Concentradores de Esfuerzo")
condicion_superficie = st.sidebar.selectbox(
    "Estado Superficial del Pin", 
    ["Nuevo (Pulido)", "Rayado por Clinker (Pitting)", "Grieta Inicial Detectada"]
)
mapeo_kt = {"Nuevo (Pulido)": 1.0, "Rayado por Clinker (Pitting)": 1.7, "Grieta Inicial Detectada": 2.5}
kt = mapeo_kt.get(condicion_superficie, 2.5)

st.sidebar.header("⚠️ Condición de la Bota")
nivel_acum = st.sidebar.select_slider("Nivel de Atascamiento", 
    options=["Limpio", "Moderado", "Crítico", "Total"], value="Total")

st.sidebar.header("⏱️ Parámetros Operativos del Tiempo")
rpm_sprocket = st.sidebar.number_input("Velocidad del Sprocket (RPM)", value=41.0, min_value=1.0)

# --- LÓGICA DE CÁLCULO CINEMÁTICO (AUTOMÁTICO) ---
paso_m = paso_pulg * 0.0254
perimetro_sprocket = num_dientes * paso_m
v_ms = (rpm_sprocket * perimetro_sprocket) / 60

# --- LÓGICA DE CÁLCULO DE ESFUERZOS (EN BASE A KG) ---
flujo_kgs = (tph * 1000) / 3600
p_mat_kg = (flujo_kgs / v_ms) * altura
f_exc_map = {"Limpio": 0.1, "Moderado": 0.5, "Crítico": 1.5, "Total": 3.0}
f_exc_kg = p_mat_kg * f_exc_map[nivel_acum]

# Sumatoria de masa en kilogramos y conversión directa a Newtons (gravedad = 9.80665 m/s²)
peso_total_kg = p_cad_kg + p_cang_kg + p_mat_kg + f_exc_kg
f_n = peso_total_kg * 9.80665
reaccion_n = f_n / 2

# Para mantener la compatibilidad gráfica del DCL, se guarda la equivalencia informativa en lb
t_total_lb = peso_total_kg * 2.20462
p_mat_lb = p_mat_kg * 2.20462
f_exc_lb = f_exc_kg * 2.20462
p_cang_lb = p_cang_kg * 2.20462
p_cad_lb = p_cad_kg * 2.20462

# Esfuerzos (Área Simple)
area_pin = (np.pi * (d_pin/2)**2)
tau_nominal = f_n / area_pin 
# Esfuerzo Pico Máximo (Aplicando Kt)
tau_m = tau_nominal * kt
tau_a = tau_m * 0.25 

# Propiedades de Corte (Von Mises)
ssu, ssy = su_mpa * 0.577, sy_mpa * 0.577

# --- BLOQUE DE MUESTRA DE VELOCIDAD CALCULADA ---
st.info(f"⚡ **Parámetros Cinemáticos Calculados:** Velocidad de la Cadena = **{v_ms:.3f} m/s** | Perímetro del Sprocket = **{perimetro_sprocket:.3f} m**")

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
    ax1.text(0.82, 0.45, f"T_Total: {peso_total_kg:,.0f} kg", color='red', fontweight='bold', fontsize=12)
    ax1.text(0.82, 0.15, f"• Mat: {p_mat_kg:,.0f} kg\n• Bota: {f_exc_kg:,.0f} kg\n• Cang: {p_cang_kg:,.0f} kg\n• Cad: {p_cad_kg:,.0f} kg", color='gray', fontsize=9)
    ax1.axis('off')
    st.pyplot(fig1)

with col2:
    st.write("### DCL: Pin con Reacciones y Concentrador")
    fig2, ax2 = plt.subplots(figsize=(8, 8))
    ax2.add_patch(plt.Rectangle((0.1, 0.45), 0.8, 0.1, color='#BDBDBD', ec='black', zorder=4))
    ax2.add_patch(plt.Rectangle((0.1, 0.3), 0.12, 0.4, color='#757575', alpha=0.9))
    ax2.add_patch(plt.Rectangle((0.78, 0.3), 0.12, 0.4, color='#757575', alpha=0.9))
    ax2.add_patch(plt.Rectangle((0.32, 0.35), 0.36, 0.3, color='#9E9E9E', hatch='//'))
    ax2.annotate('', xy=(0.16, 0.9), xytext=(0.16, 0.7), arrowprops=dict(facecolor='blue', width=3))
    ax2.annotate('', xy=(0.84, 0.9), xytext=(0.84, 0.7), arrowprops=dict(facecolor='blue', width=3))
    ax2.text(0.16, 0.93, f"R/2: {reaccion_n:,.0f} N", color='blue', ha='center', fontsize=9)
    ax2.text(0.84, 0.93, f"R/2: {reaccion_n:,.0f} N", color='blue', ha='center', fontsize=9)
    ax2.annotate('', xy=(0.5, 0.1), xytext=(0.5, 0.45), arrowprops=dict(facecolor='red', width=5))
    ax2.text(0.52, 0.15, f"Carga Total: {f_n:,.0f} N", color='red', fontweight='bold')
    if kt > 1:
        ax2.scatter(0.27, 0.5, color='yellow', s=100, edgecolors='black', zorder=10, label='Fisura/Raya')
        ax2.text(0.27, 0.4, f"Kt={kt}", color='black', fontsize=8, ha='center', fontweight='bold')
    ax2.axis('off')
    st.pyplot(fig2)

# --- BLOQUE 2: COMPARATIVA DE FATIGA Y DIAGRAMAS ---
st.markdown("---")
st.write(f"### Análisis de Fatiga Estática y Límites Tolerables (Factor $K_t$ = {kt})")
col_graf, col_tab = st.columns(2)

sse_corregido = su_mpa * 0.5 * 0.577

with col_graf:
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    tm_range = np.linspace(0, ssu, 100)
    ax3.plot([0, ssy], [sse_corregido, 0], 'green', label='SODERBERG', lw=2)
    ax3.plot([0, ssu], [sse_corregido, 0], 'blue', ls='--', label='GOODMAN', lw=2)
    ax3.plot(tm_range, sse_corregido*(1-(tm_range/ssu)**2), 'orange', label='GERBER', lw=2)
    ax3.scatter(tau_nominal, tau_nominal * 0.25, color='gray', s=120, alpha=0.6, label='Punto Nominal (Ideal)')
    ax3.scatter(tau_m, tau_a, color='red', s=200, edgecolor='black', zorder=10, label='Punto Crítico Local (Con Kt)')
    ax3.set_xlabel("τ_medio (MPa)")
    ax3.set_ylabel("τ_alternante (MPa)")
    ax3.set_xlim(0, ssu * 1.05)
    ax3.set_ylim(0, sse_corregido * 1.2)
    ax3.legend(loc='upper right')
    ax3.grid(True, alpha=0.3)
    st.pyplot(fig3)

with col_tab:
    fs_sod = 1 / ((tau_a / sse_corregido) + (tau_m / ssy)) if ((tau_a / sse_corregido) + (tau_m / ssy)) > 0 else 0.0
    fs_goo = 1 / ((tau_a / sse_corregido) + (tau_m / ssu)) if ((tau_a / sse_corregido) + (tau_m / ssu)) > 0 else 0.0
    fs_ger = 1 / ((tau_a / sse_corregido) + (tau_m / ssu)**2) if ((tau_a / sse_corregido) + (tau_m / ssu)**2) > 0 else 0.0
    
    st.write("**Métricas de Esfuerzo en el Pin:**")
    st.info(f"🔹 **τ Nominal:** {tau_nominal:.2f} MPa")
    st.error(f"🔺 **τ Local Máximo (Pico en Muesca):** {tau_m:.2f} MPa")
    
    fs_min = 1.2
    data_tabla = {
        "Criterio": ["Soderberg", "Goodman", "Gerber"],
        "Factor de Seguridad": [f"{fs_sod:.2f}", f"{fs_goo:.2f}", f"{fs_ger:.2f}"],
        "Condición Estructural": [
            "🟢 SEGURO" if fs_sod >= fs_min else "🔴 FALLA POR FATIGA",
            "🟢 SEGURO" if fs_goo >= fs_min else "🔴 FALLA POR FATIGA",
            "🟢 SEGURO" if fs_ger >= fs_min else "🔴 FALLA POR FATIGA"
        ]
    }
    st.table(data_tabla)

# --- REGLA DE MINER PURA BASADA EN ESFUERZO CORTANTE MÁXIMO ---
st.markdown("---")
st.write("### 🔨 Análisis Matemático de Vida Útil Operativa (Regla de Miner Puro)")

col_miner1, col_miner2 = st.columns(2)
with col_miner1:
    impactos_por_hora = st.slider("Cantidad de Impactos Transitorios por Hora", 1, 120, 12)
with col_miner2:
    horas_operacion_diaria = st.number_input("Horas de trabajo por día", value=24.0, max_value=24.0, min_value=0.1)

# Cálculo puro de la curva S-N para el Esfuerzo Máximo Local (tau_m)
sf_103 = 0.9 * ssu  
f_limite = sse_corregido  

if tau_m >= ssu:
    ciclos_falla_puro = 1.0
elif tau_m <= f_limite:
    ciclos_falla_puro = float('inf')
else:
    b_param = (1/3) * np.log10(f_limite / sf_103)
    a_param = (sf_103**2) / f_limite
    ciclos_falla_puro = (tau_m / a_param)**(1 / b_param)

# Renderizado del análisis de durabilidad real por impactos y RPM
if ciclos_falla_puro != float('inf') and ciclos_falla_puro > 1:
    impactos_por_dia = impactos_por_hora * horas_operacion_diaria
    dias_vida_miner = ciclos_falla_puro / impactos_por_dia
    horas_vida_miner = dias_vida_miner * 24
    
    st.markdown("#### 📊 Evaluación Dinámica de Durabilidad")
    c_m1, c_m2, c_m3 = st.columns(3)
    with c_m1:
        st.metric(label="Impactos Críticos / Día", value=f"{impactos_por_dia:,.0f}")
    with c_m2:
        st.metric(label="Vida Útil Estimada (Horas)", value=f"{horas_vida_miner:,.1f} h")
    with c_m3:
        st.metric(label="Vida Útil Estimada (Días)", value=f"{dias_vida_miner:,.1f} días")
        
    if tau_m > ssy:
        st.error(f"🚨 **ALERTA CRÍTICA:** El esfuerzo cortante máximo de **{tau_m:.2f} MPa** superó el límite elástico al corte ({ssy:.2f} MPa). Se producirá deformación plástica permanente en el primer impacto. Reemplace el pin o disminuya la bota.")
    else:
        st.warning(f"⚠️ **Diagnóstico:** Operando a **{rpm_sprocket:.1f} RPM** (lo que genera una velocidad lineal de cadena de **{v_ms:.3f} m/s**), el pin soporta la rotación normal, pero el daño acumulado por los {impactos_por_hora} impactos transitorios por hora limita su supervivencia estructural a **{dias_vida_miner:,.1f} días**.")

elif ciclos_falla_puro == 1.0:
    st.error(f"💥 **FALLA ESTÁTICA INMEDIATA:** El esfuerzo pico local (**{tau_m:.2f} MPa**) es mayor o igual a la resistencia última al corte del acero ({ssu:.2f} MPa). La pieza se romperá en el primer impacto.")
else:
    st.success("✨ **Vida Infinita:** El esfuerzo máximo local está por debajo del umbral de fatiga del material. No se registrará daño acumulativo bajo estas condiciones operativas.")
