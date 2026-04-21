import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulador de Horno Industrial Pro", layout="wide")

# --- BASE DE DATOS DE MATERIALES ---
materiales = {
    "Ladrillo de Magnesita (Alta T°)": {"k": 3.5, "desc": "Excelente para 1500°C+, pero conduce mucho calor."},
    "Ladrillo de Alúmina (Estándar)": {"k": 1.5, "desc": "Equilibrio entre resistencia y aislamiento."},
    "Ladrillo de Sílice": {"k": 1.1, "desc": "Usado en hornos de vidrio y acero."},
    "Ladrillo Refractario Aislante": {"k": 0.3, "desc": "Baja resistencia mecánica, alto aislamiento."},
    "Fibra Cerámica (Manta)": {"k": 0.12, "desc": "Máximo aislamiento, pero muy frágil."}
}

st.title("🏗️ Diseño Térmico de Horno Cilíndrico")

# --- BARRA LATERAL: ENTRADAS ---
st.sidebar.header("📏 Dimensiones del Horno")
diam_int_cm = st.sidebar.number_input("Diámetro Interior (cm)", value=60.0)
largo_m = st.sidebar.number_input("Largo del Horno (m)", value=3.0)
espesor_ref_cm = st.sidebar.slider("Espesor del Refractario (cm)", 5, 50, 15)
espesor_chapa_mm = st.sidebar.slider("Espesor de la Chapa (mm)", 3, 20, 6)

st.sidebar.header("🧱 Materiales")
tipo_ref = st.sidebar.selectbox("Selecciona Refractario:", list(materiales.keys()))
k_ref = materiales[tipo_ref]["k"]
k_acero = 50.0 # Conductividad estándar del acero

# --- CÁLCULOS FÍSICOS ---
r1 = (diam_int_cm / 2) / 100
r2 = r1 + (espesor_ref_cm / 100)
r3 = r2 + (espesor_chapa_mm / 1000)
temp_int = 1500
temp_amb = 25

# Resistencia Térmica Total (Refractario + Chapa)
r_refractario = np.log(r2/r1) / (2 * np.pi * k_ref * largo_m)
r_chapa = np.log(r3/r2) / (2 * np.pi * k_acero * largo_m)
R_total = r_refractario + r_chapa

# Flujo de calor (Watts)
q_total = (temp_int - temp_amb) / R_total

# Temperaturas en las interfaces
t_intermedia = temp_int - (q_total * r_refractario) # Entre refractario y chapa
t_exterior = t_intermedia - (q_total * r_chapa)   # Cara externa de la chapa

# --- INTERFAZ DE RESULTADOS ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("T° Interfaz (Ref/Chapa)", f"{t_intermedia:.1f} °C")
with col2:
    st.metric("T° Exterior Chapa", f"{t_exterior:.1f} °C")
with col3:
    st.metric("Pérdida Total", f"{q_total/1000:.2f} kW")

st.info(f"**Material seleccionado:** {materiales[tipo_ref]['desc']}")

# --- VISUALIZACIÓN ---
tab1, tab2 = st.tabs(["📈 Gráfico de Gradiente", "⭕ Vista de Sección"])

with tab1:
    # Radios para graficar (Refractario + Chapa)
    radios = np.linspace(r1, r3, 100)
    temps = []
    for r in radios:
        if r <= r2: # Dentro del refractario
            t = temp_int - (temp_int - t_intermedia) * (np.log(r/r1) / np.log(r2/r1))
        else: # Dentro de la chapa
            t = t_intermedia - (t_intermedia - t_exterior) * (np.log(r/r2) / np.log(r3/r2))
        temps.append(t)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(radios*100, temps, color='red', lw=3)
    ax.axvspan(r1*100, r2*100, color='orange', alpha=0.1, label='Refractario')
    ax.axvspan(r2*100, r3*100, color='blue', alpha=0.2, label='Chapa Acero')
    ax.set_xlabel("Radio (cm)")
    ax.set_ylabel("Temperatura (°C)")
    ax.legend()
    st.pyplot(fig)

with tab2:
    # Mapa de calor circular
    theta = np.linspace(0, 2*np.pi, 100)
    r_malla, t_malla = np.meshgrid(np.linspace(r1, r3, 50), theta)
    
    # Calcular matriz de temperaturas para el mapa
    z_malla = np.zeros_like(r_malla)
    for i in range(r_malla.shape[0]):
        for j in range(r_malla.shape[1]):
            r = r_malla[i,j]
            if r <= r2:
                z_malla[i,j] = temp_int - (temp_int - t_intermedia) * (np.log(r/r1) / np.log(r2/r1))
            else:
                z_malla[i,j] = t_intermedia - (t_intermedia - t_exterior) * (np.log(r/r2) / np.log(r3/r2))

    fig2, ax2 = plt.subplots(figsize=(6,6))
    ax2 = plt.subplot(111, projection='polar')
    cont = ax2.pcolormesh(t_malla, r_malla*100, z_malla, cmap='inferno', shading='auto')
    plt.colorbar(cont, label="Temperatura °C", pad=0.1)
    ax2.set_yticklabels([]) # Limpiar etiquetas radiales para estética
    st.pyplot(fig2)

# --- VALIDACIÓN DE SEGURIDAD ---
if t_exterior > 150:
    st.error("🚨 ALERTA: La chapa exterior está demasiado caliente. ¡Peligro de quemaduras y falla estructural!")
elif t_intermedia > 400:
    st.warning("⚠️ AVISO: La chapa interna supera los 400°C. Revisa la expansión térmica del acero.")
