import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Simulador Pro UNACEM", layout="wide")

st.title("🔄 Simulador de Molienda Dinámico")

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    radio = st.number_input("Radio del Molino (m)", value=2.0)
    largo = st.number_input("Largo del Molino (m)", value=6.0)
    st.divider()
    st.header("⚖️ Carga de Bolas")
    # Controlamos el llenado directamente
    llenado_j = st.slider("Porcentaje de Llenado (J %)", 10, 50, 35)
    st.header("⚡ Operación")
    rpm = st.slider("Velocidad (RPM)", 5, 50, 18)
    st.divider()
    run = st.checkbox("▶️ ACTIVAR ROTACIÓN", value=True)

# --- CÁLCULOS TÉCNICOS ---
D = radio * 2
v_critica = 42.3 / np.sqrt(D) if D > 0 else 1
phi = (rpm / v_critica) # Fracción de velocidad crítica

# Potencia estimada usando el llenado J real
ton_bolas = (np.pi * radio**2 * largo) * (llenado_j/100) * 4.6
potencia_kw = 10.6 * (D**0.3) * (llenado_j/100) * (1 - 1.03 * (llenado_j/100)) * phi * ton_bolas

c1, c2, c3 = st.columns(3)
c1.metric("Llenado Real", f"{llenado_j}%")
c2.metric("Consumo Motor", f"{potencia_kw:.1f} kW")
c3.metric("Vel. Crítica", f"{phi:.1%}")

# --- MOTOR DE ANIMACIÓN DINÁMICO ---
placeholder = st.empty()
g = 9.81
w = (rpm * 2 * np.pi) / 60

# El número de capas de bolas ahora depende del llenado J
num_capas = int(llenado_j / 3) 
radios_capas = np.linspace(radio * 0.4, radio * 0.95, num_capas)

t = 0
while run:
    t += 0.1
    fig = go.Figure()
    
    # 1. Dibujar Carcasa
    t_circ = np.linspace(0, 2*np.pi, 100)
    fig.add_trace(go.Scatter(x=radio*np.cos(t_circ), y=radio*np.sin(t_circ), 
                             mode='lines', line=dict(color='black', width=4), showlegend=False))
    
    # 2. Calcular posición con efecto de RPM (Ángulo de elevación)
    x_bolas, y_bolas, colores = [], [], []
    
    # El ángulo de desprendimiento cambia con las RPM (phi)
    # A más RPM, las bolas suben más antes de caer
    alfa_subida = np.pi * (0.2 + (phi * 0.4)) 

    for i, r_c in enumerate(radios_capas):
        # Generar varias bolas por capa para que se vea el área llena
        for a_offset in np.linspace(0, np.pi, 5):
            ang_actual = (a_offset + w * t) % (2 * np.pi)
            
            # Lógica: Si la bola está en la zona de subida (derecha inferior a superior)
            if ang_actual < alfa_subida:
                xk = r_c * np.cos(ang_actual - np.pi/2)
                yk = r_c * np.sin(ang_actual - np.pi/2)
                colores.append('darkred')
            else:
                # Fase de caída: más abierta a medida que suben las RPM
                distancia_caida = (ang_actual - alfa_subida)
                xk = r_c * np.cos(alfa_subida - np.pi/2) - (distancia_caida * phi * 2)
                yk = r_c * np.sin(alfa_subida - np.pi/2) - (0.5 * g * (distancia_caida**2) * 0.01)
                
                # Evitar que salgan de la carcasa
                dist_r = np.sqrt(xk**2 + yk**2)
                if dist_r > radio:
                    xk, yk = xk*(radio/dist_r), yk*(radio/dist_r)
                colores.append('red')
            
            x_bolas.append(xk)
            y_bolas.append(yk)

    fig.add_trace(go.Scatter(x=x_bolas, y=y_bolas, mode='markers', 
                             marker=dict(color=colores, size=10, line=dict(width=0.5, color='white')), 
                             showlegend=False))

    fig.update_layout(width=600, height=600, 
                      xaxis=dict(range=[-radio*1.2, radio*1.2], visible=False),
                      yaxis=dict(range=[-radio*1.2, radio*1.2], visible=False),
                      template="plotly_white")

    placeholder.plotly_chart(fig, use_container_width=True)
    time.sleep(0.04)

if not run:
    st.info("Simulación en pausa. Ajusta los parámetros y activa 'ROTACIÓN'.")
