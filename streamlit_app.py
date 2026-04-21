import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="Simulador Térmico Animado", layout="wide")
st.title("🔥 Simulación de Calor en Tiempo Real")

# --- Barra lateral ---
st.sidebar.header("Configuración")
alpha = st.sidebar.slider("Difusividad Térmica", 0.001, 0.05, 0.01)
temp_fuego = st.sidebar.slider("Temperatura de la Llama (°C)", 50, 500, 200)
pasos_animacion = st.sidebar.slider("Velocidad de simulación", 10, 100, 50)

if st.button('🚀 Iniciar Simulación'):
    # Inicialización
    nx = 50
    dx = 1.0 / (nx - 1)
    dt = 0.0005
    T = np.ones(nx) * 20.0 # Temperatura inicial ambiente
    T[0] = temp_fuego      # Extremo caliente
    
    # Contenedor para el gráfico dinámico
    grafico_placeholder = st.empty()
    progreso = st.progress(0)

    # Bucle de animación
    for t in range(pasos_animacion * 10):
        Tn = T.copy()
        for i in range(1, nx - 1):
            T[i] = Tn[i] + alpha * dt / dx**2 * (Tn[i+1] - 2*Tn[i] + Tn[i-1])
        
        # Actualizar gráfico cada 20 iteraciones para suavidad
        if t % 20 == 0:
            fig, ax = plt.subplots()
            ax.plot(np.linspace(0, 1, nx), T, color='orangered', lw=3)
            ax.set_ylim(0, temp_fuego + 50)
            ax.set_title(f"Propagación del Calor - Paso {t}")
            ax.set_ylabel("Temperatura °C")
            grafico_placeholder.pyplot(fig)
            plt.close(fig) # Limpiar memoria
            progreso.progress(min(t / (pasos_animacion * 10), 1.0))
            
    st.success("¡Simulación completada!")
