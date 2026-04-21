import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Simulador de Horno de Cemento Pro", layout="wide")

st.title("🔥 Simulador de Procesos: Horno Rotatorio de Clinker")
st.markdown("""
Esta herramienta simula la termodinámica y la cinética química de formación de **C3S (Alita)** 
basándose en las dimensiones físicas, el refractario y el balance de energía.
""")

# --- BARRA LATERAL: ENTRADA DE DATOS ---
st.sidebar.header("🛠️ Parámetros de Diseño")

# Dimensiones
with st.sidebar.expander("Dimensiones del Horno", expanded=True):
    L = st.number_input("Longitud Total (m)", value=60.0, step=1.0)
    D = st.number_input("Diámetro Interno (m)", value=4.0, step=0.1)

# Refractario
with st.sidebar.expander("Propiedades del Refractario"):
    k_ref = st.slider("Cond. Térmica (W/m·K)", 1.0, 5.0, 2.0)
    e_ref = st.slider("Espesor del Ladrillo (m)", 0.1, 0.3, 0.2)
    t_ambiente = st.number_input("Temp. Ambiente (°C)", value=30)

# Combustible y Material
with st.sidebar.expander("Operación y Materiales"):
    flujo_mat = st.number_input("Alimentación Crudo (kg/h)", value=120000)
    pci_comb = st.number_input("PCI Combustible (kJ/kg)", value=32000)
    flujo_comb = st.number_input("Flujo Combustible (kg/h)", value=8000)
    temp_entrada = st.number_input("Temp. Entrada Material (°C)", value=900)

# --- LÓGICA DE SIMULACIÓN ---

def calcular_simulacion():
    pasos = 200
    z = np.linspace(0, L, pasos)
    
    # 1. Simulación de Perfil de Temperatura (Modelo simplificado de transferencia)
    # Suponemos que la zona de quema está al final (entre el 70% y 100% de la longitud)
    potencia_total = (flujo_comb * pci_comb) / 3600 # kW
    perdidas_pared = (k_ref * (np.pi * D * L) * (1450 - 250)) / e_ref / 1000 # kW aprox
    
    # Perfil de temperatura del material
    # Sube gradualmente y tiene un pico en la zona de clinkerización
    temp_max = temp_entrada + (potencia_total - perdidas_pared) / (flujo_mat/3600 * 1.1)
    temp_mat = temp_entrada + (temp_max - temp_entrada) / (1 + np.exp(-0.3 * (z - (L*0.7))))

    # 2. Cinética de Formación de C3S
    # C2S + CaO -> C3S
    c3s = np.zeros(pasos)
    c2s = np.full(pasos, 60.0) # Inicia con 60% de Belita
    
    A = 1.2e12
    Ea = 450000
    R = 8.314
    dt = (L / pasos) # Delta de espacio (relacionado con tiempo de residencia)

    for i in range(1, pasos):
        Tk = temp_mat[i] + 273.15
        if temp_mat[i] > 1250: # Solo si hay fase líquida
            k = A * np.exp(-Ea / (R * Tk))
            reaccion = k * c2s[i-1] * dt * 0.5 # factor de escala
            c3s[i] = min(75.0, c3s[i-1] + reaccion)
            c2s[i] = max(0, c2s[i-1] - reaccion)
        else:
            c3s[i] = c3s[i-1]
            c2s[i] = c2s[i-1]
            
    return z, temp_mat, c3s, c2s, perdidas_pared

z, t_mat, c3s, c2s, perdidas = calcular_simulacion()

# --- VISUALIZACIÓN EN STREAMLIT ---

col1, col2, col3 = st.columns(3)
col1.metric("Pérdidas Térmicas", f"{perdidas:.2f} kW")
col2.metric("Temp. Máxima", f"{t_mat.max():.2f} °C")
col3.metric("Contenido final C3S", f"{c3s[-1]:.2f} %")

# Gráfica Principal
fig, ax1 = plt.subplots(figsize=(10, 5))

color = 'tab:red'
ax1.set_xlabel('Posición en el Horno (m)')
ax1.set_ylabel('Temperatura Material (°C)', color=color)
ax1.plot(z, t_mat, color=color, linewidth=3, label="Temp. Material")
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(alpha=0.3)

ax2 = ax1.twinx()
color = 'tab:blue'
ax2.set_ylabel('Fases del Clinker (%)', color=color)
ax2.plot(z, c3s, color=color, linewidth=2, label="C3S (Alita)")
ax2.plot(z, c2s, color='green', linestyle='--', label="C2S (Belita)")
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()
st.pyplot(fig)

# --- ANÁLISIS DE CALIDAD ---
st.subheader("📋 Análisis de Calidad del Clinker")
if c3s[-1] < 50:
    st.error(f"Calidad BAJA: El contenido de Alita ({c3s[-1]:.1f}%) es insuficiente. Aumente el combustible o reduzca la velocidad de alimentación.")
elif c3s[-1] < 65:
    st.warning(f"Calidad MEDIA: Contenido de Alita en {c3s[-1]:.1f}%. Apto para cementos de uso general.")
else:
    st.success(f"Calidad ALTA: Excelente formación de Alita ({c3s[-1]:.1f}%).")

st.info("💡 Consejo: Observe cómo el aumento del espesor del refractario reduce las pérdidas y mejora la temperatura de pico.")
