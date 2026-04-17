import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Simulador Rotativo UNACEM", layout="wide")

st.title("🔄 Simulación de Molino Rotativo")
st.write("Las bolas giran con la carcasa y caen según la velocidad de rotación.")

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    radio = st.number_input("Radio del Molino (m)", value=2.0)
    largo = st.number_input("Largo del Molino (m)", value=6.0)
    st.header("⚖️ Carga")
    h_vacia = st.slider("Espacio vacío (m)", 0.1, float(radio*2), 2.2)
    densidad_bolas = st.number_input("Densidad (TM/m³)", value=4.6)
    st.header("⚡ Operación")
    rpm = st.slider("Velocidad (RPM)", 5, 40, 18)

# --- CÁLCULOS DE INGENIERÍA ---
D = radio * 2
llenado_j = 113 - 126 * (h_vacia / D)
llenado_j = max(0, min(100, llenado_j))
ton_bolas = (np.pi * radio**2 * largo) * (llenado_j/100) * densidad_bolas

# Potencia estimada (kW)
v_critica = 42.3 / np.sqrt(D) if D > 0 else 1
phi = rpm / v_critica
potencia_kw = 10.6 * (D**0.3) * (llenado_j/100) * (1 - 1.03 * (llenado_j/100)) * phi * ton_bolas

# --- DASHBOARD ---
c1, c2, c3 = st.columns(3)
c1.metric("Llenado (J)", f"{llenado_j:.1f}%")
c2.metric("Masa Total", f"{ton_bolas:.1f} TM")
c3.metric("Consumo Motor", f"{potencia_kw:.1f} kW")

# --- LÓGICA DE ANIMACIÓN ROTATIVA ---
g = 9.81
w = (rpm * 2 * np.pi) / 60
n_frames = 40
t_total = np.linspace(0, 2, n_frames) # Tiempo de la animación

# Definimos 10 capas de bolas en diferentes radios para llenar el fondo
radios_capas = np.linspace(radio * 0.7, radio * 0.98, 8)
angulos_base = np.linspace(-np.pi/2, 0, 8) 

fig = go.Figure()

# 1. Función para calcular posición
def calcular_pos_bola(t, r_capa, ang_base):
    # Ángulo de desprendimiento teórico (cos(alpha) = w^2 * r / g)
    # Si la velocidad es alta, la bola se desprende más arriba
    cos_alpha = (w**2 * r_capa) / g
    ang_desprendimiento = np.arccos(min(1, cos_alpha))
    
    # Tiempo que tarda en llegar al punto de desprendimiento
    ang_actual = ang_base + (w * t)
    
    if ang_actual < ang_desprendimiento:
        # FASE 1: La bola gira pegada a la carcasa
        xk = r_capa * np.cos(ang_actual)
        yk = r_capa * np.sin(ang_actual)
        return xk, yk, True
    else:
        # FASE 2: Caída parabólica (proyectil interior)
        t_caida = (ang_actual - ang_desprendimiento) / w
        x0 = r_capa * np.cos(ang_desprendimiento)
        y0 = r_capa * np.sin(ang_desprendimiento)
        vx = -w * r_capa * np.sin(ang_desprendimiento)
        vy = w * r_capa * np.cos(ang_desprendimiento)
        
        xk = x0 + vx * t_caida
        yk = y0 + vy * t_caida - 0.5 * g * t_caida**2
        
        # Si choca con el fondo del molino (r > radio), se detiene
        if np.sqrt(xk**2 + yk**2) > radio:
            xk = xk * (radio/np.sqrt(xk**2 + yk**2))
            yk = yk * (radio/np.sqrt(xk**2 + yk**2))
            
        return xk, yk, False

# --- CONSTRUCCIÓN DE FRAMES ---
frames = []
t_circ = np.linspace(0, 2*np.pi, 100)

for k in range(n_frames):
    data = []
    # Carcasa giratoria (añadimos una marca para ver que gira)
    ang_giro = w * t_total[k]
    data.append(go.Scatter(x=radio*np.cos(t_circ), y=radio*np.sin(t_circ), mode='lines', line=dict(color='black', width=4)))
    # Marca de rotación en la carcasa
    data.append(go.Scatter(x=[radio*np.cos(ang_giro)], y=[radio*np.sin(ang_giro)], mode='markers', marker=dict(color='black', size=10)))
    
    for i, r_c in enumerate(radios_capas):
        xk, yk, en_pared = calcular_pos_bola(t_total[k], r_c, angulos_base[i])
        color = 'red' if not en_pared else 'darkred'
        data.append(go.Scatter(x=[xk], y=[yk], mode='markers', marker=dict(color=color, size=10), showlegend=False))
        
    frames.append(go.Frame(data=data, name=str(k)))

# Inicialización
fig.add_trace(go.Scatter(x=radio*np.cos(t_circ), y=radio*np.sin(t_circ), mode='lines', line=dict(color='black', width=4)))

fig.frames = frames
fig.update_layout(
    width=700, height=700,
    xaxis=dict(range=[-radio*1.2, radio*1.2], autorange=False, showgrid=False),
    yaxis=dict(range=[-radio*1.2, radio*1.2], autorange=False, showgrid=False),
    updatemenus=[{
        "type": "buttons",
        "buttons": [
            {"label": "▶️ Iniciar Giro", "method": "animate", "args": [None, {"frame": {"duration": 50, "redraw": True}}]},
            {"label": "⏸️ Pausar", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}}]}
        ],
        "x": 0.1, "y": -0.1
    }]
)

st.plotly_chart(fig, use_container_width=True)

st.divider()
st.info("""
**Interpretación de Mantenimiento:**
- **Bolas en Rojo Oscuro:** Están subiendo con la carcasa (fricción).
- **Bolas en Rojo Brillante:** Están en fase de vuelo (impacto).
- Si la velocidad es muy baja, verás un efecto de 'cascada' (poca caída). Si es óptima, verás la 'catarata' golpeando el pie de la carga.
""")
