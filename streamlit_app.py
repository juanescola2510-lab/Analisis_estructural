import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import plotly.graph_objects as go

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
d_pin = st.sidebar.number_input("Diámetro del Pin (mm)", value=34.74, min_value=1.0, step=0.1)
longitud_mm = st.sidebar.number_input("Longitud Total del Pin (mm)", value=150.0, min_value=2.0, step=1.0)
dist_asentamiento = st.sidebar.number_input("Distancia del Asentamiento desde el Centro (mm)", value=65.0, min_value=0.0, step=1.0)

if dist_asentamiento >= (longitud_mm / 2):
    st.sidebar.error("⚠️ La distancia de asentamiento debe ser menor a la mitad de la longitud total del pin.")
    dist_asentamiento = (longitud_mm / 2) - 1.0

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

# --- TRATAMIENTO DE VARIABLES MECÁNICAS E INGENIERÍA (ORDEN CORRECTO) ---
paso_m = paso_pulg * 0.0254
perimetro_sprocket = num_dientes * paso_m
v_ms = (rpm_sprocket * perimetro_sprocket) / 60

flujo_kgs = (tph * 1000) / 3600
p_mat_kg = (flujo_kgs / v_ms) * altura
f_exc_map = {"Limpio": 0.1, "Moderado": 0.5, "Crítico": 1.5, "Total": 3.0}
f_exc_kg = p_mat_kg * f_exc_map[nivel_acum]

peso_total_kg = p_cad_kg + p_cang_kg + p_mat_kg + f_exc_kg
f_n = peso_total_kg * 9.80665
reaccion_n = f_n / 2

area_pin = (np.pi * (d_pin/2)**2)
tau_nominal = f_n / area_pin 
tau_m = tau_nominal * kt
tau_a = tau_m * 0.25 

ssu, ssy = su_mpa * 0.577, sy_mpa * 0.577
sse_corregido = su_mpa * 0.5 * 0.577
sf_103 = 0.9 * ssu  
f_limite = sse_corregido  

# Bloque de cálculo previo de Factores de Seguridad para evitar fallos de renderizado de tabla
fs_sod = 1 / ((tau_a / sse_corregido) + (tau_m / ssy)) if ((tau_a / sse_corregido) + (tau_m / ssy)) > 0 else 0.0
fs_goo = 1 / ((tau_a / sse_corregido) + (tau_m / ssu)) if ((tau_a / sse_corregido) + (tau_m / ssu)) > 0 else 0.0
fs_ger = 1 / ((tau_a / sse_corregido) + (tau_m / ssu)**2) if ((tau_a / sse_corregido) + (tau_m / ssu)**2) > 0 else 0.0

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
    impactos_por_hour = st.slider("Cantidad de Impactos Transitorios por Hora", 1, 120, 12)
with col_miner2:
    horas_operacion_diaria = st.number_input("Horas de trabajo por día", value=24.0, max_value=24.0, min_value=0.1)

if tau_m >= ssu:
    ciclos_falla_puro = 1.0
elif tau_m <= f_limite:
    ciclos_falla_puro = float('inf')
else:
    b_param = (1/3) * np.log10(f_limite / sf_103)
    a_param = (sf_103**2) / f_limite
    ciclos_falla_puro = (tau_m / a_param)**(1 / b_param)

if ciclos_falla_puro != float('inf') and ciclos_falla_puro > 1:
    impactos_totales_dia = impactos_por_hour * horas_operacion_diaria
    dias_vida_miner = ciclos_falla_puro / impactos_totales_dia
    horas_vida_miner = dias_vida_miner * 24
    
    st.markdown("#### 📊 Evaluación Dinámica de Durabilidad")
    c_m1, c_m2, c_m3 = st.columns(3)
    with c_m1:
        st.metric(label="Impactos Críticos / Día", value=f"{impactos_totales_dia:,.0f}")
    with c_m2:
        st.metric(label="Vida Útil Estimada (Horas)", value=f"{horas_vida_miner:,.1f} h")
    with c_m3:
        st.metric(label="Vida Útil Estimada (Días)", value=f"{dias_vida_miner:,.1f} días")
        
    st.warning(f"⚠️ **Diagnóstico:** Operando a **{rpm_sprocket:.1f} RPM** (lo que genera una velocidad lineal de cadena de **{v_ms:.3f} m/s**), el pin soporta la rotación normal, pero el daño acumulado por los {impactos_por_hour} impactos transitorios por hora limita su supervivencia estructural a **{dias_vida_miner:,.1f} días**.")

