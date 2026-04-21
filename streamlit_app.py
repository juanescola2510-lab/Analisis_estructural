import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="Simulador de Materiales Térmicos", layout="wide")

# --- Diccionario de Materiales (Difusividad térmica aproximada en m²/s) ---
materiales = {
    "Cobre (Muy rápido)": 0.000111,
    "Aluminio": 0.000097,
    "Hierro": 0.000023,
    "Vidrio": 0.00000034,
    "Madera (Aislante)": 0.00000008,
    "Personalizado": 0.00001
}

st.title("🌡️ Simulador de Conducción según Material")

# --- Barra lateral ---
st.sidebar.header("Propiedades del Material")
seleccion = st.sidebar.selectbox("Selecciona un material:", list(materiales.keys()))

# Ajustar alpha según selección
if seleccion == "Personalizado":
    alpha = st.sidebar.slider("Difusividad manual:", 0.000001, 0.0001, 0.00001, format="%.6f")
else:
    alpha = materiales[seleccion]
    st.sidebar.info(f"Difusividad del {seleccion}: {alpha} m²/s")

st.sidebar.header("Condiciones iniciales")
temp_fuente = st.sidebar.slider("Temperatura de calor (°C)", 20, 1000, 500)
tiempo_sim = st.sidebar.slider("Duración (segundos)", 1, 60, 10)

if st.sidebar.button('🚀 Iniciar Simulación'):
    nx = 50
    dx = 0.1 # Barra de 10cm
    dt = 0.01 # Paso de tiempo
    nt = int(tiempo_sim / dt)
    
    T = np.ones(nx) * 25.0 # Temperatura inicial ambiente 25°C
    T[0] = temp_fuente      # Extremo caliente
    
    grafico_placeholder = st.empty()
    status_text = st.empty()
    barra_progreso = st.progress(0)

    # Simulación
    for t in range(nt):
        Tn = T.copy()
        # Ecuación de calor
        T[1:-1] = Tn[1:-1] + alpha * dt / dx**2 * (Tn[2:] - 2*Tn[1:-1] + Tn[0:-2])
        
        # Actualización visual cada cierto tiempo para no saturar
        if t % 50 == 0:
            fig, ax = plt.subplots(figsize=(10, 4))
            x = np.linspace(0, 10, nx) # cm
            ax.plot(x, T, color='red', lw=2)
            ax.fill_between(x, T, 25, color='orange', alpha=0.2)
            ax.set_ylim(0, temp_fuente + 50)
            ax.set_xlabel("Longitud de la barra (cm)")
            ax.set_ylabel("Temperatura (°C)")
            ax.set_title(f"Material: {seleccion} | Tiempo: {t*dt:.2f}s")
            
            grafico_placeholder.pyplot(fig)
            plt.close(fig)
            barra_progreso.progress(t / nt)
            
    st.success(f"Simulación de {seleccion} terminada.")
