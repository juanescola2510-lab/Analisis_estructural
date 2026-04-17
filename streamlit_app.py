import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Simulador Rotativo UNACEM", layout="wide")

st.title("🔄 Simulador de Molino Rotativo (Versión Estable)")

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    radio = st.number_input("Radio del Molino (m)", value=2.0)
    largo = st.number_input("Largo del Molino (m)", value=6.0)
    rpm = st.slider("Velocidad (RPM)", 5, 45, 18)
    st.divider()
    run = st.checkbox("▶️ ACTIVAR ROTACIÓN", value=False)
    st.info("Activa el check para iniciar el movimiento.")

# --- CÁLCULOS DE POTENCIA ---
D = radio * 2
v_critica = 42.3 / np.sqrt(D) if D > 0 else 1
phi = rpm / v_critica
potencia_kw = 10.6 * (D**0.3) * 0.35 * (1 - 1.03 * 0.35) * phi * 100 # Estimación base

c1, c2 = st.columns(2)
c1.metric("Consumo Motor", f"{potencia_kw:.1f} kW")
c2.metric("Velocidad Crítica", f"{phi:.1%}")

# --- MOTOR DE ANIMACIÓN ---
placeholder = st.empty() # Espacio reservado para el gráfico
g = 9.81
w = (rpm * 2 * np.pi) / 60

# Definimos 12 capas de bolas para que se vea lleno
radios_capas = np.linspace(radio * 0.5, radio * 0.95, 12)
angulos_base = np.linspace(-np.pi, np.pi, 12)

t = 0
while run:
    t += 0.1 # Incremento de tiempo para el movimiento
    
    fig = go.Figure()
    
    # 1. Dibujar Carcasa
    t_circ = np.linspace(0, 2*np.pi, 100)
    fig.add_trace(go.Scatter(x=radio*np.cos(t_circ), y=radio*np.sin(t_circ), 
                             mode='lines', line=dict(color='black', width=4), showlegend=False))
    
    # 2. Calcular posición de cada bola
    x_bolas = []
    y_bolas = []
    colores = []
    
    for i, r_c in enumerate(radios_capas):
        # Ángulo de desprendimiento (Física de molienda)
        cos_alpha = (w**2 * r_c) / g
        alfa_desc = np.arccos(min(1, cos_alpha))
        
        ang_actual = (angulos_base[i] + w * t) % (2 * np.pi)
        
        if ang_actual < alfa_desc or ang_actual > (2*np.pi - alfa_desc):
            # Fase de rotación con la carcasa
            xk = r_c * np.cos(ang_actual)
            yk = r_c * np.sin(ang_actual)
            colores.append('darkred')
        else:
            # Fase de caída parabólica simplificada para fluidez
            xk = r_c * np.cos(ang_actual) * 0.8 # Contracción visual de caída
            yk = r_c * np.sin(ang_actual) - (0.5 * g * 0.1)
            colores.append('red')
            
        x_bolas.append(xk)
        y_bolas.append(yk)

    fig.add_trace(go.Scatter(x=x_bolas, y=y_bolas, mode='markers', 
                             marker=dict(color=colores, size=12, line=dict(width=1, color='white')), 
                             showlegend=False))

    fig.update_layout(width=600, height=600, 
                      xaxis=dict(range=[-radio*1.2, radio*1.2], showgrid=False, zeroline=False, visible=False),
                      yaxis=dict(range=[-radio*1.2, radio*1.2], showgrid=False, zeroline=False, visible=False),
                      template="plotly_white")

    placeholder.plotly_chart(fig, use_container_width=True)
    time.sleep(0.05) # Control de velocidad de la animación

if not run:
    st.warning("La simulación está pausada. Activa el cuadro 'ACTIVAR ROTACIÓN' en la izquierda.")
