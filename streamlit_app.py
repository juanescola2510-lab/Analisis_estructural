import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# Configuración de la página
st.set_page_config(page_title="Simulador de Eficiencia UNACEM", layout="wide")

st.title("🧩 Simulador de Eficiencia de Molienda - v3.1")

# --- PANEL DE CONTROL (Barra Lateral) ---
with st.sidebar:
    st.header("⚙️ Especificaciones Técnicas")
    radio = st.number_input("Radio del Molino (m)", value=2.0, min_value=0.5)
    largo = st.number_input("Largo del Molino (m)", value=6.0, min_value=1.0)
    st.divider()
    st.header("📊 Parámetros de Operación")
    llenado_j = st.slider("Llenado de Bolas (J %)", 15, 45, 32)
    rpm = st.slider("Velocidad (RPM)", 5, 45, 18)
    st.divider()
    costo_kwh = st.number_input("Costo Energía (USD/kWh)", value=0.09)
    run = st.checkbox("▶️ INICIAR PROCESO", value=True)

# --- CÁLCULOS TÉCNICOS ---
D = radio * 2
v_critica = 42.3 / np.sqrt(D) if D > 0 else 1
phi = (rpm / v_critica)

# Eficiencia de molienda (Curva de Gauss optimizada al 72% de Nc)
eficiencia = 100 * np.exp(-((phi - 0.72)**2) / (2 * 0.15**2))
eficiencia = max(0, min(100, eficiencia))

# Masa de bolas (Densidad acero 4.6 TM/m3)
ton_bolas = (np.pi * radio**2 * largo) * (llenado_j/100) * 4.6
# Potencia (kW) según fórmula de Austin
potencia_kw = 10.6 * (D**0.3) * (llenado_j/100) * (1 - 1.03 * (llenado_j/100)) * phi * ton_bolas
costo_hora = potencia_kw * costo_kwh

# --- DASHBOARD DE INDICADORES ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Eficiencia", f"{eficiencia:.1f}%")
c2.metric("Potencia Motor", f"{potencia_kw:.1f} kW")
c3.metric("Costo Operativo", f"${costo_hora:.2f}/h")
c4.metric("% Vel. Crítica", f"{phi:.1%}")

# --- MOTOR DE ANIMACIÓN ---
placeholder = st.empty()
g = 9.81
w = (rpm * 2 * np.pi) / 60

# Partículas aleatorias para realismo visual
num_particulas = int(llenado_j * 3) 
radios_p = np.random.uniform(radio * 0.3, radio * 0.96, num_particulas)
fases_p = np.random.uniform(0, 2*np.pi, num_particulas)

while run:
    t_loop = time.time()
    fig = go.Figure()
    
    # 1. Dibujar Carcasa (Círculo Negro)
    t_circ = np.linspace(0, 2*np.pi, 100)
    fig.add_trace(go.Scatter(x=radio*np.cos(t_circ), y=radio*np.sin(t_circ), 
                             mode='lines', line=dict(color='#222', width=8), showlegend=False))
    
    # 2. Lógica de Movimiento de Partículas
    x_p, y_p, colores, tamaños = [], [], [], []
    angulo_desc = (np.pi/3) + (phi * np.pi/4) # El desprendimiento sube con las RPM

    for i in range(num_particulas):
        r_i = radios_p[i]
        ang_i = (fases_p[i] + w * t_loop) % (2 * np.pi)
        
        if ang_i < angulo_desc:
            # Subida por fricción
            xk = r_i * np.cos(ang_i - np.pi/2)
            yk = r_i * np.sin(ang_i - np.pi/2)
            colores.append('#8B0000') # Rojo oscuro
            tamaños.append(7)
        else:
            # Caída en catarata
            t_v = (ang_i - angulo_desc) / w
            x0, y0 = r_i * np.cos(angulo_desc-np.pi/2), r_i * np.sin(angulo_desc-np.pi/2)
            vx, vy = -w * r_i * np.sin(angulo_desc-np.pi/2), w * r_i * np.cos(angulo_desc-np.pi/2)
            
            xk = x0 + vx * t_v * 1.3
            yk = y0 + vy * t_v - 0.5 * g * (t_v**2)
            
            # Limitar impacto dentro de la carcasa
            if np.sqrt(xk**2 + yk**2) > radio:
                xk, yk = xk * 0.85, yk * 0.85 # Rebote hacia el lecho
                colores.append('#FFA500') # Naranja impacto
                tamaños.append(11)
            else:
                colores.append('#FF0000') # Rojo brillante
                tamaños.append(9)
        
        x_p.append(xk)
        y_p.append(yk)

    fig.add_trace(go.Scatter(x=x_p, y=y_p, mode='markers', 
                             marker=dict(color=colores, size=tamaños, opacity=0.8,
                                         line=dict(width=0.5, color='white')), 
                             showlegend=False))

    # --- CORRECCIÓN DE LA GEOMETRÍA (Evita el óvalo) ---
    fig.update_layout(
        width=600, height=600,
        xaxis=dict(range=[-radio*1.3, radio*1.3], visible=False, fixedrange=True),
        yaxis=dict(range=[-radio*1.3, radio*1.3], visible=False, fixedrange=True,
                   scaleanchor="x", scaleratio=1), # Relación 1:1 obligatoria
        template="plotly_white",
        margin=dict(l=10, r=10, t=10, b=10)
    )

    placeholder.plotly_chart(fig, use_container_width=False)
    time.sleep(0.01)

if not run:
    st.info("🔄 Simulación pausada. Ajusta los parámetros para reanudar.")
