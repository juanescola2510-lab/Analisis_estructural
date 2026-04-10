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

# --- TABLAS DE CARGAS (CON KEY PARA CAPTURAR CAMBIOS) ---
st.header("⚖️ Cargas Aplicadas")
c1, c2, c3 = st.columns(3)
with c1:
    df_p = st.data_editor(pd.DataFrame([{"x": 3.0, "P (kN)": 50.0}]), num_rows="dynamic", key="p_editor")
with c2:
    df_q = st.data_editor(pd.DataFrame([{"x_i": 0.0, "x_f": 6.0, "q (kN/m)": 10.0}]), num_rows="dynamic", key="q_editor")
with c3:
    df_m = st.data_editor(pd.DataFrame([{"x": 3.0, "M (kNm)": 0.0}]), num_rows="dynamic", key="m_editor")

if st.button("🚀 CALCULAR ESTRUCTURA", use_container_width=True):
    try:
        # 1. FILTRADO ESTRICTO DE DATOS
        p_v = df_p.dropna().query("`P (kN)` != 0")
        q_v = df_q.dropna().query("`q (kN/m)` != 0")
        m_v = df_m.dropna().query("`M (kNm)` != 0")

        # 2. SISTEMA Y SEGMENTACIÓN
        ss = SystemElements(EA=E*area, EI=E*I)
        puntos = {0.0, float(L)}
        for x in p_v["x"]: puntos.add(round(float(x), 4))
        for x in m_v["x"]: puntos.add(round(float(x), 4))
        for _, r in q_v.iterrows(): 
            puntos.add(round(float(r["x_i"]), 4))
            puntos.add(round(float(r["x_f"]), 4))
        
        pts_ordenados = sorted([x for x in puntos if 0 <= x <= L])
        
        for i in range(len(pts_ordenados)-1):
            ss.add_element(location=[[pts_ordenados[i], 0], [pts_ordenados[i+1], 0]])
        
        # 3. APOYOS
        n_final = len(pts_ordenados)
        if t_izq == "Fijo": ss.add_support_hinged(1)
        elif t_izq == "Empotrado": ss.add_support_fixed(1)
        if t_der == "Móvil": ss.add_support_roll(n_final, direction=2)
        elif t_der == "Fijo": ss.add_support_hinged(n_final)
        elif t_der == "Empotrado": ss.add_support_fixed(n_final)

        # 4. APLICACIÓN DE CARGAS
        for _, r in p_v.iterrows():
            pos = round(float(r["x"]), 4)
            idx = pts_ordenados.index(pos) + 1
            ss.point_load(Fy=-float(r["P (kN)"]), node_id=idx)
            
        for _, r in m_v.iterrows():
            pos = round(float(r["x"]), 4)
            idx = pts_ordenados.index(pos) + 1
            ss.moment_load(Ty=float(r["M (kNm)"]), node_id=idx)

        for _, r in q_v.iterrows():
            xi, xf, val_q = float(r["x_i"]), float(r["x_f"]), float(r["q (kN/m)"])
            for i in range(len(pts_ordenados)-1):
                mid = round((pts_ordenados[i] + pts_ordenados[i+1]) / 2, 4)
                if xi <= mid <= xf:
                    ss.q_load(q=-val_q, element_id=i+1)

        ss.solve()
        
        # 5. RESULTADOS
        res = ss.get_element_results()
        m_max = max([abs(r['Mmax']) for r in res]) if res else 0
        
        sigma_mpa = (m_max * 1000 * c / I) / 1e6
        util = (sigma_mpa / Fy) * 100

        st.header("📊 Informe Final")
        c1, c2, c3 = st.columns(3)
        c1.metric("Momento Máximo", f"{m_max:.2f} kNm")
        c2.metric("Esfuerzo Máximo", f"{sigma_mpa:.2f} MPa")
        c3.metric("Uso del Material", f"{util:.1f}%")

        if util > 100:
            st.error(f"❌ FALLA: La viga colapsa al {util:.1f}%")
        else:
            st.success(f"✅ SEGURA: La viga resiste al {util:.1f}%")

        tab_diag, tab_reac = st.tabs(["📈 Diagramas", "📍 Reacciones"])
        with tab_diag:
            col_a, col_b = st.columns(2)
            with col_a: st.pyplot(ss.show_bending_moment(show=False))
            with col_b: st.pyplot(ss.show_displacement(show=False))
        
        with tab_reac:
            reac = ss.get_node_results_system()
            st.table([{"Nodo": r['id'], "Fy (kN)": round(r.get('fy',0),2), "M (kNm)": round(r.get('m',0),2)} for r in reac if abs(r.get('fy',0)) > 1e-3 or abs(r.get('m',0)) > 1e-3])

    except Exception as e:
        st.error(f"Error de cálculo: {e}")
