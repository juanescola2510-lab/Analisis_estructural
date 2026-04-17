import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# 1. Configuración de página
st.set_page_config(page_title="UNACEM - Control Maestro de Molienda", layout="centered")

st.title("🏭 Simulador de Molienda Avanzado")
st.subheader("Análisis de Finura y Eficiencia Energética")

# --- PANEL DE CONTROL (Barra Lateral) ---
with st.sidebar:
    st.header("⚙️ Geometría y Operación")
    radio = st.number_input("Radio del Molino (m)", value=2.0)
    largo_total = st.number_input("Largo Total (m)", value=12.0)
    rpm = st.slider("Velocidad (RPM)", 5, 50, 18)
    
    st.divider()
    st.header("📦 Cámara 1 (Impacto)")
    j1 = st.slider("Llenado J1 (%)", 0, 100, 30)
    d_bola1 = st.selectbox("Ø Bola C1 (mm)", [100, 90, 80, 60], index=1)
    
    st.divider()
    st.header("📦 Cámara 2 (Atrición)")
    j2 = st.slider("Llenado J2 (%)", 0, 100, 35)
    d_bola2 = st.selectbox("Ø Bola C2 (mm)", [40, 30, 25, 17], index=2)
    
    st.divider()
    run = st.checkbox("▶️ INICIAR SIMULACIÓN", value=True)

# --- LÓGICA DE INGENIERÍA ---
D = radio * 2
v_critica = 42.3 / np.sqrt(D) if D > 0 else 1
phi = (rpm / v_critica)

# Modelo Matemático de Finura (Blaine cm²/g)
blaine_entrada = 800
# El incremento depende exponencialmente de la superficie específica de las bolas (más pequeñas = más Blaine)
delta_c1 = (j1 * phi * (100/d_bola1)) * 10
delta_c2 = (j2 * phi * (40/d_bola2)) * 30
blaine_salida = blaine_entrada + delta_c1 + delta_c2

# Potencia y Masa
ton_total = (np.pi * radio**2 * largo_total) * ((j1+j2)/200) * 4.6
potencia_kw = 10.6 * (D**0.3) * ((j1+j2)/200) * phi * ton_total

# --- DASHBOARD DE INDICADORES ---
c1, c2, c3 = st.columns(3)
c1.metric("Finura Salida", f"{int(blaine_salida)} cm²/g", delta=f"{int(delta_c1+delta_c2)} increment")
c2.metric("Potencia Total", f"{potencia_kw:.1f} kW")
c3.metric("% Vel. Crítica", f"{phi:.1%}")

# --- MOTOR DE ANIMACIÓN Y GRÁFICO DE BARRAS ---
placeholder_sim = st.empty()
placeholder_bar = st.empty()

# Generación de partículas (limitamos a 100% para no saturar memoria)
def crear_p(j, r_m, d_b):
    n = int(min(j, 50) * 2) # Representación visual balanceada
    return np.random.uniform(r_m*0.3, r_m*0.95, n), np.random.uniform(0, 2*np.pi, n), d_b/8

r1, f1, s1 = crear_p(j1, radio, d_bola1)
r2, f2, s2 = crear_p(j2, radio, d_bola2)

g = 9.81
w = (rpm * 2 * np.pi) / 60

while run:
    t_loop = time.time()
    
    # --- 1. SIMULACIÓN VISUAL ---
    fig_sim = go.Figure()

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

    x1, y1, c1, sz1 = calc_camara(r1, f1, -radio*1.2, '#1f77b4', s1)
    x2, y2, c2, sz2 = calc_camara(r2, f2, radio*1.2, '#2ca02c', s2)

    # Dibujar Molinos (Círculos perfectos)
    t_c = np.linspace(0, 2*np.pi, 60)
    for ox in [-radio*1.2, radio*1.2]:
        fig_sim.add_trace(go.Scatter(x=radio*np.cos(t_c)+ox, y=radio*np.sin(t_c), mode='lines', line=dict(color='black', width=3), showlegend=False))

    fig_sim.add_trace(go.Scatter(x=x1, y=y1, mode='markers', marker=dict(size=sz1, color=c1, line=dict(width=0.4, color='white')), name="Cámara 1"))
    fig_sim.add_trace(go.Scatter(x=x2, y=y2, mode='markers', marker=dict(size=sz2, color=c2, line=dict(width=0.4, color='white')), name="Cámara 2"))

    fig_sim.update_layout(
        width=700, height=350,
        xaxis=dict(range=[-radio*3, radio*3], visible=False, fixedrange=True),
        yaxis=dict(range=[-radio*1.5, radio*1.5], visible=False, fixedrange=True, scaleanchor="x", scaleratio=1),
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", y=1.2, x=0.5, xanchor="center")
    )
    placeholder_sim.plotly_chart(fig_sim, use_container_width=False)

    # --- 2. GRÁFICO DE BARRAS (COMPARATIVA BLAINE) ---
    fig_bar = go.Figure(data=[
        go.Bar(name='Entrada', x=['Puzolana/Clínker'], y=[blaine_entrada], marker_color='#FFA07A'),
        go.Bar(name='Salida C1', x=['Puzolana/Clínker'], y=[blaine_entrada + delta_c1], marker_color='#1f77b4'),
        go.Bar(name='Salida Final (C2)', x=['Puzolana/Clínker'], y=[blaine_salida], marker_color='#2ca02c')
    ])
    fig_bar.update_layout(
        title="Comparativa de Finura (Blaine cm²/g)",
        barmode='group',
        height=300,
        xaxis_title="Proceso de Molienda",
        yaxis_title="Superficie Específica (Blaine)",
        margin=dict(l=50, r=50, t=50, b=50)
    )
    placeholder_bar.plotly_chart(fig_bar, use_container_width=True)

    time.sleep(0.01)

# Alertas de seguridad
if j1 > 45 or j2 > 45:
    st.error("🚨 SOBRECARGA: El llenado superior al 45% reduce la eficiencia y puede dañar el diafragma.")
