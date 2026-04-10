import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

st.set_page_config(page_title="Ingeniería PRO", layout="wide")
st.title("🏗️ Analizador y Optimizador Estructural")

# --- BARRA LATERAL ---
st.sidebar.header("🛠️ Sección y Material")
material = st.sidebar.selectbox("Material", ["Acero (ASTM A36)", "Concreto (f'c 210)", "Madera (Pino)"])
E_map = {"Acero (ASTM A36)": 200e6, "Concreto (f'c 210)": 21e6, "Madera (Pino)": 10e6}
Fy_map = {"Acero (ASTM A36)": 250, "Concreto (f'c 210)": 21, "Madera (Pino)": 15}
E, Fy = E_map[material], Fy_map[material]

forma = st.sidebar.selectbox("Forma de la Sección", ["Rectangular", "Circular Maciza"])
if forma == "Rectangular":
    base = st.sidebar.number_input("Base (m)", 0.01, 2.0, 0.20)
    altura = st.sidebar.number_input("Altura (m)", 0.01, 2.0, 0.40)
    I, area, c = (base * (altura**3)) / 12, base * altura, altura / 2
else:
    radio = st.sidebar.number_input("Radio (m)", 0.01, 2.0, 0.15)
    I, area, c = (np.pi * (radio**4)) / 4, np.pi * (radio**2), radio

st.sidebar.header("📐 Geometría")
L = st.sidebar.number_input("Longitud total (m)", 0.1, 500.0, 6.0)
t_izq = st.sidebar.selectbox("Apoyo Izq (x=0)", ["Fijo", "Empotrado", "Libre"])
t_der = st.sidebar.selectbox("Apoyo Der (x=L)", ["Móvil", "Fijo", "Empotrado", "Libre"])

# --- CARGAS ---
st.header("⚖️ Cargas Aplicadas")
c1, c2 = st.columns(2)
with c1:
    st.subheader("📍 Cargas Puntuales")
    df_p = st.data_editor(pd.DataFrame([{"x": 3.0, "P (kN)": 10.0}]), num_rows="dynamic", key="p_editor")
with c2:
    st.subheader("📏 Cargas Distribuidas")
    df_q = st.data_editor(pd.DataFrame([{"x_i": 0.0, "x_f": 6.0, "q (kN/m)": 3.0}]), num_rows="dynamic", key="q_editor")

if st.button("🚀 CALCULAR ESTRUCTURA", use_container_width=True):
    try:
        # FORZAR CONVERSIÓN A FLOTANTES PARA EVITAR NULOS
        p_v = pd.DataFrame(df_p).apply(pd.to_numeric, errors='coerce').dropna()
        q_v = pd.DataFrame(df_q).apply(pd.to_numeric, errors='coerce').dropna()
        
        p_v = p_v[p_v["P (kN)"] != 0]
        q_v = q_v[q_v["q (kN/m)"] != 0]

        ss = SystemElements(EA=E*area, EI=E*I)
        puntos = {0.0, float(L)}
        for x in p_v["x"]: puntos.add(round(float(x), 3))
        for _, r in q_v.iterrows(): 
            puntos.add(round(float(r["x_i"]), 3))
            puntos.add(round(float(r["x_f"]), 3))
        
        pts = sorted([x for x in puntos if 0 <= x <= L])
        for i in range(len(pts)-1):
            ss.add_element(location=[[pts[i], 0], [pts[i+1], 0]])
        
        nf = len(pts)
        if t_izq == "Fijo": ss.add_support_hinged(1)
        elif t_izq == "Empotrado": ss.add_support_fixed(1)
        if t_der == "Móvil": ss.add_support_roll(nf, direction=2)
        elif t_der == "Fijo": ss.add_support_hinged(nf)
        elif t_der == "Empotrado": ss.add_support_fixed(nf)

        for _, r in p_v.iterrows():
            ss.point_load(Fy=-float(r["P (kN)"]), node_id=pts.index(round(float(r["x"]), 3)) + 1)
        for _, r in q_v.iterrows():
            xi, xf, val_q = float(r["x_i"]), float(r["x_f"]), float(r["q (kN/m)"])
            for i in range(len(pts)-1):
                mid = (pts[i] + pts[i+1]) / 2
                if xi <= mid <= xf:
                    ss.q_load(q=-val_q, element_id=i+1)

        ss.solve()
        
        # --- EXTRACCIÓN DE DATOS REALES ---
        res = ss.get_element_results()
        # Buscamos el valor máximo real en todos los tramos
        m_max = max([abs(r['Mmax']) for r in res]) if res else 0
        sigma_mpa = (m_max * 1000 * c / I) / 1e6
        util = (sigma_mpa / Fy) * 100

        st.header("📊 Informe de Ingeniería")
        c1, c2, c3 = st.columns(3)
        c1.metric("Momento Máx", f"{m_max:.2f} kNm")
        c2.metric("Esfuerzo Máx", f"{sigma_mpa:.2f} MPa")
        c3.metric("Utilización", f"{util:.1f}%")

        if m_max > 0:
            st.success("✅ Datos procesados correctamente.")
            col_a, col_b = st.columns(2)
            with col_a: st.pyplot(ss.show_bending_moment(show=False))
            with col_b: st.pyplot(ss.show_displacement(show=False))
        else:
            st.error("⚠️ El cálculo sigue dando 0. Prueba a pulsar 'Enter' en las celdas de la tabla antes de calcular.")

    except Exception as e:
        st.error(f"Error: {e}")
