import streamlit as st
import numpy as np
import pandas as pd
import time

st.set_page_config(page_title="Simulador Físico de Molino", layout="centered")

st.title("🏐 Simulación de Carga: Efecto Catarata")
st.write("Ajusta la velocidad para ver cómo cambia la trayectoria de las bolas.")

# --- PARÁMETROS DE CONTROL ---
col1, col2 = st.columns(2)
with col1:
    rpm = st.slider("Velocidad de Rotación (RPM)", min_value=0, max_value=40, value=15)
    num_bolas = st.slider("Cantidad de Bolas en simulación", 10, 100, 50)
with col2:
    radio_molino = 100 # Píxeles
    gravedad = 9.8

# --- LÓGICA DE FÍSICA SIMPLIFICADA ---
# Calculamos la posición de cada bola basándonos en el ángulo de elevación
# El ángulo donde la bola se desprende depende de la velocidad angular

w = (rpm * 2 * np.pi) / 60 # Velocidad angular en rad/s
v_critica = np.sqrt(gravedad / (radio_molino / 100)) # rad/s
ratio_critico = w / v_critica if v_critica > 0 else 0

# Crear DataFrame para las posiciones de las bolas
angulos = np.linspace(0, 2 * np.pi, num_bolas)
posiciones = []

# Simulación de un "frame" de movimiento
t = time.time()
for i in range(num_bolas):
    # Ángulo base + rotación en el tiempo
    theta = angulos[i] + (w * t) 
    
    # Si la bola está en la zona de ascenso (derecha), sigue el círculo
    # Si llega al punto de caída (arriba), simulamos parábola
    x = radio_molino * np.cos(theta)
    y = radio_molino * np.sin(theta)
    
    posiciones.append({'x': x, 'y': y})

df = pd.DataFrame(posiciones)

# --- VISUALIZACIÓN ---
# Usamos un gráfico de dispersión para simular las bolas
import plotly.graph_objects as go

fig = go.Figure()

# Dibujar cuerpo del molino
theta_circ = np.linspace(0, 2*np.pi, 100)
fig.add_trace(go.Scatter(x=radio_molino*np.cos(theta_circ), y=radio_molino*np.sin(theta_circ), 
                         mode='lines', line=dict(color='black', width=4), name='Carcasa'))

# Dibujar bolas
fig.add_trace(go.Scatter(x=df['x'], y=df['y'], mode='markers', 
                         marker=dict(size=10, color='blue'), name='Bolas'))

fig.update_layout(
    width=500, height=500,
    xaxis=dict(range=[-150, 150], showgrid=False, zeroline=False),
    yaxis=dict(range=[-150, 150], showgrid=False, zeroline=False),
    template="plotly_white"
)

st.plotly_chart(fig)

# --- ANÁLISIS TÉCNICO ---
if ratio_critico > 0.8:
    st.error(f"¡CENTRIFUGACIÓN! Las bolas se pegan a la pared. Eficiencia de molienda: 0%")
elif ratio_critico > 0.6:
    st.success(f"EFECTO CATARATA: Máximo impacto para puzolana gruesa.")
else:
    st.warning(f"EFECTO CASCADA: Molienda por atrición (fina).")

st.info(f"Velocidad Relativa: {ratio_critico:.2%}")