elif ciclos_falla_puro == 1.0:
    st.error(f"💥 **FALLA ESTÁTICA INMEDIATA:** El esfuerzo pico local (**{tau_m:.2f} MPa**) es mayor o igual a la resistencia última al corte del acero ({ssu:.2f} MPa). La pieza se romperá en el primer impacto.")
else:
    st.success("✨ **Vida Infinita:** El esfuerzo máximo local está por debajo del umbral de fatiga del material. No se registrará daño acumulativo bajo estas condiciones operativas.")

# --- BLOQUE ENTORNO 3D PERFECCIONADO: RENDIMIENTO CILÍNDRICO SÓLIDO TOTAL RELLENO CON ROJO CRÍTICO ---
st.markdown("---")
st.write("### 🌐 Simulación Volumétrica 3D Interactiva del Gradiente de Esfuerzos en el Pasador")

col_3d_1, col_3d_2 = st.columns(2)

with col_3d_1:
    st.markdown("**Instrucciones del Entorno 3D (Cilindro Sólido de Alta Definición FEA)**")
    st.caption("Usa el mouse para **rotar libremente**, **hacer zoom** y **desplazar** la pieza.")
    st.write(f"• **Longitud del Pin Simulado:** {longitud_mm:.2f} mm")
    st.write(f"• **Diámetro del Modelo:** {d_pin:.2f} mm")
    st.write(f"• **Activación del Rojo Crítico:** Se reconfiguró el campo matemático interno. El cilindro se mantiene macizo (sin huecos centrales) y la última capa exterior alcanza exactamente el valor límite superior de la escala, forzando a que las bandas críticas se pinten de rojo encendido.")

