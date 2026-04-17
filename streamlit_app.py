import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Simulador Avanzado UNACEM", layout="centered")

st.title("🔄 Simulador de Carga: Molino de Bolas")
st.write("Cálculos de operación y trayectoria de impacto.")

# --- BARRA LATERAL: ENTRADA DE DATOS TÉCNICOS ---
with st.sidebar:
    st.header("⚙️ Parámetros del Molino")
    radio = st.number_input("Radio del Molino (m)", value=2.0, step=0.1)
    largo = st.number_input("Largo del Molino (m)", value=6.0, step=0.5)
    st.divider()
    st.header("⚖️ Carga de Bolas")
    # El llenado se mide comúnmente por la altura de la carga (H) desde el techo
    h_vacia = st.slider("Espacio vacío desde el techo (m)", 0.1, float(radio*2), float(radio))
    densidad_bolas = st.number_input("Densidad Aparente (TM/m³)", value=4.6) # Típico para bolas de acero
    st.divider()
    rpm = st.slider("Velocidad de Rotación (RPM)", 5, 40, 15)

# --- CÁLCULOS DE INGENIERÍA ---
# 1. Porcentaje de llenado (Fórmula aproximada de Taggart)
# J = 113 - 126 * (H/D)
diametro = radio * 2
llenado_j = 113 - 126 * (h_vacia / diametro)
llenado_j = max(0, min(100, llenado_j)) # Limitar entre 0 y 100

# 2. Volumen y Tonelaje
volumen_total = np.pi * (radio**2) * largo
volumen_carga = volumen_total * (llenado_j / 100)
tonelaje_bolas = volumen_carga * densidad_bolas

# 3. Velocidad Crítica
v_critica = 42.3 / np.sqrt(diametro)
pct_v_critica = (rpm / v_critica) * 100

# --- INDICADORES ---
col1, col2, col3 = st.columns(3)
col1.metric("Llenado (J)", f"{llenado_j:.1f} %")
col2.metric("Carga de Bolas", f"{tonelaje_bolas:.1f} TM")
col3.metric("V. Crítica", f"{pct_v_critica:.1f} %")

# --- GRÁFICO DE ANIMACIÓN ---
g = 9.81
w = (rpm * 2 * np.pi) / 60
n_frames = 25
tiempos = np.linspace(0, 0.7, n_frames)
capas = [np.pi/3, np.pi/4, np.pi/6]

fig = go.Figure()

# Traza 0: Carcasa
t_circ = np.linspace(0, 2*np.pi, 100)
fig.add_trace(go.Scatter(x=radio*np.cos(t_circ), y=radio*np.sin(t_circ), mode='lines', line=dict(color='black', width=4), name='Carcasa'))

# Dibujar el nivel de la carga estática (como referencia)
y_nivel = radio - h_vacia
x_nivel = np.sqrt(max(0, radio**2 - y_nivel**2))
fig.add_trace(go.Scatter(x=[-x_nivel, x_nivel], y=[y_nivel, y_nivel], mode='lines', line=dict(color='blue', dash='dash'), name='Nivel Carga'))

# Inicialización de bolas
for ang in capas:
    x0, y0 = radio * np.cos(ang), radio * np.sin(ang)
    fig.add_trace(go.Scatter(x=[x0], y=[y0], mode='lines', line=dict(dash='dot', color='gray'), showlegend=False))
    fig.add_trace(go.Scatter(x=[x0], y=[y0], mode='markers', marker=dict(size=12, color='red'), showlegend=False))

# Frames
frames = []
for k in range(n_frames):
    frame_data = [go.Scatter(x=radio*np.cos(t_circ), y=radio*np.sin(t_circ))]
    for ang in capas:
        x0, y0 = radio * np.cos(ang), radio * np.sin(ang)
        vx, vy = -w * radio * np.sin(ang), w * radio * np.cos(ang)
        tk = tiempos[k]
        xk = x0 + vx * tk
        yk = y0 + vy * tk - 0.5 * g * tk**2
        xr = x0 + vx * tiempos[:k+1]
        yr = y0 + vy * tiempos[:k+1] - 0.5 * g * tiempos[:k+1]**2
        frame_data.append(go.Scatter(x=xr, y=yr))
        frame_data.append(go.Scatter(x=[xk], y=[yk]))
    frames.append(go.Frame(data=frame_data, name=str(k)))

fig.frames = frames
fig.update_layout(
    width=550, height=550,
    xaxis=dict(range=[-radio*1.3, radio*1.3], autorange=False, showgrid=False),
    yaxis=dict(range=[-radio*1.3, radio*1.3], autorange=False, showgrid=False),
    updatemenus=[{
        "type": "buttons",
        "buttons": [
            {"label": "▶️ PLAY", "method": "animate", "args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}]},
            {"label": "⏸️ PAUSE", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]}
        ],
        "x": 0.1, "y": -0.1
    }]
)

st.plotly_chart(fig, use_container_width=True)

# --- RECOMENDACIÓN TÉCNICA ---
st.divider()
if llenado_j < 25:
    st.error("⚠️ Llenado insuficiente: Riesgo de daño por impacto directo en blindajes.")
elif llenado_j > 45:
    st.warning("⚠️ Sobrecarga: Reducción de la eficiencia de molienda y aumento de consumo eléctrico.")
else:
    st.success("✅ Rango Óptimo: El llenado está balanceado para máxima productividad.")
