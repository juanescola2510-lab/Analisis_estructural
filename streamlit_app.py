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
c1, c2 = st.columns(2)
with c1:
    st.subheader("📍 Cargas Puntuales")
    df_p = st.data_editor(pd.DataFrame([{"x": 3.0, "P (kN)": 50.0}]), num_rows="dynamic", key="p_edit")
with c2:
    st.subheader("📏 Cargas Distribuidas")
    df_q = st.data_editor(pd.DataFrame([{"x_i": 0.0, "x_f": 6.0, "q (kN/m)": 10.0}]), num_rows="dynamic", key="q_edit")

if st.button("🚀 CALCULAR ESTRUCTURA", use_container_width=True):
    try:
        # 1. FORZAR LECTURA DE DATOS (Solución al error 0)
        p_v = pd.DataFrame(st.session_state["p_edit"]).dropna()
        q_v = pd.DataFrame(st.session_state["q_edit"]).dropna()
        
        # Eliminar filas con ceros o vacías
        p_v = p_v[p_v["P (kN)"] != 0]
        q_v = q_v[q_v["q (kN/m)"] != 0]

        ss = SystemElements(EA=E*area, EI=E*I)
        
        # 2. NODOS Y SEGMENTACIÓN
        puntos = {0.0, float(L)}
        for x in p_v["x"]: puntos.add(round(float(x), 4))
        for _, r in q_v.iterrows(): 
            puntos.add(round(float(r["x_i"]), 4))
            puntos.add(round(float(r["x_f"]), 4))
        
        pts = sorted([x for x in puntos if 0 <= x <= L])
        for i in range(len(pts)-1):
            ss.add_element(location=[[pts[i], 0], [pts[i+1], 0]])
        
        # 3. APOYOS
        nf = len(pts)
        if t_izq == "Fijo": ss.add_support_hinged(1)
        elif t_izq == "Empotrado": ss.add_support_fixed(1)
        if t_der == "Móvil": ss.add_support_roll(nf, direction=2)
        elif t_der == "Fijo": ss.add_support_hinged(nf)
        elif t_der == "Empotrado": ss.add_support_fixed(nf)

        # 4. CARGAS
        for _, r in p_v.iterrows():
            idx = pts.index(round(float(r["x"]), 4)) + 1
            ss.point_load(Fy=-float(r["P (kN)"]), node_id=idx)
        for _, r in q_v.iterrows():
            xi, xf, val_q = float(r["x_i"]), float(r["x_f"]), float(r["q (kN/m)"])
            for i in range(len(pts)-1):
                mid = round((pts[i] + pts[i+1]) / 2, 4)
                if xi <= mid <= xf:
                    ss.q_load(q=-val_q, element_id=i+1)

        ss.solve()
        
        # 5. RESULTADOS E INFORMES
        m_max = max([abs(r['Mmax']) for r in ss.get_element_results()])
        sigma_mpa = (m_max * 1000 * c / I) / 1e6
        util = (sigma_mpa / Fy) * 100

        st.header("📊 Informe de Ingeniería")
        col_res, col_img = st.columns([2, 1])
        
        with col_res:
            c1, c2, c3 = st.columns(3)
            c1.metric("Momento Máx", f"{m_max:.2f} kNm")
            c2.metric("Esfuerzo Máx", f"{sigma_mpa:.2f} MPa")
            c3.metric("Uso Material", f"{util:.1f}%")
            
            if util > 100: st.error("❌ LA VIGA FALLA POR FLEXIÓN")
            else: st.success("✅ ESTRUCTURA SEGURA")

        with col_img:
            st.write("**Sección Transversal**")
            fig_sec, ax_sec = plt.subplots(figsize=(3,3))
            if forma == "Rectangular":
                rect = plt.Rectangle((-base/2, -altura/2), base, altura, color='gray', alpha=0.7)
                ax_sec.add_patch(rect)
                ax_sec.set_xlim(-base, base); ax_sec.set_ylim(-altura, altura)
            else:
                circ = plt.Circle((0,0), radio, color='gray', alpha=0.7)
                ax_sec.add_patch(circ)
                ax_sec.set_xlim(-radio*2, radio*2); ax_sec.set_ylim(-radio*2, radio*2)
            ax_sec.set_aspect('equal'); plt.grid(linestyle='--')
            st.pyplot(fig_sec)

        tabs = st.tabs(["📉 Momento Flector", "🌊 Deflexión Real"])
        with tabs: st.pyplot(ss.show_bending_moment(show=False))
        with tabs: st.pyplot(ss.show_displacement(show=False))

    except Exception as e:
        st.error(f"Error: {e}")
