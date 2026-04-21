import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Configuración inicial
st.set_page_config(page_title="Simulador de Horno Industrial", layout="wide")

st.title("🔥 Simulador de Transferencia de Calor y Eficiencia en Hornos")
st.markdown("""
Esta herramienta simula la protección de la chapa de un horno ante una llama de **1500°C** 
y calcula cuánto dinero se pierde por transferencia de calor a través del refractario.
""")

# --- BARRA LATERAL: PARÁMETROS ---
st.sidebar.header("🛡️ Configuración del Aislamiento")
material_tipo = st.sidebar.selectbox(
    "Tipo de Refractario:",
    ["Ladrillo Denso (Alta Resistencia)", "Ladrillo Aislante (Baja Conductividad)", "Fibra Cerámica"]
)

# Definición de conductividad térmica (W/m·K) según material
dict_k = {
    "Ladrillo Denso (Alta Resistencia)": 1.4,
    "Ladrillo Aislante (Baja Conductividad)": 0.3,
    "Fibra Cerámica": 0.12
}
k_ref = dict_k[material_tipo]

espesor_cm = st.sidebar.slider("Espesor del refractario (cm)", 5, 50, 20)
espesor_m = espesor_cm / 100

st.sidebar.header("⚙️ Operación y Costos")
area_paredes = st.sidebar.number_input("Área de paredes (m²)", value=10.0)
horas_mes = st.sidebar.number_input("Horas de uso al mes", value=160)
precio_gas = st.sidebar.number_input("Precio del m³ de Gas ($)", value=0.60)

# --- CÁLCULOS FÍSICOS ---
temp_llama = 1500
temp_ambiente = 25

# Resistencia térmica (R = L/k)
resistencia = espesor_m / k_ref
# Flujo de calor por m2 (Q = ΔT / R)
flujo_calor_m2 = (temp_llama - temp_ambiente) / resistencia
# Temperatura estimada en la cara externa (chapa) - simplificado
t_chapa = temp_ambiente + (flujo_calor_m2 * 0.04) # 0.04 es resistencia superficial del aire

# --- INTERFAZ DE RESULTADOS ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Temp. en la Chapa", f"{t_chapa:.1f} °C")
    if t_chapa > 100:
        st.error("⚠️ CRÍTICO: La chapa se puede deformar.")
    else:
        st.success("✅ Temperatura segura.")

with col2:
    perdida_total_kw = (flujo_calor_m2 * area_paredes) / 1000
    st.metric("Pérdida de Energía", f"{perdida_total_kw:.2f} kW")

with col3:
    # 1m3 gas aprox 10.5 kWh
    gas_mensual = (perdida_total_kw * horas_mes) / 10.5
    costo_mensual = gas_mensual * precio_gas
    st.metric("Costo Mensual (Pérdida)", f"${costo_mensual:.2f}")

# --- GRÁFICO DE GRADIENTE TÉRMICO ---
st.subheader("📊 Perfil de Temperatura en el interior del Refractario")

fig, ax = plt.subplots(figsize=(10, 4))
puntos_x = np.linspace(0, espesor_cm, 100)
# Gradiente lineal (Simplificación de estado estacionario)
puntos_y = temp_llama - (temp_llama - t_chapa) * (puntos_x / espesor_cm)

ax.plot(puntos_x, puntos_y, color='red', linewidth=3, label='Gradiente de Calor')
ax.fill_between(puntos_x, puntos_y, color='orange', alpha=0.2)
ax.set_xlabel("Espesor del material (cm)")
ax.set_ylabel("Temperatura (°C)")
ax.axhline(1500, color='darkred', linestyle='--', label='Llama (1500°C)')
ax.legend()
ax.grid(True, linestyle=':', alpha=0.6)

st.pyplot(fig)

st.info(f"""
💡 **Análisis del Ing:** Estás usando **{material_tipo}**. 
Si cambias a un material con menor conductividad térmica o aumentas el espesor, 
el gradiente será más pronunciado y la chapa estará más fría, ahorrando combustible.
""")
