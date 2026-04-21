import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulador Horno Pro - Termodinámica Radial", layout="wide")

# --- BASE DE DATOS DE MATERIALES ---
materiales = {
    "Ladrillo de Magnesita (Alta T°)": {"k": 3.5, "densidad": 2800},
    "Ladrillo de Alúmina (Estándar)": {"k": 1.5, "densidad": 2500},
    "Ladrillo de Sílice": {"k": 1.1, "densidad": 2200},
    "Ladrillo Refractario Aislante": {"k": 0.3, "densidad": 800},
    "Fibra Cerámica (Manta)": {"k": 0.12, "densidad": 128}
}

st.title("🏗️ Simulador Térmico Radial de Horno Industrial")
st.markdown("Cálculo de transferencia de calor en cilindros con resistencia convectiva externa.")

# --- BARRA LATERAL: ENTRADAS ---
st.sidebar.header("📐 Geometría y Estructura")
diam_int_cm = st.sidebar.number_input("Diámetro Interior del Horno (cm)", value=60.0)
largo_m = st.sidebar.number_input("Largo total del Horno (m)", value=3.0)
espesor_ref_cm = st.sidebar.slider("Espesor del Refractario (cm)", 5, 50, 15)
espesor_chapa_mm = st.sidebar.slider("Espesor de la Chapa de Acero (mm)", 2, 25, 6)

st.sidebar.header("🧱 Propiedades del Material")
tipo_ref = st.sidebar.selectbox("Selecciona Material Refractario:", list(materiales.keys()))
k_ref = materiales[tipo_ref]["k"]
densidad_ref = materiales[tipo_ref]["densidad"]

st.sidebar.header("🌬️ Condiciones Ambientales")
temp_int = 1500 # Temperatura de la llama
temp_amb = 25   # Temperatura ambiente
viento = st.sidebar.select_slider("Ventilación externa", options=["Nula (Aire calmo)", "Baja", "Media", "Alta"])
# Mapeo de coeficiente de convección (W/m²K)
h_map = {"Nula (Aire calmo)": 5, "Baja": 15, "Media": 30, "Alta": 50}
h_aire = h_map[viento]

# --- CÁLCULOS FÍSICOS (ESTADO ESTACIONARIO RADIAL) ---
r1 = (diam_int_cm / 2) / 100
r2 = r1 + (espesor_ref_cm / 100)
r3 = r2 + (espesor_chapa_mm / 1000)
k_acero = 50.0 # W/mK

# 1. Resistencia Refractario: ln(r2/r1) / (2 * pi * k * L)
R_ref = np.log(r2/r1) / (2 * np.pi * k_ref * largo_m)
# 2. Resistencia Chapa Acero
R_chapa = np.log(r3/r2) / (2 * np.pi * k_acero * largo_m)
# 3. Resistencia Convectiva Aire (Evita que la chapa marque siempre 25°C)
R_conv = 1 / (h_aire * (2 * np.pi * r3 * largo_m))

R_total = R_ref + R_chapa + R_conv

# Flujo de calor (Watts)
Q = (temp_int - temp_amb) / R_total

# Cálculo de temperaturas en las interfaces
t_pared_interna_chapa = temp_int - (Q * R_ref)
t_exterior_chapa = t_pared_interna_chapa - (Q * R_chapa)

# Peso
vol_ref = np.pi * (r2**2 - r1**2) * largo_m
peso_total = vol_ref * densidad_ref

# --- INTERFAZ DE RESULTADOS ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("T° Exterior Chapa", f"{t_exterior_chapa:.1f} °C")
c2.metric("Pérdida de Calor", f"{Q/1000:.2f} kW")
c3.metric("Peso Refractario", f"{peso_total:.0f} kg")
c4.metric("T° Interfaz Ref/Chapa", f"{t_pared_interna_chapa:.1f} °C")

# --- GRÁFICOS ---
col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader("📈 Perfil Logarítmico de Temperatura")
    radios_plot = np.linspace(r1, r3, 100)
    t_plot = []
    for r in radios_plot:
        if r <= r2:
            # Perfil dentro del refractario
            temp = temp_int - (temp_int - t_pared_interna_chapa) * (np.log(r/r1) / np.log(r2/r1))
        else:
            # Perfil dentro de la chapa de acero
            temp = t_pared_interna_chapa - (t_pared_interna_chapa - t_exterior_chapa) * (np.log(r/r2) / np.log(r3/r2))
        t_plot.append(temp)
    
    fig1, ax1 = plt.subplots()
    ax1.plot(radios_plot * 100, t_plot, color='red', lw=3, label='Gradiente Térmico')
    ax1.axvspan(r1*100, r2*100, color='orange', alpha=0.15, label='Zona Refractaria')
    ax1.axvspan(r2*100, r3*100, color='blue', alpha=0.2, label='Chapa de Acero')
    ax1.set_xlabel("Distancia desde el centro (cm)")
    ax1.set_ylabel("Temperatura (°C)")
    ax1.legend()
    st.pyplot(fig1)

with col_der:
    st.subheader("⭕ Mapa de Calor Circular")
    theta = np.linspace(0, 2*np.pi, 60)
    r_vals = np.linspace(r1, r3, 30)
    T_mesh = np.zeros((len(theta), len(r_vals)))
    
    for i, r in enumerate(r_vals):
        if r <= r2:
            T_val = temp_int - (temp_int - t_pared_interna_chapa) * (np.log(r/r1) / np.log(r2/r1))
        else:
            T_val = t_pared_interna_chapa - (t_pared_interna_chapa - t_exterior_chapa) * (np.log(r/r2) / np.log(r3/r2))
        T_mesh[:, i] = T_val

    fig2, ax2 = plt.subplots(figsize=(6,6), subplot_kw={'projection': 'polar'})
    T_mesh_plot = ax2.pcolormesh(theta, r_vals*100, T_mesh.T, cmap='inferno', shading='auto')
    plt.colorbar(T_mesh_plot, label="Temperatura °C", pad=0.1)
    ax2.set_yticklabels([]) 
    st.pyplot(fig2)

# --- VALIDACIÓN DE SEGURIDAD ---
if t_exterior_chapa > 140:
    st.error("🚨 CRÍTICO: La chapa exterior supera los 140°C. Riesgo inminente de falla estructural o accidentes.")
elif t_exterior_chapa > 60:
    st.warning("⚠️ PRECAUCIÓN: Superficie caliente. Se requiere guarda de seguridad.")
else:
    st.success("✅ Diseño térmico dentro de parámetros de contacto seguro.")
