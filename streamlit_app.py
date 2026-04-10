import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Configuración de página
st.set_page_config(page_title="Ingeniería de Perfiles PRO", layout="wide")
st.title("🏗️ Analizador Estructural con Materiales y Secciones")

# --- BARRA LATERAL: MATERIAL Y FORMA ---
st.sidebar.header("🛠️ Propiedades de la Sección")

# 1. Selección de Material
material = st.sidebar.selectbox("Material", ["Acero (ASTM A36)", "Concreto (f'c 210)", "Madera (Pino)"])
E_map = {"Acero (ASTM A36)": 200e6, "Concreto (f'c 210)": 21e6, "Madera (Pino)": 10e6} # kPa
E = E_map[material]

# 2. Selección de Forma y Cálculo de Inercia (I)
forma = st.sidebar.selectbox("Forma de la Sección", ["Rectangular", "Circular Maciza", "Perfil I (Héxtandar)"])

if forma == "Rectangular":
    base = st.sidebar.number_input("Base (m)", 0.1, 1.0, 0.2, step=0.01)
    altura = st.sidebar.number_input("Altura (m)", 0.1, 1.0, 0.4, step=0.01)
    I = (base * (altura**3)) / 12
    area = base * altura
elif forma == "Circular Maciza":
    radio = st.sidebar.number_input("Radio (m)", 0.05, 1.0, 0.15, step=0.01)
    I = (np.pi * (radio**4)) / 4
    area = np.pi * (radio**2)
else: # Perfil I básico
    tw, tf, h, b = 0.01, 0.02, 0.3, 0.2 # Valores fijos para ejemplo
    st.sidebar.info("Perfil IPE estándar (0.3x0.2m)")
    I = 0.00008 # Valor aproximado m4
    area = 0.005

st.sidebar.write(f"**Inercia (I):** {I:.2e} $m^4$")

# --- GEOMETRÍA Y APOYOS ---
st.sidebar.header("📐 Geometría")
L = st.sidebar.number_input("Longitud (m)", 0.1, 100.0, 6.0, step=0.1)
tipo_izq = st.sidebar.selectbox("Apoyo Izq", ["Fijo", "Empotrado", "Libre"])
tipo_der = st.sidebar.selectbox("Apoyo Der", ["Móvil", "Fijo", "Empotrado", "Libre"])

# --- TABLAS DE CARGAS ---
st.header("⚖️ Cargas y Momentos")
col1, col2, col3 = st.columns(3)
with col1:
    df_p = st.data_editor(pd.DataFrame([{"x": L/2, "P (kN)": 10.0}]), num_rows="dynamic", key="p")
with col2:
    df_q = st.data_editor(pd.DataFrame([{"x_i": 0.0, "x_f": L, "q (kN/m)": 5.0}]), num_rows="dynamic", key="q")
with col3:
    df_m = st.data_editor(pd.DataFrame([{"x": L/2, "M (kNm)": 0.0}]), num_rows="dynamic", key="m")

# --- CÁLCULO ---
if st.button("🚀 Iniciar Análisis Estructural", use_container_width=True):
    try:
        # EA = E * Area, EI = E * I
        ss = SystemElements(EA=E*area, EI=E*I)
        
        # Segmentación
        puntos = {0.0, L}
        for x in df_p.dropna()["x"]: puntos.add(float(x))
        for x in df_m.dropna()["x"]: puntos.add(float(x))
        for _, r in df_q.dropna().iterrows(): puntos.update([float(r["x_i"]), float(r["x_f"])])
        
        pts = sorted([x for x in puntos if 0 <= x <= L])
        for i in range(len(pts)-1):
            ss.add_element(location=[[pts[i], 0], [pts[i+1], 0]])
            
        # Apoyos
        nf = len(pts)
        if tipo_izq == "Fijo": ss.add_support_hinged(1)
        elif tipo_izq == "Empotrado": ss.add_support_fixed(1)
        if tipo_der == "Móvil": ss.add_support_roll(nf, direction=2)
        elif tipo_der == "Fijo": ss.add_support_hinged(nf)
        elif tipo_der == "Empotrado": ss.add_support_fixed(nf)

        # Aplicar Cargas (Filtro anti-ceros)
        for _, r in df_p.dropna().iterrows():
            if r["P (kN)"] != 0: ss.point_load(Fy=-float(r["P (kN)"]), node_id=pts.index(float(r["x"]))+1)
        for _, r in df_m.dropna().iterrows():
            if r["M (kNm)"] != 0: ss.moment_load(Ty=float(r["M (kNm)"]), node_id=pts.index(float(r["x"]))+1)
        for _, r in df_q.dropna().iterrows():
            if r["q (kN/m)"] != 0:
                for i in range(len(pts)-1):
                    if float(r["x_i"]) <= (pts[i]+pts[i+1])/2 <= float(r["x_f"]):
                        ss.q_load(q=-float(r["q (kN/m)"]), element_id=i+1)

        ss.solve()

        # Resultados
        st.header("📊 Resultados del Análisis")
        t1, t2, t3, t4 = st.tabs(["📐 Estructura", "📉 Cortante", "📈 Momento", "🌊 Deflexión Real"])
        with t1: st.pyplot(ss.show_structure(show=False))
        with t2: st.pyplot(ss.show_shear_force(show=False))
        with t3: st.pyplot(ss.show_bending_moment(show=False))
        with t4: 
            st.info(f"Deflexión calculada con E={E/1e6:.1f} MPa e I={I:.2e} m4")
            st.pyplot(ss.show_displacement(show=False))

    except Exception as e:
        st.error(f"Error: {e}")
