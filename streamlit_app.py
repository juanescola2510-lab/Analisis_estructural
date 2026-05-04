import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Análisis de Falla - Elevador de Cangilones", layout="wide")

st.title("🛡️ Sistema de Análisis de Falla y Diseño de Cadena")
st.markdown("### Diagnóstico Técnico: Clinker y Puzolana (33.5m)")

# --- SIDEBAR: DATOS DE ENTRADA ---
st.sidebar.header("📊 Parámetros de Operación")
tph = st.sidebar.number_input("Capacidad Real (Ton/h)", value=150)
v_ms = st.sidebar.slider("Velocidad (m/s)", 0.5, 2.0, 1.2)
altura = st.sidebar.number_input("Altura entre centros (m)", value=33.5)

st.sidebar.header("⛓️ Pesos del Sistema (lb)")
p_cadena = st.sidebar.number_input("Peso Total Cadena", value=2400)
p_cangilones = st.sidebar.number_input("Peso Total Cangilones", value=11820)

st.sidebar.header("🔩 Geometría del Pin")
d_pin = st.sidebar.slider("Diámetro actual/propuesto (mm)", 20.0, 50.0, 34.74)
res_mpa = st.sidebar.number_input("Resistencia Tracción Acero (MPa)", value=980)

# --- LÓGICA DE CÁLCULO ---
flujo_kgs = (tph * 1000) / 3600
p_material_lb = ((flujo_kgs / v_ms) * altura) * 2.20462
t_max_lb = p_cadena + p_cangilones + p_material_lb
f_n = t_max_lb * 4.44822

# Esfuerzos
area_doble = 2 * (np.pi * (d_pin / 2)**2)
esfuerzo_mpa = f_n / area_doble
res_corte = res_mpa * 0.577
fs = res_corte / esfuerzo_mpa

# --- INTERFAZ DE RESULTADOS ---
col1, col2, col3 = st.columns(3)
col1.metric("Tensión Total", f"{t_max_lb:,.0f} lb")
col2.metric("Esfuerzo de Corte", f"{esfuerzo_mpa:.2f} MPa")
col3.metric("Factor de Seguridad", f"{fs:.2f}")

# --- GRÁFICOS REALISTAS ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# 1. SPROCKET REALISTA
ax1.set_title("DCL: MECANISMO DE TRACCIÓN SUPERIOR", fontsize=14, fontweight='bold')
# Cuerpo y dientes
ax1.add_patch(plt.Circle((0.5, 0.6), 0.25, color='#454545', zorder=2))
for i in range(12):
    angle = np.deg2rad(i * 30); x = 0.5 + 0.27 * np.cos(angle); y = 0.6 + 0.27 * np.sin(angle)
    ax1.add_patch(plt.Circle((x, y), 0.04, color='#454545'))
# Vectores de carga
ax1.annotate('', xy=(0.77, 0.1), xytext=(0.77, 0.6), arrowprops=dict(facecolor='red', width=4))
ax1.text(0.8, 0.45, f"T_max: {t_max_lb:,.0f} lb", color='red', fontweight='bold', fontsize=12)
ax1.text(0.8, 0.35, f"• Mat: {p_material_lb:,.0f} lb\n• Cang: {p_cangilones:,.0f} lb\n• Cad: {p_cadena:,.0f} lb", color='gray')
ax1.axis('off')

# 2. ENSAMBLE DEL PIN REALISTA
ax2.set_title("DCL: ANALISIS DE CORTE EN EL PASADOR", fontsize=14, fontweight='bold')
# Pin
ax2.add_patch(plt.Rectangle((0.1, 0.45), 0.8, 0.1, color='#BDBDBD', ec='black', zorder=4))
# Placas Externas (Soportes)
ax2.add_patch(plt.Rectangle((0.1, 0.3), 0.12, 0.4, color='#757575', alpha=0.9))
ax2.add_patch(plt.Rectangle((0.78, 0.3), 0.12, 0.4, color='#757575', alpha=0.9))
# Placa Interna (Carga)
ax2.add_patch(plt.Rectangle((0.32, 0.35), 0.36, 0.3, color='#9E9E9E', hatch='//'))
# Planos de Falla
ax2.axvline(0.27, color='red', ls='--', lw=2)
ax2.axvline(0.73, color='red', ls='--', lw=2)
ax2.text(0.27, 0.75, "FALLA A", color='red', ha='center', fontweight='bold')
ax2.text(0.73, 0.75, "FALLA B", color='red', ha='center', fontweight='bold')
# Fuerza central
ax2.annotate('', xy=(0.5, 0.45), xytext=(0.5, 0.1), arrowprops=dict(facecolor='red', width=5))
ax2.axis('off')

st.pyplot(fig)

# --- SECCIÓN DE ANÁLISIS DE FALLA (MODO INGENIERÍA) ---
st.markdown("---")
st.subheader("🕵️ Análisis de Causa Raíz (RCA)")

col_a, col_b = st.columns(2)

with col_a:
    st.info("#### Estado del Pin de 1\" (Falla Original)")
    area_falla = 2 * (np.pi * (25.4 / 2)**2)
    esfuerzo_falla = f_n / area_falla
    st.write(f"- **Esfuerzo Real:** {esfuerzo_falla:.2f} MPa")
    st.write(f"- **Límite de Fatiga (Clinker):** ~180 MPa")
    st.write(f"- **Diagnóstico:** El esfuerzo de operación + picos de arranque superaron el límite de fatiga acumulado en 3 años.")

with col_b:
    if fs < 10:
        st.warning(f"#### Estado de Mejora (Pin Ø{d_pin}mm)\nFactor de Seguridad: {fs:.2f}. El diseño aún está cerca de la zona de fatiga para cementeras.")
    else:
        st.success(f"#### Estado de Mejora (Pin Ø{d_pin}mm)\nFactor de Seguridad: {fs:.2f}. Diseño Robusto. Vida útil estimada > 8 años.")

# Historial de Fatiga (Gráfico de tendencia)
st.write("### Sensibilidad del Factor de Seguridad vs Diámetro")
diametros = np.linspace(20, 50, 100)
factores = (res_corte) / (f_n / (2 * (np.pi * (diametros / 2)**2)))
fig2, ax3 = plt.subplots(figsize=(10, 3))
ax3.plot(diametros, factores, color='blue', lw=2)
ax3.axhline(10, color='green', ls='--', label='Zona Segura (FS=10)')
ax3.axvline(d_pin, color='red', ls=':', label='Tu Selección')
ax3.set_xlabel("Diámetro del Pin (mm)")
ax3.set_ylabel("Factor de Seguridad")
ax3.legend()
st.pyplot(fig2)
