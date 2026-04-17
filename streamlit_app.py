import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Simulador de Confiabilidad UNACEM", layout="wide")

st.title("🧩 Simulador de Eficiencia de Molienda - v3.0")

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.header("⚙️ Especificaciones Técnicas")
    radio = st.number_input("Radio del Molino (m)", value=2.0)
    largo = st.number_input("Largo del Molino (m)", value=6.0)
    st.divider()
    st.header("📊 Parámetros de Operación")
    llenado_j = st.slider("Llenado de Bolas (J %)", 15, 45, 32)
    rpm = st.slider("Velocidad (RPM)", 5, 45, 18)
    st.divider()
    run = st.checkbox("▶️ INICIAR PROCESO", value=True)

# --- CÁLCULOS TÉCNICOS ---
D = radio * 2
v_critica = 42.3 / np.sqrt(D) if D > 0 else 1
phi = (rpm / v_critica)

# Cálculo de Eficiencia de Molienda (Basado en el ángulo de impacto)
# La eficiencia máxima ocurre cerca del 70-75% de la velocidad crítica
eficiencia = 100 * (1 - abs(phi - 0.72) / 0.5) 
eficiencia = max(0, min(100, eficiencia))

# Potencia (kW)
ton_bolas = (np.pi * radio**2 * largo) * (llenado_j/100) * 4.6
potencia_kw = 10.6 * (D**0.3) * (llenado_j/100) * (1 - 1.03 * (llenado_j/100)) * phi * ton_bolas

# --- DASHBOARD ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Eficiencia de Molienda", f"{eficiencia:.1f}%")
c2.metric("Potencia Motor", f"{potencia_kw:.1f} kW")
c3.metric("Masa de Carga", f"{ton_bolas:.1f} TM")
c4.metric("% Vel. Crítica", f"{phi:.1%}")

# --- MOTOR DE ANIMACIÓN REALISTA ---
placeholder = st.empty()
g = 9.81
w = (rpm * 2 * np.pi) / 60

# Generar partículas de carga (Bolas + Material)
num_particulas = int(llenado_j * 2.5) 
radios_p = np.random.uniform(radio * 0.4, radio * 0.96, num_particulas)
fases_p = np.random.uniform(0, np.pi, num_particulas)

t = 0
while run:
    t += 0.08
    fig = go.Figure()
    
    # 1. Dibujar Carcasa y Blindajes (Simulados con líneas)
    t_circ = np.linspace(0, 2*np.pi, 100)
    fig.add_trace(go.Scatter(x=radio*np.cos(t_circ), y=radio*np.sin(t_circ), 
                             mode='lines', line=dict(color='#333', width=6), showlegend=False))
    
    # 2. Lógica de Movimiento: Catarata + Cascada
    x_p, y_p, colores, tamaños = [], [], [], []
    
    # Ángulo de desprendimiento dinámico según RPM
    angulo_desc = (np.pi/3) + (phi * np.pi/4)

    for i in range(num_particulas):
        r_i = radios_p[i]
        ang_i = (fases_p[i] + w * t) % (2 * np.pi)
        
        if ang_i < angulo_desc:
            # FASE ASCENDENTE (Pegada a los blindajes)
            xk = r_i * np.cos(ang_i - np.pi/2)
            yk = r_i * np.sin(ang_i - np.pi/2)
            colores.append('#8B0000') # Rojo oscuro (Bolas subiendo)
            tamaños.append(8)
        else:
            # FASE DE VUELO (Parábola de impacto)
            t_v = (ang_i - angulo_desc) / w
            x0 = r_i * np.cos(angulo_desc - np.pi/2)
            y0 = r_i * np.sin(angulo_desc - np.pi/2)
            vx = -w * r_i * np.sin(angulo_desc - np.pi/2)
            vy = w * r_i * np.cos(angulo_desc - np.pi/2)
            
            xk = x0 + vx * t_v * 1.5
            yk = y0 + vy * t_v - 0.5 * g * (t_v**2)
            
            # Lógica de impacto en el pie de carga
            dist_r = np.sqrt(xk**2 + yk**2)
            if dist_r > radio:
                # Rebote visual hacia el centro
                xk, yk = xk * 0.8, yk * 0.8
                colores.append('#FF4500') # Naranja (Impacto)
                tamaños.append(12)
            else:
                colores.append('#FF0000') # Rojo brillante (Vuelo)
                tamaños.append(9)
        
        x_p.append(xk)
        y_p.append(yk)

    # 3. Dibujar partículas con estilo 3D (Markers con bordes)
    fig.add_trace(go.Scatter(x=x_p, y=y_p, mode='markers', 
                             marker=dict(color=colores, size=tamaños, 
                                         line=dict(width=0.5, color='white'),
                                         opacity=0.8), 
                             showlegend=False))

    fig.update_layout(width=700, height=700, 
                      xaxis=dict(range=[-radio*1.2, radio*1.2], visible=False),
                      yaxis=dict(range=[-radio*1.2, radio*1.2], visible=False),
                      template="plotly_white",
                      margin=dict(l=0, r=0, t=0, b=0))

    placeholder.plotly_chart(fig, use_container_width=True)
    time.sleep(0.01)

if not run:
    st.warning("⚠️ Sistema en Parada de Mantenimiento. Activa el check para reiniciar.")
