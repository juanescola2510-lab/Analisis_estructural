import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Configuración de la página para que se vea bien en móviles y PC
st.set_page_config(page_title="Simulador UNACEM - Caída de Bolas", layout="wide")

st.title("🎥 Simulación Animada: Caída de Bolas")
st.write("Visualización de trayectoria y punto de impacto en el molino.")

# --- BARRA LATERAL: CONTROLES ---
with st.sidebar:
    st.header("⚙️ Ajustes del Molino")
    rpm = st.slider("Velocidad de Rotación (RPM)", 5, 40, 16)
    radio = st.number_input("Radio del Molino (m)", value=1.0, step=0.1)
    st.divider()
    st.info("💡 Presiona el botón de Play debajo del gráfico para iniciar.")

# --- LÓGICA FÍSICA ---
g = 9.81
w = (rpm * 2 * np.pi) / 60
num_frames = 40
t_vuelo = np.linspace(0, 0.8, num_frames)

# Ángulos de lanzamiento (3 capas de bolas para ver el efecto)
capas = [np.pi/3, np.pi/4, np.pi/6]

# --- CREACIÓN DE LA ANIMACIÓN ---
fig = go.Figure()

# 1. Dibujar el cuerpo del molino (Círculo estático)
t_circ = np.linspace(0, 2*np.pi, 100)
x_circ = radio * np.cos(t_circ)
y_circ = radio * np.sin(t_circ)

# Añadimos la traza inicial (Frame 0)
fig.add_trace(go.Scatter(x=x_circ, y=y_circ, mode='lines', line=dict(color='black', width=4), name="Carcasa"))

# 2. Construcción de los Frames de la animación
frames = []
for k in range(num_frames):
    frame_data = []
    # Dibujar siempre la carcasa
    frame_data.append(go.Scatter(x=x_circ, y=y_circ, mode='lines', line=dict(color='black', width=4)))
    
    for i, ang in enumerate(capas):
        # Punto de desprendimiento
        x0, y0 = radio * np.cos(ang), radio * np.sin(ang)
        vx, vy = -w * radio * np.sin(ang), w * radio * np.cos(ang)
        
        # Posición en el tiempo k
        tk = t_vuelo[k]
        xk = x0 + vx * tk
        yk = y0 + vy * tk - 0.5 * g * tk**2
        
        # Rastro punteado hasta la posición actual
        trastro = t_vuelo[:k+1]
        xrastro = x0 + vx * trastro
        yrastro = y0 + vy * trastro - 0.5 * g * trastro**2
        
        # Añadir rastro y bola
        frame_data.append(go.Scatter(x=xrastro, y=yrastro, mode='lines', line=dict(dash='dot', width=1, color='gray'), showlegend=False))
        frame_data.append(go.Scatter(x=[xk], y=[yk], mode='markers', marker=dict(size=12, color='red'), showlegend=False))
        
    frames.append(go.Frame(data=frame_data, name=str(k)))

# 3. Configuración del Layout y Controles de Animación
fig.frames = frames
fig.update_layout(
    width=650, height=650,
    # Ejes fijos para evitar que el gráfico se "mueva" o desaparezca
    xaxis=dict(range=[-radio*1.5, radio*1.5], autorange=False, showgrid=False, zeroline=True),
    yaxis=dict(range=[-radio*1.5, radio*1.5], autorange=False, showgrid=False, zeroline=True),
    updatemenus=[{
        "buttons": [
            {
                "args": [None, {"frame": {"duration": 40, "redraw": True}, "fromcurrent": True, "transition": {"duration": 0}}],
                "label": "▶️ Iniciar Simulación", 
                "method": "animate"
            },
            {
                "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}],
                "label": "⏸️ Pausar", 
                "method": "animate"
            }
        ],
        "type": "buttons",
        "direction": "left",
        "pad": {"r": 10, "t": 85},
        "showactive": False,
        "x": 0.1,
        "y": 0
    }],
    template="plotly_white"
)

# Renderizar el gráfico
st.plotly_chart(fig, use_container_width=True)

# --- PANEL DE ANÁLISIS ---
st.divider()
v_critica = 42.3 / np.sqrt(radio * 2) if radio > 0 else 0
porcentaje = (rpm / v_critica) * 100 if v_critica > 0 else 0

col1, col2 = st.columns(2)
with col1:
    st.metric("Velocidad Crítica Calculada", f"{v_critica:.2f} RPM")
with col2:
    st.metric("% de Velocidad Crítica", f"{porcentaje:.1f}%")

if porcentaje > 80:
    st.error("🚨 ALERTA: Centrifugación detectada. Las bolas no caerán, dañando los blindajes.")
elif 65 <= porcentaje <= 75:
    st.success("🎯 ZONA ÓPTIMA: Efecto catarata máximo para molienda de puzolana.")
else:
    st.warning("⚠️ Molienda ineficiente: Poca energía de impacto.")
