import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Simulador de Calor", layout="wide")
st.title("🔥 Simulación de Transferencia de Calor en 1D")
st.write("Ajusta los parámetros para ver cómo se propaga el calor en una barra.")

# Barra lateral para parámetros
st.sidebar.header("Parámetros del Material")
L = st.sidebar.slider("Longitud de la barra (m)", 0.5, 5.0, 1.0)
alpha = st.sidebar.slider("Difusividad (Material)", 0.001, 0.05, 0.01, format="%.3f")
tiempo = st.sidebar.slider("Tiempo de simulación", 0.1, 5.0, 1.0)

st.sidebar.header("Condiciones de Temperatura")
temp_izq = st.sidebar.number_input("Temperatura Extremo Izquierdo (°C)", value=100)
temp_der = st.sidebar.number_input("Temperatura Extremo Derecho (°C)", value=20)

# --- Lógica de la Simulación ---
nx = 50
dx = L / (nx - 1)
dt = 0.0005  # Paso de tiempo pequeño para estabilidad
nt = int(tiempo / dt)

# Condición inicial (barra a temp ambiente)
T = np.ones(nx) * 20.0
T[0] = temp_izq
T[-1] = temp_der

# Cálculo de diferencias finitas
for t in range(nt):
    Tn = T.copy()
    for i in range(1, nx - 1):
        T[i] = Tn[i] + alpha * dt / dx**2 * (Tn[i+1] - 2*Tn[i] + Tn[i-1])

# --- Gráfico con Matplotlib ---
fig, ax = plt.subplots()
x = np.linspace(0, L, nx)
ax.plot(x, T, color='red', linewidth=2)
ax.fill_between(x, T, 0, color='red', alpha=0.1)
ax.set_ylim(0, max(temp_izq, temp_der) + 20)
ax.set_xlabel("Posición en la barra (m)")
ax.set_ylabel("Temperatura (°C)")
ax.set_title("Perfil de Temperatura Final")
ax.grid(True, linestyle='--')

# Mostrar en Streamlit
st.pyplot(fig)

# Mostrar datos métricos
col1, col2 = st.columns(2)
col1.metric("Punto más caliente", f"{np.max(T):.1f} °C")
col2.metric("Promedio de la barra", f"{np.mean(T):.1f} °C")
