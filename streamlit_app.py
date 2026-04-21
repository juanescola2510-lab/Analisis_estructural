import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulador de Horno Industrial Pro", layout="wide")

# --- BASE DE DATOS DE MATERIALES ---
materiales = {
    "Ladrillo de Magnesita (Alta T°)": {"k": 3.5, "densidad": 2800, "desc": "Alta resistencia a 1500°C+, pero conduce mucho calor."},
    "Ladrillo de Alúmina (Estándar)": {"k": 1.5, "densidad": 2500, "desc": "Equilibrio entre resistencia y aislamiento."},
    "Ladrillo de Sílice": {"k": 1.1, "densidad": 2200, "desc": "Usado comúnmente en hornos de fundición."},
    "Ladrillo Refractario Aislante": {"k": 0.3, "densidad": 800, "desc": "Baja resistencia mecánica, alto aislamiento."},
    "Fibra Cerámica (Manta)": {"k": 0.12, "densidad": 128, "desc": "Máximo aislamiento, pero muy frágil."}
}

st.title("🏗️ Diseño Térmico y Estructural de Horno Cilíndrico")

# --- BARRA LATERAL: ENTRADAS ---
st.sidebar.header("📐 Dimensiones del Horno")
diam_int_cm = st.sidebar.number_input("Diámetro Interior (cm)", value=60.0)
largo_m = st.sidebar.number_input("Largo del Horno (m)", value=3.0)
espesor_ref_cm = st.sidebar.slider("Espesor del Refractario (cm)", 5, 50, 15)
espesor_chapa_mm = st.sidebar.slider("Espesor de la Chapa Acero (mm)", 3, 20, 6)

st.sidebar.header("🧱 Materiales")
tipo_ref = st.sidebar.selectbox("Selecciona Refractario:", list(materiales.keys()))
k_ref = materiales[tipo_ref]["k"]
densidad_ref = materiales[tipo_ref]["densidad"]
k_acero = 50.0 

# --- CÁLCULOS FÍSICOS ---
r1 = (diam_int_cm / 2) / 100
r2 = r1 + (espesor_ref_cm / 100)
r3 = r2 + (espesor_chapa_mm / 1000)
temp_int = 1500
temp_amb = 25

# Resistencia Térmica Total
r_refractario = np.log(r2/r1) / (2 * np.pi * k_ref * largo_m)
r_chapa = np.log(r3/r2) / (2 * np.pi * k_acero * largo_m)
R_total = r_refractario + r_chapa

# Flujo de calor y Temperaturas
q_total = (temp_int - temp_amb) / R_total
t_intermedia = temp_int - (q_total * r_refractario)
t_exterior = t_intermedia - (q_total * r_chapa)

# Cálculo de Peso (Volumen cilindro hueco)
vol_ref = np.pi * (r2**2 - r1**2) * largo_m
peso_ref = vol_ref * densidad_ref

# --- INTERFAZ DE RESULTADOS ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("T° Exterior Chapa", f"{t_exterior:.1f} °C")
c2.metric("Pérdida de Calor", f"{q_total/1000:.2f} kW")
c3.metric("Peso Refractario", f"{peso_ref:.0f} kg")
c4.metric("Gas mes (Pérdida)", f"${((q_total/1000)*160/10.5)*0.6:.1f}")

# --- GRÁFICOS ---
col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader("📈 Perfil de Temperatura Radial (Logarítmico)")
    radios_plot = np.linspace(r1, r3, 100)
    temps_plot = []
    for r in radios_plot:
        if r <= r2:
            t = temp_int - (temp_int - t_intermedia) * (np.log(r/r1) / np.log(r2/r1))
        else:
            t = t_intermedia - (t_intermedia - t_exterior) * (np.log(r/r2) / np.log(r3/r2))
        temps_plot.append(t)
    
    fig1, ax1 = plt.subplots()
    ax1.plot(radios_plot*100, temps_plot, color='red', lw=3)
    ax1.axvspan(r1*100, r2*100, color='orange', alpha=0.1, label='Refractario')
    ax1.axvspan(r2*100, r3*100, color='gray', alpha=0.3, label='Chapa')
    ax1.set_xlabel("Radio (cm)")
    ax1.set_ylabel("Temperatura (°C)")
    ax1.legend()
    st.pyplot(fig1)

with col_der:
    st.subheader("⭕ Vista de Sección Transversal")
    theta = np.linspace(0, 2*np.pi, 100)
    r_malla, t_malla = np.meshgrid(np.linspace(r1, r3, 50), theta)
    z_malla = np.zeros_like(r_malla)
    for i in range(r_malla.shape[0]):
        for j in range(r_malla.shape[1]):
            r = r_malla[i,j]
            if r <= r2:
                z_malla[i,j] = temp_int - (temp_int - t_intermedia) * (np.log(r/r1) / np.log(r2/r1))
            else:
                z_malla[i,j] = t_intermedia - (t_intermedia - t_exterior) * (np.log(r/r2) / np.log(r3/r2))

    fig2 = plt.figure(figsize=(6,6))
    ax2 = plt.subplot(111, projection='polar')
    cont = ax2.pcolormesh(t_malla, r_malla*100, z_malla, cmap='inferno', shading='auto')
    plt.colorbar(cont, label="Temperatura °C", pad=0.1)
    ax2.set_yticklabels([]) 
    st.pyplot(fig2)

if t_exterior > 120:
    st.error(f"🚨 PELIGRO: La chapa está a {t_exterior:.1f}°C. El acero pierde resistencia y es un riesgo de quemadura.")
