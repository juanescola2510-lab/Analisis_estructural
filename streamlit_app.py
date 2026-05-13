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
v_ms = st.sidebar.slider("Velocidad de Cadena (m/s)", 0.5, 2.0, 1.2)
altura = st.sidebar.number_input("Altura entre centros (m)", value=33.5)

st.sidebar.header("⚖️ Pesos del Sistema (lb)")
p_cad_lb = st.sidebar.number_input("Peso Total de la Cadena (lb)", value=2400)
p_cang_lb = st.sidebar.number_input("Peso Total de los Cangilones (lb)", value=11820)

st.sidebar.header("⚙️ Geometría y Material")
d_pin = st.sidebar.slider("Diámetro del Pin (mm)", 20.0, 60.0, 34.74)
su_mpa = st.sidebar.number_input("Resistencia Última Su (MPa)", value=980)
sy_mpa = st.sidebar.number_input("Límite Elástico Sy (MPa)", value=835)

st.sidebar.header("🔍 Concentradores de Esfuerzo")
condicion_superficie = st.sidebar.selectbox(
    "Estado Superficial del Pin", 
    ["Nuevo (Pulido)", "Rayado por Clinker (Pitting)", "Grieta Inicial Detectada"]
)
mapeo_kt = {"Nuevo (Pulido)": 1.0, "Rayado por Clinker (Pitting)": 1.7, "Grieta Inicial Detectada": 2.5}
kt = mapeo_kt[condicion_superficie]

st.sidebar.header("⚠️ Condición de la Bota")
nivel_acum = st.sidebar.select_slider("Nivel de Atascamiento", 
    options=["Limpio", "Moderado", "Crítico", "Total"], value="Limpio")

st.sidebar.header("⏱️ Parámetros Operativos del Tiempo")
rpm_sprocket = st.sidebar.number_input("Velocidad del Sprocket (RPM)", value=45.0, min_value=1.0)

# --- LÓGICA DE CÁLCULO ---
flujo_kgs = (tph * 1000) / 3600
p_mat_lb = ((flujo_kgs / v_ms) * altura) * 2.20462
f_exc_map = {"Limpio": 0.1, "Moderado": 0.5, "Crítico": 1.5, "Total": 3.0}
f_exc_lb = p_mat_lb * f_exc_map[nivel_acum]

t_total_lb = p_cad_lb + p_cang_lb + p_mat_lb + f_exc_lb
f_n = t_total_lb * 4.44822
reaccion_n = f_n / 2

# Esfuerzos (Área Simple)
area_pin = (np.pi * (d_pin/2)**2)
tau_nominal = f_n / area_pin 
# Esfuerzo Pico (Aplicando Kt)
tau_m = tau_nominal * kt
tau_a = tau_m * 0.25 

# Propiedades de Corte (Von Mises)
ssu, ssy = su_mpa * 0.577, sy_mpa * 0.577

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
    ax1.text(0.82, 0.45, f"T_Total: {t_total_lb:,.0f} lb", color='red', fontweight='bold', fontsize=12)
    ax1.text(0.82, 0.15, f"• Mat: {p_mat_lb:,.0f} lb\n• Bota: {f_exc_lb:,.0f} lb\n• Cang: {p_cang_lb:,.0f} lb\n• Cad: {p_cad_lb:,.0f} lb", color='gray', fontsize=9)
    ax1.axis('off')
    st.pyplot(fig1)

with col2:
    st.write("### DCL: Pin con Reacciones y Concentrador")
    fig2, ax2 = plt.subplots(figsize=(8, 8))
    ax2.add_patch(plt.Rectangle((0.1, 0.45), 0.8, 0.1, color='#BDBDBD', ec='black', zorder=4))
    ax2.add_patch(plt.Rectangle((0.1, 0.3), 0.12, 0.4, color='#757575', alpha=0.9)) # Placa Izq
    ax2.add_patch(plt.Rectangle((0.78, 0.3), 0.12, 0.4, color='#757575', alpha=0.9)) # Placa Der
    ax2.add_patch(plt.Rectangle((0.32, 0.35), 0.36, 0.3, color='#9E9E9E', hatch='//')) # Carga central
    ax2.annotate('', xy=(0.16, 0.9), xytext=(0.16, 0.7), arrowprops=dict(facecolor='blue', width=3))
    ax2.annotate('', xy=(0.84, 0.9), xytext=(0.84, 0.7), arrowprops=dict(facecolor='blue', width=3))
    ax2.text(0.16, 0.93, f"R/2: {reaccion_n:,.0f} N", color='blue', ha='center', fontsize=9)
    ax2.text(0.84, 0.93, f"R/2: {reaccion_n:,.0f} N", color='blue', ha='center', fontsize=9)
    ax2.annotate('', xy=(0.5, 0.1), xytext=(0.5, 0.45), arrowprops=dict(facecolor='red', width=5))
    ax2.text(0.52, 0.15, f"Carga Total: {f_n:,.0f} N", color='red', fontweight='bold')
    # Marca del concentrador
    if kt > 1:
        ax2.scatter(0.27, 0.5, color='yellow', s=100, edgecolors='black', zorder=10, label='Fisura/Raya')
        ax2.text(0.27, 0.4, f"Kt={kt}", color='black', fontsize=8, ha='center', fontweight='bold')
    ax2.axis('off')
    st.pyplot(fig2)

