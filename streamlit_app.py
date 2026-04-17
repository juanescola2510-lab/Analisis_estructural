import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Simulador UNACEM Fijo", layout="centered")

st.title("🎥 Simulación: Caída de Bolas")
st.write("Si no ves las bolas, mueve el slider de RPM para refrescar.")

# 1. Parámetros
with st.sidebar:
    rpm = st.slider("Velocidad (RPM)", 5, 40, 18)
    radio = st.number_input("Radio (m)", value=1.0)

# 2. Lógica Física
g = 9.81
w = (rpm * 2 * np.pi) / 60
n_frames = 25
tiempos = np.linspace(0, 0.7, n_frames)
capas = [np.pi/3, np.pi/4, np.pi/6]

# 3. CREAR EL GRÁFICO BASE CON LAS BOLAS YA DIBUJADAS (FRAME 0)
fig = go.Figure()

# Traza 0: Carcasa
t_circ = np.linspace(0, 2*np.pi, 100)
fig.add_trace(go.Scatter(x=radio*np.cos(t_circ), y=radio*np.sin(t_circ), mode='lines', line=dict(color='black', width=4), name='Carcasa'))

# Trazas de inicialización para las 3 capas (bolas y rastros iniciales)
for i, ang in enumerate(capas):
    x0, y0 = radio * np.cos(ang), radio * np.sin(ang)
    # Rastro inicial (un punto)
    fig.add_trace(go.Scatter(x=[x0], y=[y0], mode='lines', line=dict(dash='dot', color='gray'), showlegend=False))
    # Bola inicial
    fig.add_trace(go.Scatter(x=[x0], y=[y0], mode='markers', marker=dict(size=12, color='red'), showlegend=False))

# 4. CREAR LOS FRAMES
frames = []
for k in range(n_frames):
    frame_data = []
    # La carcasa siempre es la primera traza
    frame_data.append(go.Scatter(x=radio*np.cos(t_circ), y=radio*np.sin(t_circ)))
    
    for ang in capas:
        x0, y0 = radio * np.cos(ang), radio * np.sin(ang)
        vx, vy = -w * radio * np.sin(ang), w * radio * np.cos(ang)
        tk = tiempos[k]
        xk = x0 + vx * tk
        yk = y0 + vy * tk - 0.5 * g * tk**2
        
        tr = tiempos[:k+1]
        xr = x0 + vx * tr
        yr = y0 + vy * tk - 0.5 * g * tr**2 # Nota: Corregí un pequeño error de índice aquí
        
        frame_data.append(go.Scatter(x=xr, y=yr)) # Rastro
        frame_data.append(go.Scatter(x=[xk], y=[yk])) # Bola
        
    frames.append(go.Frame(data=frame_data, name=str(k)))

fig.frames = frames

# 5. CONFIGURACIÓN FINAL
fig.update_layout(
    width=600, height=600,
    xaxis=dict(range=[-1.5, 1.5], autorange=False, showgrid=False),
    yaxis=dict(range=[-1.5, 1.5], autorange=False, showgrid=False),
    updatemenus=[{
        "type": "buttons",
        "buttons": [
            {"label": "▶️ PLAY", "method": "animate", "args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}]},
            {"label": "⏸️ PAUSE", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]}
        ],
        "x": 0.1, "y": -0.1
    }]
)

st.plotly_chart(fig, use_container_width=True)
