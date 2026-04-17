import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Simulador Doble Cámara UNACEM", layout="wide")

st.title("🏭 Simulador de Molienda: Molino de Dos Cámaras")
st.write("Optimización de molienda por impacto (Cámara 1) y atrición (Cámara 2).")

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.header("⚙️ Geometría General")
    radio = st.number_input("Radio del Molino (m)", value=2.0)
    largo_total = st.number_input("Largo Total (m)", value=12.0)
    rpm = st.slider("Velocidad (RPM)", 5, 45, 18)
    
    st.divider()
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.header("📦 Cámara 1")
        j1 = st.slider("Llenado J1 (%)", 15, 45, 30)
        d_bola1 = st.selectbox("Ø Bola C1 (mm)", [90, 80, 70, 60], index=1)
    with col_c2:
        st.header("📦 Cámara 2")
        j2 = st.slider("Llenado J2 (%)", 15, 45, 35)
        d_bola2 = st.selectbox("Ø Bola C2 (mm)", [40, 30, 25, 15], index=2)
    
    st.divider()
    run = st.checkbox("▶️ INICIAR PROCESO", value=True)

# --- CÁLCULOS TÉCNICOS ---
D = radio * 2
v_critica = 42.3 / np.sqrt(D) if D > 0 else 1
phi = (rpm / v_critica)

# Eficiencia basada en el diámetro de bola y velocidad
# Cámara 1 prefiere impacto (más velocidad), Cámara 2 prefiere atrición (más llenado)
ef_c1 = 100 * np.exp(-((phi - 0.75)**2) / 0.1) # Óptimo 75% Nc
ef_c2 = 100 * np.exp(-((phi - 0.68)**2) / 0.1) # Óptimo 68% Nc
ef_total = (ef_c1 + ef_c2) / 2

# Potencia estimada (Simplificada para dos cámaras)
ton_total = (np.pi * radio**2 * (largo_total/2)) * ((j1+j2)/200) * 4.6
potencia_kw = 10.6 * (D**0.3) * ((j1+j2)/200) * phi * ton_total

# --- DASHBOARD ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Eficiencia Global", f"{ef_total:.1f}%")
c2.metric("Potencia Total", f"{potencia_kw:.1f} kW")
c3.metric("Masa de Carga", f"{ton_total:.1f} TM")
c4.metric("% Vel. Crítica", f"{phi:.1%}")

# --- MOTOR DE ANIMACIÓN DUAL ---
placeholder = st.empty()

def generar_particulas(llenado, radio_m, d_bola):
    num = int(llenado * 2)
    # El tamaño visual de la partícula en el gráfico depende del diámetro real de la bola
    size_visual = d_bola / 8 
    radios = np.random.uniform(radio_m * 0.3, radio_m * 0.95, num)
    fases = np.random.uniform(0, 2*np.pi, num)
    return radios, fases, size_visual

r1, f1, s1 = generar_particulas(j1, radio, d_bola1)
r2, f2, s2 = generar_particulas(j2, radio, d_bola2)

g = 9.81
w = (rpm * 2 * np.pi) / 60

while run:
    t_loop = time.time()
    fig = go.Figure()
    
    # Creamos dos sub-gráficos en la misma figura usando coordenadas desplazadas
    def calcular_trayectoria(radios, fases, offset_x, color_base, size_v):
        x_p, y_p, colores = [], [], []
        angulo_desc = (np.pi/3) + (phi * np.pi/4)
        
        for i in range(len(radios)):
            r_i = radios[i]
            ang_i = (fases[i] + w * t_loop) % (2 * np.pi)
            
            if ang_i < angulo_desc:
                xk = r_i * np.cos(ang_i - np.pi/2)
                yk = r_i * np.sin(ang_i - np.pi/2)
                colores.append(color_base)
            else:
                t_v = (ang_i - angulo_desc) / w
                x0, y0 = r_i * np.cos(angulo_desc-np.pi/2), r_i * np.sin(angulo_desc-np.pi/2)
                vx, vy = -w * r_i * np.sin(angulo_desc-np.pi/2), w * r_i * np.cos(angulo_desc-np.pi/2)
                xk = x0 + vx * t_v * 1.2
                yk = y0 + vy * t_v - 0.5 * g * (t_v**2)
                if np.sqrt(xk**2 + yk**2) > radio:
                    xk, yk = xk * 0.85, yk * 0.85
                colores.append('#FF4500')
            
            x_p.append(xk + offset_x)
            y_p.append(yk)
        return x_p, y_p, colores, size_v

    # Cámara 1 (Izquierda)
    x1, y1, c1, sz1 = calcular_trayectoria(r1, f1, -radio*1.3, '#1f77b4', s1)
    # Cámara 2 (Derecha)
    x2, y2, c2, sz2 = calcular_trayectoria(r2, f2, radio*1.3, '#2ca02c', s2)

    # Dibujar Carcasas
    t_circ = np.linspace(0, 2*np.pi, 100)
    for off in [-radio*1.3, radio*1.3]:
        fig.add_trace(go.Scatter(x=radio*np.cos(t_circ)+off, y=radio*np.sin(t_circ), 
                                 mode='lines', line=dict(color='black', width=3), showlegend=False))

    # Añadir Bolas Cámara 1
    fig.add_trace(go.Scatter(x=x1, y=y1, mode='markers', marker=dict(size=sz1, color=c1, line=dict(width=0.5, color='white')), name="C1: Impacto"))
    # Añadir Bolas Cámara 2
    fig.add_trace(go.Scatter(x=x2, y=y2, mode='markers', marker=dict(size=sz2, color=c2, line=dict(width=0.5, color='white')), name="C2: Atrición"))

    fig.update_layout(
        width=1000, height=500,
        xaxis=dict(range=[-radio*3, radio*3], visible=False, fixedrange=True),
        yaxis=dict(range=[-radio*1.2, radio*1.2], visible=False, fixedrange=True, scaleanchor="x", scaleratio=1),
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    placeholder.plotly_chart(fig, use_container_width=True)
    time.sleep(0.01)
