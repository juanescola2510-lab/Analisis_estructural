import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Configuración de página
st.set_page_config(page_title="Ingeniería de Perfiles PRO", layout="wide")
st.title("🏗️ Analizador Estructural con Verificación de Resistencia")

# --- BARRA LATERAL: PROPIEDADES ---
st.sidebar.header("🛠️ Propiedades de la Sección")

# 1. Selección de Material y Esfuerzo de Fluencia (Fy en MPa)
material = st.sidebar.selectbox("Material", ["Acero (ASTM A36)", "Concreto (f'c 210)", "Madera (Pino)"])
E_map = {"Acero (ASTM A36)": 200e6, "Concreto (f'c 210)": 21e6, "Madera (Pino)": 10e6} # kPa
Fy_map = {"Acero (ASTM A36)": 250, "Concreto (f'c 210)": 21, "Madera (Pino)": 15} # MPa (Aprox para diseño)

E = E_map[material]
Fy = Fy_map[material]

# 2. Selección de Forma y Cálculo de Inercia (I) y distancia al eje neutro (c)
forma = st.sidebar.selectbox("Forma de la Sección", ["Rectangular", "Circular Maciza"])

if forma == "Rectangular":
    base = st.sidebar.number_input("Base (m)", 0.01, 1.0, 0.2, step=0.01)
    altura = st.sidebar.number_input("Altura (m)", 0.01, 1.0, 0.4, step=0.01)
    I = (base * (altura**3)) / 12
    area = base * altura
    c = altura / 2  # Distancia máxima al eje neutro
elif forma == "Circular Maciza":
    radio = st.sidebar.number_input("Radio (m)", 0.01, 1.0, 0.15, step=0.01)
    I = (np.pi * (radio**4)) / 4
    area = np.pi * (radio**2)
    c = radio

# --- GEOMETRÍA Y CARGAS ---
st.sidebar.header("📐 Geometría")
L = st.sidebar.number_input("Longitud total (m)", 0.1, 100.0, 6.0, step=0.1)
tipo_izq = st.sidebar.selectbox("Apoyo Izq", ["Fijo", "Empotrado", "Libre"])
tipo_der = st.sidebar.selectbox("Apoyo Der", ["Móvil", "Fijo", "Empotrado", "Libre"])

st.header("⚖️ Cargas Aplicadas")
col1, col2, col3 = st.columns(3)
with col1:
    df_p = st.data_editor(pd.DataFrame([{"x": L/2, "P (kN)": 20.0}]), num_rows="dynamic", key="p")
with col2:
    df_q = st.data_editor(pd.DataFrame([{"x_i": 0.0, "x_f": L, "q (kN/m)": 0.0}]), num_rows="dynamic", key="q")
with col3:
    df_m = st.data_editor(pd.DataFrame([{"x": L/2, "M (kNm)": 0.0}]), num_rows="dynamic", key="m")

# --- CÁLCULO ---
if st.button("🚀 Iniciar Análisis de Resistencia", use_container_width=True):
    try:
        ss = SystemElements(EA=E*area, EI=E*I)
        
        # Segmentación y Aplicación de Cargas (Lógica simplificada anterior)
        puntos = {0.0, float(L)}
        p_v = df_p.dropna().loc[df_p["P (kN)"] != 0]; m_v = df_m.dropna().loc[df_m["M (kNm)"] != 0]
        q_v = df_q.dropna().loc[df_q["q (kN/m)"] != 0]
        for x in p_v["x"]: puntos.add(float(x))
        for x in m_v["x"]: puntos.add(float(x))
        for _, r in q_v.iterrows(): puntos.update([float(r["x_i"]), float(r["x_f"])])
        
        pts = sorted([x for x in puntos if 0 <= x <= L])
        for i in range(len(pts)-1): ss.add_element(location=[[pts[i], 0], [pts[i+1], 0]])
        
        nf = len(pts)
        if tipo_izq == "Fijo": ss.add_support_hinged(1)
        elif tipo_izq == "Empotrado": ss.add_support_fixed(1)
        if tipo_der == "Móvil": ss.add_support_roll(nf, direction=2)
        elif tipo_der == "Fijo": ss.add_support_hinged(nf)
        elif tipo_der == "Empotrado": ss.add_support_fixed(nf)

        for _, r in p_v.iterrows(): ss.point_load(Fy=-float(r["P (kN)"]), node_id=pts.index(float(r["x"]))+1)
        for _, r in m_v.iterrows(): ss.moment_load(Ty=float(r["M (kNm)"]), node_id=pts.index(float(r["x"]))+1)
        for _, r in q_v.iterrows():
            for i in range(len(pts)-1):
                if float(r["x_i"]) <= (pts[i]+pts[i+1])/2 <= float(r["x_f"]):
                    ss.q_load(q=-float(r["q (kN/m)"]), element_id=i+1)

        ss.solve()

        # --- ANÁLISIS DE ESFUERZOS ---
        # Obtenemos el momento máximo absoluto
        momentos = ss.get_element_results()
        m_max = max([abs(res['Mmax']) for res in momentos]) # kNm
        
        # Cálculo de Esfuerzo Máximo: sigma = M * c / I
        # M en kNm -> *1000 para Nm. I en m4. c en m. Resultado en Pascales (Pa).
        sigma_max_pa = (m_max * 1000 * c) / I
        sigma_max_mpa = sigma_max_pa / 1e6 # Convertir a MPa
        
        # Factor de Utilización
        utilizacion = (sigma_max_mpa / Fy) * 100

        # --- MOSTRAR RESULTADOS ---
        st.header("📊 Resultados e Informe de Ingeniería")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Momento Máximo", f"{m_max:.2f} kNm")
        c2.metric("Esfuerzo actuante", f"{sigma_max_mpa:.2f} MPa")
        c3.metric("Límite Material", f"{Fy:.1f} MPa")

        if utilizacion <= 100:
            st.success(f"✅ ESTRUCTURA SEGURA: El material trabaja al {utilizacion:.1f}% de su capacidad.")
        else:
            st.error(f"❌ FALLA ESTRUCTURAL: El esfuerzo supera el límite por {utilizacion - 100:.1f}%. ¡Aumenta la sección!")

        tabs = st.tabs(["📉 Cortante", "📈 Momento", "🌊 Deflexión Real"])
        with tabs[0]: st.pyplot(ss.show_shear_force(show=False))
        with tabs[1]: st.pyplot(ss.show_bending_moment(show=False))
        with tabs[2]: st.pyplot(ss.show_displacement(show=False))

    except Exception as e:
        st.error(f"Error: {e}")
