import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# 1. Configuración de página (Sin diseño ancho para evitar distorsión)
st.set_page_config(page_title="UNACEM - Simulador Bi-Cámara", layout="centered")

st.title("🏭 Optimización de Molienda UNACEM")
st.subheader("Control de Dos Cámaras y Tamaño de Partícula")

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.header("⚙️ Geometría y Operación")
    radio = st.number_input("Radio del Molino (m)", value=2.0)
    largo_total = st.number_input("Largo Total (m)", value=12.0)
    rpm = st.slider("Velocidad (RPM)", 5, 45, 18)
    
    st.divider()
    st.header("📦 Cámara 1 (Gruesos)")
    j1 = st.slider("Llenado J1 (%)", 15, 45, 30)
    d_bola1 = st.selectbox("Ø Bola C1 (mm)", [90, 80, 60], index=1)
    
    st.divider()
    st.header("📦 Cámara 2 (Finos)")
    j2 = st.slider("Llenado J2 (%)", 15, 45, 35)
    d_bola2 = st.selectbox("Ø Bola C2 (mm)", [40, 30, 20], index=2)
    
    st.divider()
    run = st.checkbox("▶️ INICIAR PROCESO", value=True)

# --- LÓGICA TÉCNICA Y TAMAÑO DE PARTÍCULA ---
D = radio * 2
v_critica = 42.3 / np.sqrt(D) if D > 0 else 1
phi = (rpm / v_critica)

# Estimación de Tamaño de Partícula (Blaine - cm²/g)
# Basado en tiempo de residencia, energía y diámetro de bola
blaine_entrada = 800  # cm²/g (Material triturado)
# Incremento por cámara (Simplificado)
delta_c1 = (j1 * phi * (90/d_bola1)) * 15
delta_c2 = (j2 * phi * (40/d_bola2)) * 35
blaine_salida = blaine_entrada + delta_c1 + delta_c2

# Potencia (kW)
ton_total = (np.pi * radio**2 * largo_total) * ((j1+j2)/200) * 4.6
potencia_kw = 10.6 * (D**0.3) * ((j1+j2)/200) * phi * ton_total

# --- DASHBOARD DE RESULTADOS ---
c1, c2, c3 = st.columns(3)
c1.metric("Finura Salida (Blaine)", f"{int(blaine_salida)} cm²/g", delta=f"{int(delta_c1+delta_c2)} increment")
c2.metric("Potencia Total", f"{potencia_kw:.1f} kW")
c3.metric("% Vel. Crítica", f"{phi:.1%}")

# --- MOTOR DE ANIMACIÓN ANTI-DISTORSIÓN ---
placeholder = st.empty()

# Generación de partículas
def crear_p(j, r_m, d_b):
    n = int(j * 1.5)
    return np.random.uniform(r_m*0.3, r_m*0.95, n), np.random.uniform(0, 2*np.pi, n), d_b/8

r1, f1, s1 = crear_p(j1, radio, d_bola1)
r2, f2, s2 = crear_p(j2, radio, d_bola2)

g = 9.81
w = (rpm * 2 * np.pi) / 60

while run:
    t_loop = time.time()
    fig = go.Figure()

    def calc_camara(radios, fases, off_x, col, sz):
        xp, yp, colors = [], [], []
        ang_desc = (np.pi/3) + (phi * np.pi/4)
        for i in range(len(radios)):
            ri, ai = radios[i], (fases[i] + w * t_loop) % (2*np.pi)
            if ai < ang_desc:
                xk, yk = ri * np.cos(ai-np.pi/2), ri * np.sin(ai-np.pi/2)
                colors.append(col)
            else:
                tv = (ai - ang_desc) / w
                x0, y0 = ri*np.cos(ang_desc-np.pi/2), ri*np.sin(ang_desc-np.pi/2)
                vx, vy = -w*ri*np.sin(ang_desc-np.pi/2), w*ri*np.cos(ang_desc-np.pi/2)
                xk, yk = x0 + vx*tv*1.2, y0 + vy*tv - 0.5*g*(tv**2)
                if np.sqrt(xk**2 + yk**2) > radio: xk, yk = xk*0.85, yk*0.85
                colors.append('#FF4500')
            xp.append(xk + off_x); yp.append(yk)
        return xp, yp, colors, sz

    # Datos Cámaras
    x1, y1, c1, sz1 = calc_camara(r1, f1, -radio*1.2, '#1f77b4', s1)
    x2, y2, c2, sz2 = calc_camara(r2, f2, radio*1.2, '#2ca02c', s2)

    # Dibujar Carcasas
    t_c = np.linspace(0, 2*np.pi, 60)
    for ox in [-radio*1.2, radio*1.2]:
        fig.add_trace(go.Scatter(x=radio*np.cos(t_c)+ox, y=radio*np.sin(t_c), mode='lines', line=dict(color='black', width=3), showlegend=False))

    fig.add_trace(go.Scatter(x=x1, y=y1, mode='markers', marker=dict(size=sz1, color=c1, line=dict(width=0.4, color='white')), name="C1: Impacto"))
    fig.add_trace(go.Scatter(x=x2, y=y2, mode='markers', marker=dict(size=sz2, color=c2, line=dict(width=0.4, color='white')), name="C2: Atrición"))

    # FIX DE DISTORSIÓN: Forzamos escala absoluta
    fig.update_layout(
        width=800, height=400,
        xaxis=dict(range=[-radio*3, radio*3], visible=False, fixedrange=True),
        yaxis=dict(range=[-radio*1.5, radio*1.5], visible=False, fixedrange=True, scaleanchor="x", scaleratio=1),
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(orientation="h", y=1.1)
    )

    placeholder.plotly_chart(fig, use_container_width=False) # IMPORTANTE: False para evitar óvalos
    time.sleep(0.01)
