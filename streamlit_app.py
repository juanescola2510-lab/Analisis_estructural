import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Simulador Animado UNACEM", layout="wide")

st.title("🎥 Simulación Animada: Caída de Bolas")
st.subheader("Visualización de Trayectoria y Punto de Impacto")

# --- PARÁMETROS EN LA BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Ajustes del Molino")
    rpm = st.slider("Velocidad de Rotación (RPM)", 5, 35, 16)
    radio = st.number_input("Radio del Molino (m)", value=2.0)
    num_frames = 30 # Duración de la animación

# --- LÓGICA FÍSICA ---
g = 9.81
w = (rpm * 2 * np.pi) / 60
t_vuelo = np.linspace(0, 0.8, num_frames)

# Ángulos de las capas de bolas
capas = [np.pi/3, np.pi/4, np.pi/6]

# --- CREACIÓN DE LA ANIMACIÓN CON PLOTLY ---
fig = go.Figure()

# 1. Dibujar el cuerpo del molino (Estático)
t_circ = np.linspace(0, 2*np.pi, 100)
fig.add_trace(go.Scatter(x=radio*np.cos(t_circ), y=radio*np.sin(t_circ), 
                         mode='lines', line=dict(color='black', width=4), 
                         showlegend=False))

# 2. Configurar frames (el movimiento)
frames = []
for k in range(len(t_vuelo)):
    frame_data = []
    # Dibujar la carcasa en cada frame para que no desaparezca
    frame_data.append(go.Scatter(x=radio*np.cos(t_circ), y=radio*np.sin(t_circ), mode='lines', line=dict(color='black', width=4)))
    
    for ang in capas:
        # Ecuaciones de movimiento parabólico
        x0, y0 = radio * np.cos(ang), radio * np.sin(ang)
        vx, vy = -w * radio * np.sin(ang), w * radio * np.cos(ang)
        
        # Posición actual de la bola en el frame k
        tk = t_vuelo[k]
        xk = x0 + vx * tk
        yk = y0 + vy * tk - 0.5 * g * tk**2
        
        # Rastro (posiciones anteriores hasta k)
        trastro = t_vuelo[:k+1]
        xrastro = x0 + vx * trastro
        yrastro = y0 + vy * trastro - 0.5 * g * trastro**2
        
        # Añadir rastro y bola al frame
        frame_data.append(go.Scatter(x=xrastro, y=yrastro, mode='lines', line=dict(dash='dot', width=1)))
        frame_data.append(go.Scatter(x=[xk], y=[yk], mode='markers', marker=dict(size=12, color='red')))
        
    frames.append(go.Frame(data=frame_data, name=str(k)))

# 3. Configurar el Layout y Botones de Play
fig.frames = frames
fig.update_layout(
    width=700, height=700,
    xaxis=dict(range=[-3, 3], showgrid=False, zeroline=False),
    yaxis=dict(range=[-3, 3], showgrid=False, zeroline=False),
    updatemenus=[{
        "buttons": [
            {"args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}],
             "label": "▶️ Iniciar Simulación", "method": "animate"},
            {"args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
             "label": "⏸️ Pausar", "method": "animate"}
        ],
        "type": "buttons", "direction": "left", "pad": {"r": 10, "t": 87}, "showactive": False, "x": 0.1, "y": 0
    }]
)

st.plotly_chart(fig, use_container_width=True)

# --- NOTA TÉCNICA ---
st.info("""
**Análisis de Trayectoria:** 
El punto donde el rastro rojo termina indica el impacto. Si el impacto ocurre por encima de la línea media horizontal, 
estás protegiendo los blindajes. Si el impacto es muy bajo, el efecto es puramente de fricción (cascada).
""")
