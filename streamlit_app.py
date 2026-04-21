import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulador Horno Cilíndrico", layout="wide")

st.title("🌀 Transferencia de Calor Radial - Horno Cilíndrico")
st.markdown("Cálculo de gradiente térmico para refractarios en geometrías circulares.")

# --- BARRA LATERAL ---
st.sidebar.header("📐 Geometría del Horno")
radio_int_cm = st.sidebar.slider("Radio Interior (cm)", 10, 100, 30)
espesor_cm = st.sidebar.slider("Espesor Refractario (cm)", 5, 40, 15)
largo_horno = st.sidebar.number_input("Largo del horno (m)", value=2.0)

st.sidebar.header("🛡️ Material Refractario")
k_ref = st.sidebar.slider("Conductividad (k) en W/m·K", 0.1, 2.0, 1.2)

st.sidebar.header("⚙️ Operación")
temp_interior = 1500 # °C
temp_ambiente = 25   # °C
precio_gas = st.sidebar.number_input("Precio m³ Gas ($)", value=0.60)

# --- CÁLCULOS FÍSICOS RADIALES ---
r1 = radio_int_cm / 100
r2 = (radio_int_cm + espesor_cm) / 100

# Resistencia Térmica Cilíndrica: ln(r2/r1) / (2 * pi * k * L)
resistencia_radial = np.log(r2/r1) / (2 * np.pi * k_ref * largo_horno)

# Flujo de calor total (Watts)
q_total = (temp_interior - temp_ambiente) / resistencia_radial

# Temperatura en la chapa (cara externa r2)
# Usamos una resistencia superficial externa simplificada
t_chapa = temp_ambiente + (q_total * 0.02) # 0.02 estimado de convección aire

# --- MÉTRICAS ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Temp. Exterior Chapa", f"{t_chapa:.1f} °C")
with col2:
    st.metric("Pérdida de Calor", f"{q_total/1000:.2f} kW")
with col3:
    gas_mensual = ((q_total/1000) * 160) / 10.5 # 160h mes
    st.metric("Costo Mensual Gas", f"${gas_mensual * precio_gas:.2f}")

# --- GRÁFICO DE PERFIL RADIAL ---
st.subheader("📊 Gradiente Térmico Radial (Perfil Curvo)")

# Generar radios para la gráfica
radios = np.linspace(r1, r2, 100)
# Fórmula del perfil de temperatura radial: 
# T(r) = T1 - (T1 - T2) * [ln(r/r1) / ln(r2/r1)]
temperaturas = temp_interior - (temp_interior - t_chapa) * (np.log(radios/r1) / np.log(r2/r1))

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(radios * 100, temperaturas, color='red', lw=3, label='Descenso de Calor')
ax.fill_between(radios * 100, temperaturas, temp_ambiente, color='orange', alpha=0.1)

ax.set_xlabel("Radio desde el centro (cm)")
ax.set_ylabel("Temperatura (°C)")
ax.set_title("Distribución de Calor a través del Cilindro")
ax.grid(True, linestyle='--')
ax.axvline(r1*100, color='black', linestyle='--', label='Cara Interna')
ax.axvline(r2*100, color='blue', linestyle='--', label='Chapa Metálica')
ax.legend()

st.pyplot(fig)

st.info("""
💡 **Nota de Ingeniería:** En cilindros, la temperatura no baja de forma recta (lineal), 
sino de forma **logarítmica**. Esto significa que las primeras capas de ladrillo 
soportan mucho más estrés térmico que las capas exteriores.
""")
