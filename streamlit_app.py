import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# 1. Configuración de página
st.set_page_config(page_title="UNACEM - Efecto Cascada Real", layout="centered")

st.title("🏭 Monitor de Molienda UNACEM")
st.subheader("Simulación Física de Cascada y Catarata")

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.header("⚡ Datos del Motor")
    p_nominal = 2600.0
    
    st.divider()
    st.header("⚙️ Operación en Planta")
    radio = st.number_input("Radio del Molino (m)", value=2.2)
    largo = st.number_input("Largo Total (m)", value=12.0)
    # Aumentar RPM hará que las bolas caigan desde más arriba
    rpm = st.slider("Velocidad (RPM)", 5.0, 25.0, 15.5)
    ton_h = st.number_input("Producción (ton/h)", value=80.0)
    
    st.divider()
    st.header("📦 Cámaras")
    j1 = st.slider("Llenado J1 (%)", 0, 100, 91)
    d_bola1 = st.number_input("Ø Bola C1 (mm)", value=75.0)
    j2 = st.slider("Llenado J2 (%)", 0, 100, 80)
    d_bola2 = st.number_input("Ø Bola C2 (mm)", value=25.0)
    
    st.divider()
    run = st.checkbox("▶️ ACTIVAR MONITOR", value=True)

# --- LÓGICA DE INGENIERÍA Y BLAINE ---
D = radio * 2
v_critica = 42.3 / np.sqrt(D) if D > 0 else 1
phi = (rpm / v_critica)
j_avg = (j1 + j2) / 2

# Calibración para los 2400 kW reales
factor_calibracion = 0.5 if j_avg > 70 else 1.0
ton_bolas = (np.pi * radio**2 * largo) * (j_avg / 100) * 4.6
potencia_eje = (10.6 * (D**0.3) * (j_avg/100) * phi * ton_bolas) * factor_calibracion
potencia_motor_real = potencia_eje / 0.96 

# Modelo Blaine
blaine_entrada = 800
t_residencia = 80 / ton_h if ton_h > 0 else 1
delta_c1 = (j1 * phi * (100/d_bola1)) * 10 * t_residencia
delta_c2 = (j2 * phi * (40/d_bola2)) * 30 * t_residencia
blaine_salida = blaine_entrada + delta_c1 + delta_c2

# --- DASHBOARD ---
c1, c2, c3 = st.columns(3)
c1.metric("Potencia Real", f"{potencia_motor_real:.1f} kW")
c2.metric("Finura (Blaine)", f"{int(blaine_salida)} cm²/g")
c3.metric("% Vel. Crítica", f"{phi:.1%}")

# --- MOTOR DE ANIMACIÓN CON EFECTO CASCADA ---
placeholder = st.empty()
if run:
    g = 9.81
    w = (rpm * 2 * np.pi) / 60
    t_sim = 0
    
    # Partículas para la animación
    n1, n2 = 40, 35 
    radios1 = np.random.uniform(radio*0.3, radio*0.95, n1)
    fases1 = np.random.uniform(0, 2*np.pi, n1)
    radios2 = np.random.uniform(radio*0.3, radio*0.95, n2)
    fases2 = np.random.uniform(0, 2*np.pi, n2)

    while run:
        t_sim += 0.05
        fig = go.Figure()
        
        # Ángulo de desprendimiento dinámico (Efecto RPM)
        # A mayor RPM (phi), el ángulo es mayor y la bola cae desde más alto
        angulo_desprendimiento = (np.pi/4) + (phi * np.pi/3)

        def obtener_posicion(r_bola, fase_inicial):
            # Ángulo actual en el giro
            angulo_actual = (fase_inicial + w * t_sim) % (2 * np.pi)
            
            if angulo_actual < angulo_desprendimiento:
                # FASE 1: ASCENSO (Giran con el molino)
                xk = r_bola * np.cos(angulo_actual - np.pi/2)
                yk = r_bola * np.sin(angulo_actual - np.pi/2)
                return xk, yk, False
            else:
                # FASE 2: CAÍDA (Parábola/Cascada)
                t_caida = (angulo_actual - angulo_desprendimiento) / w
                x0 = r_bola * np.cos(angulo_desprendimiento - np.pi/2)
                y0 = r_bola * np.sin(angulo_desprendimiento - np.pi/2)
                vx = -w * r_bola * np.sin(angulo_desprendimiento - np.pi/2)
                vy = w * r_bola * np.cos(angulo_desprendimiento - np.pi/2)
                
                xk = x0 + vx * t_caida
                yk = y0 + vy * t_caida - 0.5 * g * (t_caida**2)
                
                # Si choca con el fondo, se queda ahí
                dist_centro = np.sqrt(xk**2 + yk**2)
                if dist_centro > radio:
                    xk = xk * (radio/dist_centro)
                    yk = yk * (radio/dist_centro)
                return xk, yk, True

        # Dibujar Cámaras y Partículas
        for (rs, fs, ox, col, sz) in [(radios1, fases1, -radio*1.2, '#1f77b4', d_bola1/10), 
                                      (radios2, fases2, radio*1.2, '#2ca02c', d_bola2/10)]:
            # Carcasa
            t_c = np.linspace(0, 2*np.pi, 50)
            fig.add_trace(go.Scatter(x=radio*np.cos(t_c)+ox, y=radio*np.sin(t_c), mode='lines', line=dict(color='black', width=3), showlegend=False))
            
            xp, yp, colores = [], [], []
            for i in range(len(rs)):
                xk, yk, en_caida = obtener_posicion(rs[i], fs[i])
                xp.append(xk + ox)
                yp.append(yk)
                colores.append('#FF4500' if en_caida else col) # Naranja si está cayendo
            
            fig.add_trace(go.Scatter(x=xp, y=yp, mode='markers', marker=dict(color=colores, size=sz, line=dict(width=0.4, color='white')), showlegend=False))

        fig.update_layout(width=700, height=350, xaxis=dict(visible=False, range=[-radio*3, radio*3]), 
                          yaxis=dict(visible=False, range=[-radio*1.5, radio*1.5], scaleanchor="x"), 
                          margin=dict(l=0,r=0,t=10,b=0), template="plotly_white")
        
        placeholder.plotly_chart(fig, use_container_width=False, key=f"cascada_{time.time()}")
        time.sleep(0.01)
