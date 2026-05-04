import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Análisis Comparativo de Fatiga", layout="wide")

st.title("🏗️ Análisis de Falla Multicriterio: Soderberg, Goodman y Gerber")
st.sidebar.header("📊 Parámetros del Sistema")

# --- ENTRADAS ---
tph = st.sidebar.number_input("Capacidad Real (Ton/h)", value=150)
v_ms = st.sidebar.slider("Velocidad (m/s)", 0.5, 2.0, 1.2)
altura = st.sidebar.number_input("Altura (m)", value=33.5)
p_cadena = st.sidebar.number_input("Peso Cadena (lb)", value=2400)
p_cangilones = st.sidebar.number_input("Peso Total Cangilones (lb)", value=11820)
d_pin = st.sidebar.slider("Diámetro del Pin (mm)", 20.0, 55.0, 34.74)

# Propiedades del Acero 35CrMo
st.sidebar.subheader("🛠️ Propiedades del Material")
su_mpa = st.sidebar.number_input("Resistencia Última (Su) - MPa", value=980)
sy_mpa = st.sidebar.number_input("Límite Elástico (Sy) - MPa", value=835)

# --- CÁLCULOS TÉCNICOS ---
flujo_kgs = (tph * 1000) / 3600
p_material_lb = ((flujo_kgs / v_ms) * altura) * 2.20462
t_max_lb = p_cadena + p_cangilones + p_material_lb
f_n = t_max_lb * 4.44822

# Esfuerzos Cortantes (Doble Corte)
area_total = 2 * (np.pi * (d_pin / 2)**2)
tau_m = f_n / area_total            # Esfuerzo medio
tau_a = tau_m * 0.25                # Esfuerzo alternante (picos del 25%)

# Propiedades de Corte (Von Mises)
ssu = su_mpa * 0.577                # Última al corte
ssy = sy_mpa * 0.577                # Fluencia al corte
sse = ssu * 0.35                    # Límite fatiga corregido (ambiente clinker)

# --- CÁLCULO DE FACTORES DE SEGURIDAD ---
fs_soderberg = 1 / ((tau_a / sse) + (tau_m / ssy))
fs_goodman = 1 / ((tau_a / sse) + (tau_m / ssu))
# Gerber (Parabólico)
fs_gerber = 1 / ((tau_a / sse) + (tau_m / ssu)**2) # Simplificación para Gerber

# --- GRÁFICOS INICIALES (DCL SPROCKET Y ENSAMBLE PIN) ---
col_dcl1, col_dcl2 = st.columns(2)

with col_dcl1:
    st.write("### DCL: Mecanismo Superior")
    fig_dcl1, ax_dcl1 = plt.subplots(figsize=(6, 6))
    # Sprocket con dientes
    ax_dcl1.add_patch(plt.Circle((0.5, 0.6), 0.25, color='#454545', zorder=2))
    for i in range(12):
        angle = np.deg2rad(i * 30); x = 0.5 + 0.27 * np.cos(angle); y = 0.6 + 0.27 * np.sin(angle)
        ax_dcl1.add_patch(plt.Circle((x, y), 0.04, color='#454545'))
    ax_dcl1.annotate('', xy=(0.78, 0.1), xytext=(0.78, 0.6), arrowprops=dict(facecolor='red', width=4))
    ax_dcl1.text(0.8, 0.35, f"T_max: {t_max_lb:,.0f} lb", color='red', fontweight='bold')
    ax_dcl1.axis('off')
    st.pyplot(fig_dcl1)

with col_dcl2:
    st.write("### DCL: Ensamble del Pin")
    fig_dcl2, ax_dcl2 = plt.subplots(figsize=(6, 6))
    # Pin y Placas
    ax_dcl2.add_patch(plt.Rectangle((0.1, 0.45), 0.8, 0.1, color='#BDBDBD', ec='black', zorder=4))
    ax_dcl2.add_patch(plt.Rectangle((0.1, 0.3), 0.12, 0.4, color='#757575', alpha=0.9)) # Placa Ext
    ax_dcl2.add_patch(plt.Rectangle((0.78, 0.3), 0.12, 0.4, color='#757575', alpha=0.9)) # Placa Ext
    ax_dcl2.add_patch(plt.Rectangle((0.32, 0.35), 0.36, 0.3, color='#9E9E9E', hatch='//')) # Placa Int
    ax_dcl2.axvline(0.27, color='red', ls='--'); ax_dcl2.axvline(0.73, color='red', ls='--')
    ax_dcl2.axis('off')
    st.pyplot(fig_dcl2)

st.markdown("---")

# --- GRÁFICO COMPARATIVO DE FATIGA (Soderberg, Goodman, Gerber) ---
st.write("### Comparativa de Criterios de Falla: Soderberg vs Goodman vs Gerber")
fig_fat, ax_fat = plt.subplots(figsize=(10, 6))

# Rango de esfuerzos medios para las curvas
tau_m_range = np.linspace(0, ssu, 100)

# Línea de Soderberg (Recta Se a Sy)
ax_fat.plot([0, ssy], [sse, 0], 'green', lw=2, label='SODERBERG (Más Conservador)')
# Línea de Goodman (Recta Se a Su)
ax_fat.plot([0, ssu], [sse, 0], 'blue', lw=2, ls='--', label='GOODMAN (Estándar)')
# Línea de Gerber (Parábola Se a Su)
tau_a_gerber = sse * (1 - (tau_m_range / ssu)**2)
ax_fat.plot(tau_m_range, tau_a_gerber, 'orange', lw=2, label='GERBER (Menos Conservador)')

# Punto de Operación Real
ax_fat.scatter(tau_m, tau_a, color='red', s=150, edgecolor='black', zorder=10, label='Punto de Carga Real')

ax_fat.set_xlabel("Esfuerzo Medio τ_m (MPa)")
ax_fat.set_ylabel("Esfuerzo Alternante τ_a (MPa)")
ax_fat.set_xlim(0, ssu * 1.1); ax_fat.set_ylim(0, sse * 1.2)
ax_fat.grid(True, alpha=0.3)
ax_fat.legend()
st.pyplot(fig_fat)

# --- TABLA COMPARATIVA DE RESULTADOS ---
st.write("### Resumen de Factores de Seguridad")
st.table({
    "Criterio de Falla": ["Soderberg (Fluencia)", "Goodman (Fractura)", "Gerber (Parabólico)"],
    "Factor de Seguridad (FS)": [f"{fs_soderberg:.2f}", f"{fs_goodman:.2f}", f"{fs_gerber:.2f}"],
    "Estado": [
        "✅ Seguro" if fs_soderberg > 1.2 else "❌ Riesgo",
        "✅ Seguro" if fs_goodman > 1.2 else "❌ Riesgo",
        "✅ Seguro" if fs_gerber > 1.2 else "❌ Riesgo"
    ]
})

st.info("**Interpretación:** Si tu punto rojo está por debajo de la línea verde (Soderberg), el pin es extremadamente seguro. Si está entre la verde y la azul (Goodman), el pin resistirá la rotura pero podría tener ligeras deformaciones.")
