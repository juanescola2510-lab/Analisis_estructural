import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

st.set_page_config(page_title="Analizador Estructural PRO", layout="wide")
st.title("🏗️ Analizador y Optimizador Estructural")

# --- BARRA LATERAL ---
st.sidebar.header("🛠️ Propiedades de la Sección")
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

# --- TABLAS DE CARGAS ---
st.header("⚖️ Cargas Aplicadas")
c1, c2, c3 = st.columns(3)
with c1:
    df_p = st.data_editor(pd.DataFrame([{"x": 3.0, "P (kN)": 50.0}]), num_rows="dynamic", key="p_v")
with c2:
    df_q = st.data_editor(pd.DataFrame([{"x_i": 0.0, "x_f": 6.0, "q (kN/m)": 10.0}]), num_rows="dynamic", key="q_v")
with c3:
    df_m = st.data_editor(pd.DataFrame([{"x": 3.0, "M (kNm)": 0.0}]), num_rows="dynamic", key="m_v")

if st.button("🚀 CALCULAR ESTRUCTURA", use_container_width=True):
    try:
        # Reiniciar sistema en cada clic
        ss = SystemElements(EA=E*area, EI=E*I)
        
        # 1. Limpieza de datos
        p_v = df_p.dropna().loc[df_p["P (kN)"] != 0]
        q_v = df_q.dropna().loc[df_q["q (kN/m)"] != 0]
        m_v = df_m.dropna().loc[df_m["M (kNm)"] != 0]

        # 2. Creación de Nodos (Puntos críticos)
        puntos = {0.0, float(L)}
        for x in p_v["x"]: puntos.add(float(x))
        for x in m_v["x"]: puntos.add(float(x))
        for _, r in q_v.iterrows(): 
            puntos.add(float(r["x_i"]))
            puntos.add(float(r["x_f"]))
        
        pts_ordenados = sorted([x for x in puntos if 0 <= x <= L])
        
        # 3. Construir Elementos
        for i in range(len(pts_ordenados)-1):
            ss.add_element(location=[[pts_ordenados[i], 0], [pts_ordenados[i+1], 0]])
        
        # 4. Aplicar Apoyos
        n_final = len(pts_ordenados)
        if t_izq == "Fijo": ss.add_support_hinged(1)
        elif t_izq == "Empotrado": ss.add_support_fixed(1)
        
        if t_der == "Móvil": ss.add_support_roll(n_final, direction=2)
        elif t_der == "Fijo": ss.add_support_hinged(n_final)
        elif t_der == "Empotrado": ss.add_support_fixed(n_final)

        # 5. Aplicar Cargas buscando el nodo exacto
        for _, r in p_v.iterrows():
            idx = pts_ordenados.index(float(r["x"])) + 1
            ss.point_load(Fy=-float(r["P (kN)"]), node_id=idx)
            
        for _, r in m_v.iterrows():
            idx = pts_ordenados.index(float(r["x"])) + 1
            ss.moment_load(Ty=float(r["M (kNm)"]), node_id=idx)

        for _, r in q_v.iterrows():
            for i in range(len(pts_ordenados)-1):
                mid = (pts_ordenados[i] + pts_ordenados[i+1]) / 2
                if float(r["x_i"]) <= mid <= float(r["x_f"]):
                    ss.q_load(q=-float(r["q (kN/m)"]), element_id=i+1)

        # 6. Resolver y Mostrar
        ss.solve()
        
        # Resultados numéricos
        resultados = ss.get_element_results()
        m_max = max([abs(r['Mmax']) for r in resultados]) if resultados else 0
        
        if m_max == 0:
            st.warning("⚠️ El Momento es 0. Revisa si los apoyos o las cargas están en posiciones compatibles.")
        
        sigma_mpa = (m_max * 1000 * c / I) / 1e6
        util = (sigma_mpa / Fy) * 100

        st.header("📊 Informe Final")
        c1, c2, c3 = st.columns(3)
        c1.metric("Momento Máximo", f"{m_max:.2f} kNm")
        c2.metric("Esfuerzo Máximo", f"{sigma_mpa:.2f} MPa")
        c3.metric("Uso del Material", f"{util:.1f}%")

        tabs = st.tabs(["Diagramas", "Detalle de Reacciones"])
        with tabs[0]:
            col_a, col_b = st.columns(2)
            with col_a: st.pyplot(ss.show_bending_moment(show=False))
            with col_b: st.pyplot(ss.show_displacement(show=False))
        
        with tabs[1]:
            reac = ss.get_node_results_system()
            st.table([{"Nodo": r['id'], "Fx": r.get('fx',0), "Fy": r.get('fy',0), "M": r.get('m',0)} for r in reac if r['id'] in [1, n_final]])

    except Exception as e:
        st.error(f"Error crítico: {e}")
