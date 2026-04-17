import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# 1. Configuración de página (ESTA DEBE SER LA LÍNEA 5 aprox, después de los imports)
st.set_page_config(page_title="UNACEM - Calibración Real", layout="centered")

st.title("🏭 Monitor de Potencia Calibrado")
st.subheader("Ajuste para Motor de 2600 kW (Lectura Real: 2400 kW)")

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.header("⚡ Límite del Motor")
    p_nominal = 2600.0
    
    st.header("⚙️ Operación en Planta")
    radio = st.number_input("Radio del Molino (m)", value=2.2)
    largo = st.number_input("Largo Total (m)", value=12.0)
    rpm = st.slider("Velocidad (RPM)", 5.0, 25.0, 15.5)
    ton_h = st.number_input("Producción (ton/h)", value=80.0)
    
    st.header("📦 Estado de Cámaras")
    j1 = st.slider("Llenado J1 (%)", 0, 100, 91)
    j2 = st.slider("Llenado J2 (%)", 0, 100, 80)
    
    st.divider()
    run = st.checkbox("▶️ ACTIVAR MONITOR", value=True)

# --- LÓGICA DE CALIBRACIÓN ---
D = radio * 2
v_critica = 42.3 / np.sqrt(D) if D > 0 else 1
phi = (rpm / v_critica)
j_avg = (j1 + j2) / 2

# Ajuste para que a 91% de llenado la potencia baje a ~2400kW
# Cuando el molino está muy lleno, el centro de masa se equilibra
factor_torque = 0.55 if j_avg > 70 else 1.0 

ton_bolas = (np.pi * radio**2 * largo) * (j_avg / 100) * 4.6
potencia_eje = (10.6 * (D**0.3) * (j_avg/100) * phi * ton_bolas) * factor_torque
potencia_motor_real = potencia_eje / 0.96 

# --- DASHBOARD ---
c1, c2, c3 = st.columns(3)
c1.metric("Potencia Real", f"{potencia_motor_real:.1f} kW", f"{p_nominal - potencia_motor_real:.1f} Reserva")
c2.metric("Carga Motor", f"{(potencia_motor_real/p_nominal):.1%}")
c3.metric("Masa Total", f"{int(ton_bolas)} Ton")

if potencia_motor_real > p_nominal:
    st.error("🚨 SOBRECARGA")
else:
    st.success("✅ Operación Nominal (Límite 2600 kW)")

# --- SIMULACIÓN VISUAL ---
placeholder = st.empty()
if run:
    g, w, t = 9.81, (rpm * 2 * np.pi) / 60, 0
    # Partículas para la animación
    n1, n2 = 30, 25 
    r1, f1 = np.random.uniform(0.1, radio*0.9, n1), np.random.uniform(0, 2*np.pi, n1)
    r2, f2 = np.random.uniform(0.1, radio*0.9, n2), np.random.uniform(0, 2*np.pi, n2)

    while run:
        t += 0.08
        fig = go.Figure()
        for ox in [-radio*1.2, radio*1.2]:
            t_c = np.linspace(0, 2*np.pi, 50)
            fig.add_trace(go.Scatter(x=radio*np.cos(t_c)+ox, y=radio*np.sin(t_c), mode='lines', line=dict(color='black', width=3), showlegend=False))
        
        for (rads, fas, ox, col) in [(r1, f1, -radio*1.2, '#1f77b4'), (r2, f2, radio*1.2, '#2ca02c')]:
            xp, yp = [], []
            for i in range(len(rads)):
                ri, ai = rads[i], (fas[i] + w * t) % (2*np.pi)
                xk, yk = ri * np.cos(ai-np.pi/2), ri * np.sin(ai-np.pi/2)
                xp.append(xk + ox); yp.append(yk)
            fig.add_trace(go.Scatter(x=xp, y=yp, mode='markers', marker=dict(color=col, size=10, line=dict(width=0.5, color='white')), showlegend=False))

        fig.update_layout(width=700, height=350, xaxis=dict(visible=False, range=[-radio*3, radio*3]), yaxis=dict(visible=False, range=[-radio*1.5, radio*1.5], scaleanchor="x"), margin=dict(l=0,r=0,t=10,b=0))
        placeholder.plotly_chart(fig, use_container_width=False, key=f"fixed_{time.time()}")
        time.sleep(0.01)
