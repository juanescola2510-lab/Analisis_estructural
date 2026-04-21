import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

st.set_page_config(page_title="Simulador Horno Industrial 360", layout="wide")

st.title("🌀 Visualizador Térmico de Horno Cilíndrico")
st.markdown("Simulación de distribución de calor en sección transversal.")

# --- BARRA LATERAL ---
st.sidebar.header("📐 Dimensiones")
r_int = st.sidebar.slider("Radio Interior (cm)", 10, 80, 30)
espesor = st.sidebar.slider("Espesor Refractario (cm)", 5, 40, 15)
k_ref = st.sidebar.slider("Conductividad (k) W/m·K", 0.1, 2.0, 1.1)

temp_int = 1500
temp_amb = 25
r_ext = r_int + espesor

# --- CÁLCULOS ---
# Resistencia radial simplificada para cálculo de temp. exterior
resistencia = np.log(r_ext/r_int) / (2 * np.pi * k_ref)
q_per_meter = (temp_int - temp_amb) / resistencia
t_chapa = temp_amb + (q_per_meter * 0.01) # Estimación de cara externa

# --- VISUALIZACIÓN ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Perfil de Temperatura")
    # Generar datos para la curva
    r_coords = np.linspace(r_int, r_ext, 100)
    t_coords = temp_int - (temp_int - t_chapa) * (np.log(r_coords/r_int) / np.log(r_ext/r_int))
    
    fig1, ax1 = plt.subplots()
    ax1.plot(r_coords, t_coords, color='red', lw=3)
    ax1.set_xlabel("Radio (cm)")
    ax1.set_ylabel("Temperatura (°C)")
    ax1.grid(True, alpha=0.3)
    st.pyplot(fig1)

with col2:
    st.subheader("⭕ Sección Transversal (Calor)")
    
    # Crear malla polar para el círculo
    theta = np.linspace(0, 2*np.pi, 100)
    r_grid, theta_grid = np.meshgrid(r_coords, theta)
    
    # Calcular temperaturas para cada punto de la malla
    t_grid = temp_int - (temp_int - t_chapa) * (np.log(r_grid/r_int) / np.log(r_ext/r_int))
    
    # Convertir a coordenadas cartesianas para graficar
    X = r_grid * np.cos(theta_grid)
    Y = r_grid * np.sin(theta_grid)
    
    fig2, ax2 = plt.subplots(figsize=(6,6))
    # Dibujar el mapa de calor
    cont = ax2.pcolormesh(X, Y, t_grid, cmap='inferno', shading='auto')
    plt.colorbar(cont, label="Temperatura °C")
    
    # Dibujar límites
    circ_int = plt.Circle((0,0), r_int, color='white', fill=False, linestyle='--')
    circ_ext = plt.Circle((0,0), r_ext, color='cyan', fill=False, lw=2)
    ax2.add_artist(circ_int)
    ax2.add_artist(circ_ext)
    
    ax2.set_aspect('equal')
    ax2.axis('off')
    st.pyplot(fig2)

# --- PANEL DE ALERTAS ---
st.divider()
st_col1, st_col2, st_col3 = st.columns(3)

with st_col1:
    st.metric("T° Cara Interna", f"{temp_int}°C")
with st_col2:
    st.metric("T° Cara Externa (Chapa)", f"{t_chapa:.1f}°C")
with st_col3:
    if t_chapa > 120:
        st.error("❌ RIESGO: Temperatura de chapa muy alta.")
    elif t_chapa > 70:
        st.warning("⚠️ PRECAUCIÓN: Superficie caliente.")
    else:
        st.success("✅ Diseño térmico seguro.")

st.info(f"""
    **Interpretación Visual:** 
    - El centro blanco/amarillo representa los **{temp_int}°C** de la llama.
    - El degradado hacia el negro/púrpura muestra cómo el **refractario absorbe y frena el calor**.
    - La línea azul exterior es tu **chapa metálica**, protegida por el espesor de {espesor} cm.
""")
