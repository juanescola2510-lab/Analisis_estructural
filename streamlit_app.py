import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Configuración inicial
st.set_page_config(page_title="Gestor de Colectores de Polvo", layout="wide")

st.title("🌪️ Sistema de Diagnóstico: Colector de Mangas y Ductos")

# --- BARRA LATERAL: ENTRADA DE DATOS ---
st.sidebar.header("📊 Datos del Sistema Actual")

cfm_entrada = st.sidebar.number_input("Caudal del Ventilador (CFM)", value=7600)
v_diseno = st.sidebar.slider("Velocidad de aire en ductos (m/s)", 15, 30, 20)

with st.sidebar.expander("Dimensiones de Mangas Actuales"):
    n_mangas_act = st.number_input("Número de mangas", value=120)
    diam_manga_mm = st.number_input("Diámetro manga (mm)", value=120)
    largo_manga_mm = st.number_input("Largo manga (mm)", value=2115)

st.sidebar.header("🔌 Nuevos Ramales")
n_ramales = st.sidebar.number_input("¿Cuántos ramales quieres conectar?", value=3)
diam_ramal_mm = st.sidebar.number_input("Diámetro de cada ramal (mm)", value=200)

# --- CÁLCULOS TÉCNICOS ---

# Conversiones
m3h_total = cfm_entrada * 1.699
area_manga_m2 = np.pi * (diam_manga_mm / 1000) * (largo_manga_mm / 1000)
area_filtracion_act = n_mangas_act * area_manga_m2
relacion_aire_tela = m3h_total / (area_filtracion_act * 60)

# Capacidad de Ramales
area_un_ramal = np.pi * (diam_ramal_mm / 1000)**2 / 4
caudal_un_ramal = area_un_ramal * v_diseno * 3600
max_ramales_posibles = int(m3h_total / caudal_un_ramal)

# Necesidades para nuevos ramales
caudal_total_nuevo = n_ramales * caudal_un_ramal
mangas_necesarias_total = np.ceil(caudal_total_nuevo / (1.1 * 60 * area_manga_m2))
mangas_faltantes = max(0, mangas_necesarias_total - n_mangas_act)

# Diámetro Ducto Principal
area_principal_req = (caudal_total_nuevo / 3600) / v_diseno
diam_principal_mm = np.sqrt(4 * area_principal_req / np.pi) * 1000

# --- INTERFAZ DE RESULTADOS ---

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Relación Aire/Tela Actual", f"{relacion_aire_tela:.2f} m/min")
    if relacion_aire_tela > 1.1:
        st.error("⚠️ Sobrecarga en mangas")
    else:
        st.success("✅ Mangas estables")

with col2:
    st.metric("Ramales soportados (Actual)", f"{max_ramales_posibles}")
    st.write(f"Cada ramal consume {caudal_un_ramal:.0f} m³/h")

with col3:
    st.metric("Ducto Principal Requerido", f"{diam_principal_mm:.0f} mm")

# --- ALERTAS DE EQUIPO ---
st.subheader("🛠️ Plan de Modificación")
if n_ramales > max_ramales_posibles:
    st.warning(f"❗ **Cambio de Motor/Ventilador:** Necesitas un ventilador de al menos {caudal_total_nuevo/1.699:.0f} CFM. El actual no tiene fuerza para {n_ramales} ramales.")
else:
    st.info("El ventilador actual soporta la carga, pero revisa la presión estática.")

if mangas_faltantes > 0:
    st.error(f"❗ **Faltan {mangas_faltantes:.0f} mangas.** Debes ampliar el colector para no quemar las actuales.")

# --- SIMULACIÓN VISUAL DEL POLVO ---
st.subheader("🌊 Simulación de Flujo en el Ducto")
fig, ax = plt.subplots(figsize=(10, 2))

# Dibujo del ducto
ax.axhline(0.5, color='black', lw=2)
ax.axhline(-0.5, color='black', lw=2)

# Partículas de polvo
n_particles = 100
x = np.random.rand(n_particles) * 10
y = (np.random.rand(n_particles) - 0.5) * 0.8

# Si el diámetro es pequeño (obstrucción), las partículas se ven más densas
densidad = 200 / diam_ramal_mm # Simulación visual de obstrucción
if diam_ramal_mm < 250:
    ax.scatter(x, y, s=5 * densidad, color='brown', alpha=0.6, label="Polvo Abrasivo")
else:
    ax.scatter(x, y, s=5, color='gray', alpha=0.4, label="Flujo Normal")

ax.set_xlim(0, 10)
ax.set_ylim(-1, 1)
ax.set_title(f"Visualización a {v_diseno} m/s")
ax.axis('off')
st.pyplot(fig)

st.markdown("""
### Notas de Interpretación:
1. **Puntos Marrones:** Indican alta densidad o riesgo de abrasión por ducto estrecho.
2. **Motor:** Si la suma de caudales de ramales > CFM de entrada, el motor actual **se disparará por amperaje**.
3. **Fraguado:** Si bajas la velocidad de 20 m/s en la barra lateral, el polvo decantará en el fondo del ducto visualizado.
""")
