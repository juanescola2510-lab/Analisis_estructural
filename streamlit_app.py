import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# 1. Configuración de página
st.set_page_config(page_title="UNACEM - Auditoría Real", layout="centered")

st.title("🏭 Monitor Maestro UNACEM")
st.subheader("Calibración Real: 2400 kW | Costos y Finura (Blaine)")

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.header("⚡ Parámetros Económicos")
    costo_kwh = st.number_input("Costo Energía (USD/kWh)", value=0.09, format="%.4f")
    p_nominal = 2600.0
    
    st.divider()
    st.header("⚙️ Operación en Planta")
    radio = st.number_input("Radio del Molino (m)", value=2.2)
    largo = st.number_input("Largo Total (m)", value=12.0)
    rpm = st.slider("Velocidad (RPM)", 5.0, 25.0, 15.5)
    ton_h = st.number_input("Producción (ton/h)", value=80.0)
    
    st.divider()
    st.header("📦 Cámaras de Molienda")
    j1 = st.slider("Llenado J1 (%)", 0, 100, 91)
    d_bola1 = st.number_input("Ø Bola C1 (mm)", value=75.0)
    j2 = st.slider("Llenado J2 (%)", 0, 100, 80)
    d_bola2 = st.number_input("Ø Bola C2 (mm)", value=25.0)
    
    st.divider()
    run = st.checkbox("▶️ ACTIVAR MONITOR", value=True)

# --- LÓGICA DE INGENIERÍA CALIBRADA ---
D = radio * 2
v_critica = 42.3 / np.sqrt(D) if D > 0 else 1
phi = (rpm / v_critica)
j_avg = (j1 + j2) / 2

# Calibración de Potencia para ajustar a los 2400 kW reales medidos
factor_calibracion = 0.5 if j_avg > 70 else 1.0
ton_bolas = (np.pi * radio**2 * largo) * (j_avg / 100) * 4.6
potencia_eje = (10.6 * (D**0.3) * (j_avg/100) * phi * ton_bolas) * factor_calibracion
potencia_motor_real = potencia_eje / 0.96 

# CÁLCULOS DE COSTO
costo_hora = potencia_motor_real * costo_kwh
costo_ton = costo_hora / ton_h if ton_h > 0 else 0

# Modelo Blaine (Finura)
blaine_entrada = 800
t_residencia = 80 / ton_h if ton_h > 0 else 1
delta_c1 = (j1 * phi * (100/d_bola1)) * 10 * t_residencia
delta_c2 = (j2 * phi * (40/d_bola2)) * 30 * t_residencia
blaine_salida = blaine_entrada + delta_c1 + delta_c2

# --- DASHBOARD DE RESULTADOS ---
c1, c2, c3 = st.columns(3)
c1.metric("Potencia Real", f"{potencia_motor_real:.1f} kW", f"{p_nominal - potencia_motor_real:.1f} Reserva")
c2.metric("Finura (Blaine)", f"{int(blaine_salida)} cm²/g", f"+{int(delta_c1+delta_c2)}")
c3.metric("Costo Energía", f"${costo_ton:.2f} / ton", f"${costo_hora:.2f} / hora")

if potencia_motor_real > p_nominal:
    st.error(f"🚨 ALERTA: Sobrecarga del Motor ({potencia_motor_real:.1f} kW)")
else:
    st.success(f"✅ Operación Estable ({potencia_motor_real/p_nominal:.1%} de carga motor)")

# --- MOTOR DE ANIMACIÓN CON EFECTO CASCADA ---
placeholder = st.empty()
if run:
    g, w, t_sim = 9.81, (rpm * 2 * np.pi) / 60, 0
    n1, n2 = 35, 30 
    radios1 = np.random.uniform(radio*0.3, radio*0.95, n1)
    fases1 = np.random.uniform(0, 2*np.pi, n1)
    radios2 = np.random.uniform(radio*0.3, radio*0.95, n2)
    fases2 = np.random.uniform(0, 2*np.pi, n2)

    while run:
        t_sim += 0.05
        fig = go.Figure()
        
        # Ángulo de desprendimiento dinámico (Efecto RPM)
        angulo_desp = (np.pi/4) + (phi * np.pi/3)

        def obtener_pos(r_b, f_i):
            ang_act = (f_i + w * t_sim) % (2 * np.pi)
            if ang_act < ang_desp:
                # FASE ASCENSO
                return r_b * np.cos(ang_act - np.pi/2), r_b * np.sin(ang_act - np.pi/2), False
            else:
                # FASE CAÍDA (Cascada)
                tc = (ang_act - ang_desp) / w
                x0, y0 = r_b * np.cos(ang_desp - np.pi/2), r_b * np.sin(ang_desp - np.pi/2)
                vx, vy = -w * r_b * np.sin(ang_desp - np.pi/2), w * r_b * np.cos(ang_desp - np.pi/2)
                xk, yk = x0 + vx * tc, y0 + vy * tc - 0.5 * g * (tc**2)
                if np.sqrt(xk**2 + yk**2) > radio:
                    xk, yk = xk * (radio/np.sqrt(xk**2+yk**2)), yk * (radio/np.sqrt(xk**2+yk**2))
                return xk, yk, True

        # Dibujar Cámaras y Partículas
        for (rs, fs, ox, col, sz) in [(radios1, fases1, -radio*1.2, '#1f77b4', d_bola1/10), 
                                      (radios2, fases2, radio*1.2, '#2ca02c', d_bola2/10)]:
            t_c = np.linspace(0, 2*np.pi, 50)
            fig.add_trace(go.Scatter(x=radio*np.cos(t_c)+ox, y=radio*np.sin(t_c), mode='lines', line=dict(color='black', width=3), showlegend=False))
            xp, yp, cols = [], [], []
            for i in range(len(rs)):
                xk, yk, cai = obtener_pos(rs[i], fs[i])
                xp.append(xk + ox); yp.append(yk)
                cols.append('#FF4500' if cai else col)
            fig.add_trace(go.Scatter(x=xp, y=yp, mode='markers', marker=dict(color=cols, size=sz, line=dict(width=0.4, color='white')), showlegend=False))

        fig.update_layout(width=700, height=350, xaxis=dict(visible=False, range=[-radio*3, radio*3]), 
                          yaxis=dict(visible=False, range=[-radio*1.5, radio*1.5], scaleanchor="x"), 
                          margin=dict(l=0,r=0,t=10,b=0), template="plotly_white")
        
        placeholder.plotly_chart(fig, use_container_width=False, key=f"v_total_{time.time()}")
        time.sleep(0.01)
