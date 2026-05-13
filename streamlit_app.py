import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import time

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

peso_total_kg = p_cad_kg + p_cang_kg + p_mat_kg + f_exc_kg
f_n = peso_total_kg * 9.80665
reaccion_n = f_n / 2

# Esfuerzos (Área Simple)
area_pin = (np.pi * (d_pin/2)**2)
tau_nominal = f_n / area_pin 
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

# --- BLOQUE DE SIMULACIÓN REALISTA CON TRAYECTORIA CURVA EN SPROCKETS ---
st.markdown("---")
st.write("### 🔄 Simulación Dinámica Industrial del Movimiento de Cangilones")

col_sim1, col_sim2 = st.columns(2)

with col_sim1:
    st.markdown("**Control de Animación**")
    radio_sprocket_sim = 1.2
    perimetro_total_lazo = (2 * altura) + (2 * np.pi * radio_sprocket_sim)
    tiempo_vuelta_completa = perimetro_total_lazo / v_ms if v_ms > 0 else 0
    st.write(f"⏱️ **Tiempo de ciclo completo de un cangilón:** {tiempo_vuelta_completa:.2f} segundos")
    play_sim = st.button("▶️ Iniciar / Reiniciar Simulación")

with col_sim2:
    placeholder_grafico = st.empty()

if play_sim:
    num_cangilones_sim = 50
    posiciones_fase = np.linspace(0, perimetro_total_lazo, num_cangilones_sim, endpoint=False)
    
    for t_step in range(80):
        dt = 0.35
        desplazamiento = (v_ms * t_step * dt) % perimetro_total_lazo
        
        fig_sim, ax_sim = plt.subplots(figsize=(6, 9))
        
        ax_sim.add_patch(patches.Circle((0, altura), radio_sprocket_sim, color='#7f8c8d', fill=True, zorder=2))
        ax_sim.add_patch(patches.Circle((0, altura), 0.3, color='#2c3e50', fill=True, zorder=3)) 
        ax_sim.add_patch(patches.Circle((0, 0), radio_sprocket_sim, color='#7f8c8d', fill=True, zorder=2))
        ax_sim.add_patch(patches.Circle((0, 0), 0.3, color='#2c3e50', fill=True, zorder=3)) 
        
        ax_sim.plot([radio_sprocket_sim, radio_sprocket_sim], [0, altura], color='#34495e', lw=2.5, zorder=1)
        ax_sim.plot([-radio_sprocket_sim, -radio_sprocket_sim], [0, altura], color='#34495e', lw=2.5, zorder=1)
        
        for pos_base in posiciones_fase:
            pos_actual = (pos_base + desplazamiento) % perimetro_total_lazo
            
            if pos_actual <= altura:
                x_pos = radio_sprocket_sim
                y_pos = pos_actual
                angulo_rotacion = 0.0
                cargado = True
            elif pos_actual <= (altura + np.pi * radio_sprocket_sim):
                dist_arco = pos_actual - altura
                angulo_arco = dist_arco / radio_sprocket_sim  
                
                x_pos = radio_sprocket_sim * np.cos(angulo_arco)
                y_pos = altura + radio_sprocket_sim * np.sin(angulo_arco)
                angulo_rotacion = angulo_arco
                cargado = angulo_arco < (np.pi / 2) 
            elif pos_actual <= (2 * altura + np.pi * radio_sprocket_sim):
                x_pos = -radio_sprocket_sim
                y_pos = altura - (pos_actual - (altura + np.pi * radio_sprocket_sim))
                angulo_rotacion = np.pi
                cargado = False
            else:
                dist_arco = pos_actual - (2 * altura + np.pi * radio_sprocket_sim)
                angulo_arco = dist_arco / radio_sprocket_sim
                
                x_pos = -radio_sprocket_sim * np.cos(angulo_arco)
                y_pos = -radio_sprocket_sim * np.sin(angulo_arco)
                angulo_rotacion = np.pi + angulo_arco
                cargado = False

            cos_a, sin_a = np.cos(angulo_rotacion), np.sin(angulo_rotacion)
            
            puntos_locales = np.array([
                [0.0, -0.4],       
                [0.6, -0.4],       
                [0.8, 0.3],        
                [0.0, 0.3]         
            ])
            
            # CORRECCIÓN DE INDEXACIÓN MATEMÁTICA: Extracción explícita de componentes escalares pt[0] y pt[1]
            puntos_transformados = []
            for pt in puntos_locales:
                x_rot = pt[0] * cos_a - pt[1] * sin_a + x_pos
                y_rot = pt[0] * sin_a + pt[1] * cos_a + y_pos
                puntos_transformados.append([x_rot, y_rot])
                
            color_cang = '#27ae60' if cargado else '#2980b9'
            color_borde = '#1e8449' if cargado else '#1f618d'
            
            ax_sim.add_patch(patches.Polygon(puntos_transformados, closed=True, facecolor=color_cang, edgecolor=color_borde, lw=1.5, zorder=4))
            
            if cargado:
                puntos_mat_locales = np.array([[0.05, -0.35], [0.55, -0.35], [0.65, 0.1], [0.05, 0.1]])
                puntos_mat_trans = []
                for pt in puntos_mat_locales:
                    x_rot = pt[0] * cos_a - pt[1] * sin_a + x_pos
                    y_rot = pt[0] * sin_a + pt[1] * cos_a + y_pos
                    puntos_mat_trans.append([x_rot, y_rot])
                ax_sim.add_patch(patches.Polygon(puntos_mat_trans, closed=True, facecolor='#d35400', alpha=0.9, zorder=5))
        
        ax_sim.set_xlim(-4, 4)
        ax_sim.set_ylim(-radio_sprocket_sim - 2, altura + radio_sprocket_sim + 2)
        ax_sim.set_title(f"Cinemática Paramétrica Completa | Velocidad: {v_ms:.2f} m/s", fontsize=10, fontweight='bold')
        ax_sim.set_xlabel("Ancho de Carcasa (m)")
        ax_sim.set_ylabel("Altura de Elevación Vertical (m)")
        ax_sim.grid(True, alpha=0.12, ls=':')
        
        placeholder_grafico.pyplot(fig_sim)
        plt.close(fig_sim)
        time.sleep(0.04)
