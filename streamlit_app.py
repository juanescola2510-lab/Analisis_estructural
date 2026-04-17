import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 1. Configuración inicial
st.set_page_config(page_title="Simulador UNACEM v2", layout="centered")

st.title("🎥 Simulación: Caída de Bolas")
st.write("Si la animación no inicia, ajusta el control de RPM para refrescar el sistema.")

# 2. Parámetros (Ajustados para tu radio de 1.0m)
with st.sidebar:
    st.header("⚙️ Parámetros")
    rpm = st.slider("Velocidad (RPM)", 5, 40, 18)
    radio = st.number_input("Radio (m)", value=1.0)

# 3. Lógica Física de Trayectoria
g = 9.81
w = (rpm * 2 * np.pi) / 60
n_frames = 30
tiempos = np.linspace(0, 0.7, n_frames)

# Definimos 3 capas de bolas
angulos_lanzamiento = [np.pi/3, np.pi/4, np.pi/6]

# 4. Crear el Gráfico Base
fig = go.Figure()

# Dibujar Carcasa (Círculo)
t_circ = np.linspace(0, 2*np.pi, 100)
fig.add_trace(go.Scatter(
    x=radio * np.cos(t_circ), 
    y=radio * np.sin(t_circ), 
    mode='lines', 
    line=dict(color='black', width=4),
    name='Carcasa'
))

# 5. Crear los Frames de Animación
frames = []
for k in range(n_frames):
    frame_data = []
    # Añadimos la carcasa a cada frame
    frame_data.append(go.Scatter(x=radio*np.cos(t_circ), y=radio*np.sin(t_circ), mode='lines', line=dict(color='black', width=4)))
    
    for ang in angulos_lanzamiento:
        # Ecuación de proyectil
        x0, y0 = radio * np.cos(ang), radio * np.sin(ang)
        vx, vy = -w * radio * np.sin(ang), w * radio * np.cos(ang)
        
        tk = tiempos[k]
        xk = x0 + vx * tk
        yk = y0 + vy * tk - 0.5 * g * tk**2
        
        # Rastro
        tr = tiempos[:k+1]
        xr = x0 + vx * tr
        yr = y0 + vy * tr - 0.5 * g * tr**2
        
        frame_data.append(go.Scatter(x=xr, y=yr, mode='lines', line=dict(dash='dot', color='gray')))
        frame_data.append(go.Scatter(x=[xk], y=[yk], mode='markers', marker=dict(size=12, color='red')))
    
    frames.append(go.Frame(data=frame_data, name=str(k)))

fig.frames = frames

# 6. Configuración de botones (Versión Simplificada)
fig.update_layout(
    width=600, height=600,
    xaxis=dict(range=[-1.5, 1.5], autorange=False, showgrid=False),
    yaxis=dict(range=[-1.5, 1.5], autorange=False, showgrid=False),
    updatemenus=[{
        "type": "buttons",
        "buttons": [
            {
                "label": "▶️ PLAY",
                "method": "animate",
                "args": [None, {"frame": {"duration": 30, "redraw": True}, "fromcurrent": True}]
            },
            {
                "label": "⏸️ PAUSE",
                "method": "animate",
                "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]
            }
        ],
        "direction": "left",
        "x": 0.1, "y": -0.1
    }]
)

# 7. Forzar renderizado
st.plotly_chart(fig, use_container_width=True)

# 8. Información técnica extra
v_critica = 42.3 / np.sqrt(radio * 2) if radio > 0 else 0
st.write(f"**Velocidad Crítica:** {v_critica:.2f} RPM | **Estado:** {'Óptimo' if 65 < (rpm/v_critica)*100 < 80 else 'Revisar'}")