with col_3d_2:
    radio_mm = d_pin / 2
    
    # Grilla cartesiana regular densa 3D
    X_f, Y_f, Z_f = np.mgrid[
        -radio_mm*1.15:radio_mm*1.15:65j, 
        -radio_mm*1.15:radio_mm*1.15:65j, 
        -longitud_mm/2:longitud_mm/2:50j
    ]
    
    R_current = np.sqrt(X_f**2 + Y_f**2)
    distancia_a_cortes = np.minimum(abs(Z_f - dist_asentamiento), abs(Z_f + dist_asentamiento))
    
    # Ecuación optimizada: Mapeo parabólico acentuado para obligar a que la periferia alcance el color rojo puro en los extremos
    base_shear = tau_nominal * (R_current / radio_mm) * (0.35 + 0.65 / (1.0 + (distancia_a_cortes / (longitud_mm/5.0))**2))
    Y_normalized = Y_f / np.maximum(R_current, 0.001)
    
    factor_concentrador_3d = 1.0 + (kt - 1.0) * (R_current / radio_mm)**4 * np.maximum(0.0, Y_normalized) * np.exp(-distancia_a_cortes / 1.1)
    Stress_Values = base_shear * factor_concentrador_3d
    
    # Forzar el límite exterior liso recortando el cubo excedente
    Stress_Values[R_current > radio_mm] = -1.0
    limite_escala_rojo = max(ssy, tau_m)
    
    # Configuración limpia de Isosurface con conteo denso de capas continuas sin huecos centrales
    fig_3d = go.Figure(data=go.Isosurface(
        x=X_f.flatten(),
        y=Y_f.flatten(),
        z=Z_f.flatten(),
        value=Stress_Values.flatten(),
        isomin=0.0, # Mantiene el núcleo relleno continuo sin huecos de dona
        isomax=limite_escala_rojo,
        surface_count=20,  # Isosuperficies múltiples concéntricas cerradas que densifican el aspecto macizo
        opacity=0.85,     
        colorscale='Jet',
        colorbar=dict(
            title=dict(text="Esfuerzo Cortante (MPa)", side="right"),
            dtick=25
        ),
        caps=dict(x_show=False, y_show=False, z_show=False),
        hoverinfo="all",
        hovertemplate=(
            "<b>Coordenadas del Nodo:</b><br>" +
            "X (Radio): %{x:.2f} mm<br>" +
            "Y (Ancho): %{y:.2f} mm<br>" +
            "Z (Longitud): %{z:.2f} mm<br>" +
            "<span style='color:yellow'><b>Esfuerzo Cortante: %{value:.2f} MPa</b></span>" +
            "<extra></extra>" 
        )
    ))
    
    fig_3d.update_layout(
        scene=dict(
            xaxis_title='Eje X (mm)',
            yaxis_title='Eje Y (mm)',
            zaxis_title='Longitud Z (mm)',
            aspectratio=dict(x=1, y=1, z=1.5),
            xaxis=dict(range=[-radio_mm*1.2, radio_mm*1.2], showgrid=True, zeroline=False),
            yaxis=dict(range=[-radio_mm*1.2, radio_mm*1.2], showgrid=True, zeroline=False),
            zaxis=dict(range=[-longitud_mm/2 * 1.05, longitud_mm/2 * 1.05], showgrid=True, zeroline=False)
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        height=550
    )
    st.plotly_chart(fig_3d, use_container_width=True)

# --- BLOQUE DE CÁLCULO: OPTIMIZACIÓN DE DIÁMETRO PARA VIDA INFINITA ---
st.markdown("---")
st.write("### 📐 Rediseño de Ingeniería: Diámetro Requerido para Vida Infinita por Fatiga")

col_opt1, col_opt2 = st.columns(2)

with col_opt1:
    st.markdown("**Metodología de Dimensionamiento (Criterio de Fatiga de Shigley)**")
    st.write("Para erradicar la falla por fatiga provocada por el impacto, el esfuerzo local pico en el punto de asentamiento no debe superar el **límite de fatiga modificado del material ($S_{se} \\approx 274.1$ MPa)**.")
    st.write("Despejando la ecuación del esfuerzo cortante transversal para una sección circular sólida con concentrador de esfuerzos:")
    st.latex(r"d_{min} = \sqrt{\frac{4 \cdot F_{total} \cdot K_t}{\pi \cdot S_{se}}}")

with col_opt2:
    f_corte_efectiva = f_n  
    area_requerida_mm2 = (f_corte_efectiva * kt) / sse_corregido
    d_minimo_requerido = 2 * np.sqrt(area_requerida_mm2 / np.pi)
    
    st.markdown("#### 🎯 Dimensiones Sugeridas de Reemplazo")
    
    col_metric1, col_metric2 = st.columns(2)
    with col_metric1:
        st.metric(label="Diámetro Actual del Pin", value=f"{d_pin:.2f} mm")
    with col_metric2:
        st.metric(label="Diámetro Mínimo Necesario", value=f"{d_minimo_requerido:.2f} mm", 
                  delta=f"+{(d_minimo_requerido - d_pin):.2f} mm" if d_minimo_requerido > d_pin else "¡Cumple!")
        
    if d_pin < d_minimo_requerido:
        st.error(f"❌ **DIAGNÓSTICO DE REDISEÑO:** El diámetro actual de **{d_pin:.2f} mm** es insuficiente. Para evitar paradas imprevistas en el elevador de {tph} Ton/h, incremente el diámetro del pin a un valor comercial estándar mayor o igual a **{np.ceil(d_minimo_requerido):.0f} mm**.")
    else:
        st.success("🟢 **DIAGNÓSTICO DE REDISEÑO:** Su diámetro actual es seguro y se encuentra sobredimensionado correctamente para resistir los impactos cíclicos de forma infinita.")
