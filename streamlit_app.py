import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# 1. Configuración de página
st.set_page_config(page_title="UNACEM - Simulador de Molienda Total", layout="centered")

st.title("🏭 Simulador Maestro de Molienda")
st.subheader("Cámaras, Reductor y Control de Finura (Blaine)")

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.header("⚙️ Configuración Mecánica")
    radio = st.number_input("Radio del Molino (m)", value=2.0)
    largo_total = st.number_input("Largo Total (m)", value=12.0)
    rpm_molino = st.slider("Velocidad Molino (RPM)", 5, 50, 18)
    
    st.divider()
    st.header("⚙️ Reductor")
    eficiencia_red = st.slider("Eficiencia Reductor (%)", 90, 99, 96) / 100
    rpm_motor = st.number_input("RPM Motor Eléctrico", value=1180)
    
    st.divider()
    st.header("📦 Cámara 1 (Gruesos)")
    j1 = st.slider("Llenado J1 (%)", 0, 100, 30)
    d_bola1 = st.selectbox("Ø Bola C1 (mm)", [90, 80, 60], index=1)
    
    st.divider()
    st.header("📦 Cámara 2 (Finos)")
    j2 = st.slider("Llenado J2 (%)", 0, 100, 35)
    d_bola2 = st.selectbox("Ø Bola C2 (mm)", [40, 30, 20], index=1)
    
    run = st.checkbox("▶️ INICIAR SIMULACIÓN", value=True)

# --- LÓGICA DE INGENIERÍA ---
D = radio * 2
v_critica = 42.3 / np.sqrt(D) if D > 0 else 1
phi = (rpm_molino / v_critica)

# 1. Cálculos de Potencia y Torque
ton_total = (np.pi * radio**2 * largo_total) * ((j1+j2)/200) * 4.6
potencia_eje = 10.6 * (D**0.3) * ((j1+j2)/200) * phi * ton_total
potencia_motor = potencia_eje / eficiencia_red
torque_molino = (9550 * potencia_eje) / rpm_molino if rpm_molino > 0 else 0

# 2. Modelo de Finura (Blaine)
blaine_entrada = 800
delta_c1 = (j1 * phi * (100/d_bola1)) * 10
delta_c2 = (j2 * phi * (40/d_bola2)) * 30
blaine_salida = blaine_entrada + delta_c1 + delta_c2

# --- DASHBOARD DE INDICADORES ---
c1, c2, c3 = st.columns(3)
c1.metric("Finura (Blaine)", f"{int(blaine_salida)} cm²/g", f"+{int(delta_c1+delta_c2)}")
c2.metric("Potencia Motor", f"{potencia_motor:.1f} kW", f"{potencia_motor-potencia_eje:.1f} Pérdida")
c3.metric("Torque en Eje", f"{int(torque_molino):,} Nm")

# --- MOTOR DE ANIMACIÓN ---
placeholder_sim = st.empty()
placeholder_bar = st.empty()

def crear_p(j, r_m, d_b):
    n = int(min(j, 35) * 2) 
    return np.random.uniform(r_m*0.3, r_m*0.95, n), np.random.uniform(0, 2*np.pi, n), d_b/8

r1, f1, s1 = crear_p(j1, radio, d_bola1)
r2, f2, s2 = crear_p(j2, radio, d_bola2)

g, w = 9.81, (rpm_molino * 2 * np.pi) / 60
iteracion = 0

while run:
    t_loop = time.time()
    iteracion += 1
    
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

    # Datos Visuales
    x1, y1, c1, sz1 = calc_camara(r1, f1, -radio*1.2, '#1f77b4', s1)
    x2, y2, c2, sz2 = calc_camara(r2, f2, radio*1.2, '#2ca02c', sz=d_bola2/8)

    # Dibujar Molinos
    t_c = np.linspace(0, 2*np.pi, 60)
    for ox in [-radio*1.2, radio*1.2]:
        fig_sim.add_trace(go.Scatter(x=radio*np.cos(t_c)+ox, y=radio*np.sin(t_c), mode='lines', line=dict(color='black', width=4), showlegend=False))

    fig_sim.add_trace(go.Scatter(x=x1, y=y1, mode='markers', marker=dict(size=sz1, color=c1, line=dict(width=0.4, color='white')), showlegend=False))
    fig_sim.add_trace(go.Scatter(x=x2, y=y2, mode='markers', marker=dict(size=sz2, color=c2, line=dict(width=0.4, color='white')), showlegend=False))

    fig_sim.update_layout(
        width=700, height=350,
        xaxis=dict(range=[-radio*3, radio*3], visible=False, fixedrange=True),
        yaxis=dict(range=[-radio*1.5, radio*1.5], visible=False, fixedrange=True, scaleanchor="x", scaleratio=1),
        margin=dict(l=0, r=0, t=10, b=0), template="plotly_white"
    )
    placeholder_sim.plotly_chart(fig_sim, use_container_width=False, key=f"sim_{iteracion}")

    # --- 2. GRÁFICO DE BARRAS BLAINE ---
    fig_bar = go.Figure(data=[
        go.Bar(name='Entrada', x=['Puzolana'], y=[blaine_entrada], marker_color='#FFA07A'),
        go.Bar(name='Cámara 1', x=['Puzolana'], y=[blaine_entrada + delta_c1], marker_color='#1f77b4'),
        go.Bar(name='Salida Final', x=['Puzolana'], y=[blaine_salida], marker_color='#2ca02c')
    ])
    fig_bar.update_layout(height=300, barmode='group', title="Evolución de la Finura (Blaine)", template="plotly_white")
    placeholder_bar.plotly_chart(fig_bar, use_container_width=True, key=f"bar_{iteracion}")

    time.sleep(0.01)