# --- BLOQUE 2: COMPARATIVA DE FATIGA Y VIDA ÚTIL ---
st.markdown("---")
st.write(f"### Análisis de Fatiga y Estimación de Vida Útil (Factor $K_t$ = {kt})")
col_graf, col_tab = st.columns(2)

# Corrección analítica rigurosa del límite de fatiga a cortante (Shigley)
sse_corregido = su_mpa * 0.5 * 0.577  # ~0.288 * Su

# --- CÁLCULO DE VIDA ÚTIL Y CICLOS (TEORÍA S-N) ---
if tau_m < ssu:
    tau_eq = tau_a / (1 - (tau_m / ssu))
else:
    tau_eq = tau_a + tau_m

sf_103 = 0.9 * ssu  # Resistencia estimada a 10^3 ciclos
f_limite = sse_corregido

if tau_eq <= f_limite:
    ciclos_estimados = float('inf')
    vida_horas = float('inf')
    txt_horas = "Sin límite teórico bajo estas cargas"
elif tau_eq >= sf_103:
    ciclos_estimados = 1000.0
    vida_horas = ciclos_estimados / (rpm_sprocket * 60)
    txt_horas = f"{vida_horas:.2f} horas de operación continua"
else:
    b_param = (1/3) * np.log10(f_limite / sf_103)
    a_param = (sf_103**2) / f_limite
    
    ciclos_estimados = (tau_eq / a_param)**(1 / b_param)
    vida_horas = ciclos_estimados / (rpm_sprocket * 60)
    txt_horas = f"{vida_horas:,.1f} horas operativas ({vida_horas/24:,.1f} días aprox.)"

# --- RENDERIZADO DEL GRÁFICO ---
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

# --- RENDERIZADO DE MÉTRICAS Y TABLAS ---
with col_tab:
    fs_sod = 1 / ((tau_a / sse_corregido) + (tau_m / ssy)) if ((tau_a / sse_corregido) + (tau_m / ssy)) > 0 else float('inf')
    fs_goo = 1 / ((tau_a / sse_corregido) + (tau_m / ssu)) if ((tau_a / sse_corregido) + (tau_m / ssu)) > 0 else float('inf')
    fs_ger = 1 / ((tau_a / sse_corregido) + (tau_m / ssu)**2) if ((tau_a / sse_corregido) + (tau_m / ssu)**2) > 0 else float('inf')
    
    st.write("**Métricas de Esfuerzo en el Pin:**")
    st.info(f"🔹 **τ Nominal:** {tau_nominal:.2f} MPa")
    st.error(f"🔺 **τ Local (Pico en Muesca):** {tau_m:.2f} MPa")
    
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
    
    st.write("**⌛ Estimación de Durabilidad Continua Basada en Carga Constante:**")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.metric(label="Ciclos hasta el inicio de falla", value=f"{ciclos_estimados:,.0f}" if ciclos_estimados != float('inf') else "Infinitos")
    with col_c2:
        st.metric(label="Tiempo estimado de servicio", value=f"{vida_horas:,.1f} h" if vida_horas != float('inf') else "Infinito")

# --- BLOQUE DE INTEGRACIÓN REGLA DE MINER (IMPACTOS TRANSITORIOS) ---
st.markdown("---")
st.write("### 🔨 Análisis de Daño Acumulado por Impactos Transitorios (Regla de Miner)")

col_miner1, col_miner2 = st.columns(2)

with col_miner1:
    frecuencia_impacto = st.slider("Frecuencia del Impacto Transitorio (Cada 'X' minutos)", 1, 60, 5)

with col_miner2:
    horas_operacion_diaria = st.number_input("Horas de operación por día", value=24.0, max_value=24.0, min_value=0.1)

if ciclos_estimados != float('inf') and ciclos_estimados > 1000:
    # Se calcula la cantidad de impactos basándose en la frecuencia configurada
    impactos_por_hora = 60 / frecuencia_impacto
    impactos_por_dia = impactos_por_hora * horas_operacion_diaria
    
    # Aplicación lineal de la regla de Palmgren-Miner: 
    # El giro continuo seguro a esfuerzo nominal aporta daño despreciable frente al impacto.
    dias_vida_util_miner = ciclos_estimados / impactos_por_dia
    años_vida_util = dias_vida_util_miner / 365
    
    st.markdown("#### 📊 Durabilidad Estimada bajo Miner")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric(label="Impactos Transitorios / Día", value=f"{impactos_por_dia:,.0f}")
    with col_m2:
        st.metric(label="Vida Útil Real (Días)", value=f"{dias_vida_util_miner:,.1f} días")
    with col_m3:
        st.metric(label="Vida Útil Real (Años)", value=f"{años_vida_util:,.2f} años")
        
    st.warning(f"⚠️ **Nota operativa:** Aunque las cargas rotacionales básicas son seguras, la aparición del impacto transitorio limita severamente el ciclo de reemplazo del pin a **{dias_vida_util_miner:,.1f} días**.")
else:
    st.success("✨ **Condición Óptima:** El esfuerzo equivalente calculado se encuentra por debajo del límite de fatiga modificado o el pin posee dimensiones suficientes. El material operará en la zona de **Vida Infinita** sin daño acumulativo por impactos.")
