import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Simulador de Potencia UNACEM", layout="wide")

st.title("🔄 Simulador Avanzado de Molienda y Potencia")

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.header("⚙️ Geometría")
    radio = st.number_input("Radio del Molino (m)", value=2.0)
    largo = st.number_input("Largo del Molino (m)", value=6.0)
    
    st.header("⚖️ Carga de Bolas")
    h_vacia = st.slider("Espacio vacío (m)", 0.1, float(radio*2), float(radio))
    densidad_bolas = st.number_input("Densidad Aparente (TM/m³)", value=4.6)
    
    st.header("⚡ Operación")
    rpm = st.slider("Velocidad (RPM)", 5, 40, 16)

# --- CÁLCULOS TÉCNICOS ---
D = radio * 2
# 1. Porcentaje de llenado (J)
llenado_j = 113 - 126 * (h_vacia / D)
llenado_j = max(0, min(100, llenado_j))

# 2. Tonelaje de bolas
vol_total = np.pi * (radio**2) * largo
ton_bolas = vol_total * (llenado_j / 100) * densidad_bolas

# 3. CONSUMO DE ENERGÍA (Fórmula de Austin/Bond simplificada)
# La potencia depende de la carga, la velocidad y el diámetro
# P (kW) = 10.6 * D^0.3 * (J/100) * (1 - 1.03 * J/100) * (RPM/Nc) * Ton_Bolas
v_critica = 42.3 / np.sqrt(D) if D > 0 else 1
phi = rpm / v_critica
potencia_kw = 10.6 * (D**0.3) * (llenado_j/100) * (1 - 1.03 * (llenado_j/100)) * phi * ton_bolas

# --- DASHBOARD DE INDICADORES ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Llenado (J)", f"{llenado_j:.1f}%")
c2.metric("Masa de Bolas", f"{ton_bolas:.1f} TM")
c3.metric("Potencia Estimada", f"{potencia_kw:.1f} kW")
c4.metric("Vel. Crítica", f"{phi:.1%}")

# --- ANIMACIÓN DE TRAYECTORIAS MÚLTIPLES ---
g = 9.81
w = (rpm * 2 * np.pi) / 60
# Creamos 8 capas de bolas para mayor densidad
capas = np.linspace(np.pi/6, np.pi/2.5, 8) 
n_frames = 35
tiempos = np.linspace(0, 1.2, n_frames)

fig = go.Figure()

# Dibujar Carcasa
t_circ = np.linspace(0, 2*np.pi, 100)
fig.add_trace(go.Scatter(x=radio*np.cos(t_circ), y=radio*np.sin(t_circ), mode='lines', line=dict(color='black', width=4), name='Carcasa'))

# Dibujar Nivel de Carga (Estático)
y_nivel = radio - h_vacia
x_lim = np.sqrt(max(0, radio**2 - y_nivel**2))
fig.add_trace(go.Scatter(x=[-x_lim, x_lim], y=[y_nivel, y_nivel], mode='lines', line=dict(color='blue', dash='dash'), name='Nivel Carga'))

# Inicializar capas de bolas
for i, ang in enumerate(capas):
    x0, y0 = radio * np.cos(ang), radio * np.sin(ang)
    fig.add_trace(go.Scatter(x=[x0], y=[y0], mode='lines', line=dict(dash='dot', width=1, color='rgba(255,0,0,0.3)'), showlegend=False))
    fig.add_trace(go.Scatter(x=[x0], y=[y0], mode='markers', marker=dict(size=8, color='red'), showlegend=False))

# Generar Frames
frames = []
for k in range(n_frames):
    frame_data = [go.Scatter(x=radio*np.cos(t_circ), y=radio*np.sin(t_circ))] # Carcasa
    frame_data.append(go.Scatter(x=[-x_lim, x_lim], y=[y_nivel, y_nivel])) # Nivel Carga
    
    for ang in capas:
        x0, y0 = radio * np.cos(ang), radio * np.sin(ang)
        vx, vy = -w * radio * np.sin(ang), w * radio * np.cos(ang)
        tk = tiempos[k]
        
        # Trayectoria parabólica
        xk = x0 + vx * tk
        yk = y0 + vy * tk - 0.5 * g * tk**2
        
        # Rastro
        xr = x0 + vx * tiempos[:k+1]
        yr = y0 + vy * tiempos[:k+1] - 0.5 * g * tiempos[:k+1]**2
        
        frame_data.append(go.Scatter(x=xr, y=yr))
        frame_data.append(go.Scatter(x=[xk], y=[yk]))
        
    frames.append(go.Frame(data=frame_data, name=str(k)))

fig.frames = frames
fig.update_layout(
    width=700, height=600,
    xaxis=dict(range=[-radio*1.4, radio*1.4], autorange=False, showgrid=False),
    yaxis=dict(range=[-radio*1.4, radio*1.4], autorange=False, showgrid=False),
    updatemenus=[{
        "type": "buttons",
        "buttons": [
            {"label": "▶️ Simular Impacto", "method": "animate", "args": [None, {"frame": {"duration": 40, "redraw": True}}]},
            {"label": "⏸️ Pausar", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}}]}
        ],
        "x": 0.1, "y": -0.1
    }]
)

st.plotly_chart(fig, use_container_width=True)

# --- ANÁLISIS DE EFICIENCIA ---
st.divider()
st.subheader("💡 Análisis de Consumo Energético")
st.write(f"Para mover **{ton_bolas:.1f} toneladas** de acero a **{rpm} RPM**, el motor principal demanda aproximadamente **{potencia_kw:.1f} kW**.")
st.info("Esta estimación considera un molino de descarga por rebose. El consumo real puede variar según la viscosidad de la pulpa/puzolana.")
