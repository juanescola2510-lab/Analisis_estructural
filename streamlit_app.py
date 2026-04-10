import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Ingeniería PRO", layout="wide")
st.title("🏗️ Analizador Estructural: Informe de Esfuerzos")

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
        # 1. Limpieza de datos (Evitar 0 y Nones)
        p_v = pd.DataFrame(df_p).apply(pd.to_numeric, errors='coerce').dropna()
        q_v = pd.DataFrame(df_q).apply(pd.to_numeric, errors='coerce').dropna()
        p_v = p_v[p_v["P (kN)"] != 0]
        q_v = q_v[q_v["q (kN/m)"] != 0]

        ss = SystemElements(EA=E*area, EI=E*I)
        
        # 2. Definición de puntos críticos
        puntos = {0.0, float(L)}
        for x in p_v["x"]: puntos.add(round(float(x), 3))
        for _, r in q_v.iterrows(): 
            puntos.add(round(float(r["x_i"]), 3))
            puntos.add(round(float(r["x_f"]), 3))
        
        pts = sorted([x for x in puntos if 0 <= x <= L])
        
        # 3. Crear elementos y apoyos
        for i in range(len(pts)-1):
            ss.add_element(location=[[pts[i], 0], [pts[i+1], 0]])
        
        nf = len(pts)
        if t_izq == "Fijo": ss.add_support_hinged(1)
        elif t_izq == "Empotrado": ss.add_support_fixed(1)
        if t_der == "Móvil": ss.add_support_roll(nf, direction=2)
        elif t_der == "Fijo": ss.add_support_hinged(nf)
        elif t_der == "Empotrado": ss.add_support_fixed(nf)

        # 4. Aplicación de Cargas
        for _, r in p_v.iterrows():
            idx = pts.index(round(float(r["x"]), 3)) + 1
            ss.point_load(Fy=-float(r["P (kN)"]), node_id=idx)
        for _, r in q_v.iterrows():
            xi, xf, val_q = float(r["x_i"]), float(r["x_f"]), float(r["q (kN/m)"])
            for i in range(len(pts)-1):
                mid = (pts[i] + pts[i+1]) / 2
                if xi <= mid <= xf:
                    ss.q_load(q=-val_q, element_id=i+1)

        ss.solve()
        
        # 5. EXTRACCIÓN DE RESULTADOS (CORRECCIÓN DE VALORES 0)
        elementos = ss.get_element_results()
        todos_los_momentos = []
        todas_las_deflexiones = []

        for el in elementos:
            # Capturamos todos los valores posibles de momento en cada tramo
            todos_los_momentos.append(abs(el.get('Mmin', 0)))
            todos_los_momentos.append(abs(el.get('Mmax', 0)))
            # Capturamos deflexiones
            todas_las_deflexiones.append(abs(el.get('wmin', 0)))
            todas_las_deflexiones.append(abs(el.get('wmax', 0)))
            
        m_max = max(todos_los_momentos) if todos_los_momentos else 0.0
        deflex_max_mm = (max(todas_las_deflexiones) if todas_las_deflexiones else 0.0) * 1000

        # 6. CÁLCULO DE ESFUERZO REAL
        sigma_mpa = (m_max * 1000 * c / I) / 1e6
        util = (sigma_mpa / Fy) * 100

        # --- INFORME ---
        st.header("📊 Informe de Ingeniería")
        col_res, col_img = st.columns([2, 1])
        
        with col_res:
            c1, c2, c3 = st.columns(3)
            c1.metric("Momento Máx", f"{m_max:.2f} kNm")
            c2.metric("Esfuerzo Máx", f"{sigma_mpa:.2f} MPa")
            c3.metric("Deflexión Máx", f"{deflex_max_mm:.2f} mm")
            
            st.write(f"**Utilización del material:** {util:.1f}%")
            if util > 100:
                st.error(f"❌ FALLA: El esfuerzo supera el límite de {Fy} MPa.")
            else:
                st.success(f"✅ SEGURA: La viga trabaja dentro del rango elástico.")

        with col_img:
            st.write("**Sección Transversal**")
            fig_sec, ax_sec = plt.subplots(figsize=(3,3))
            if forma == "Rectangular":
                ax_sec.add_patch(plt.Rectangle((-base/2, -altura/2), base, altura, color='gray', alpha=0.5, ec='black'))
                ax_sec.set_xlim(-base, base); ax_sec.set_ylim(-altura, altura)
            else:
                ax_sec.add_patch(plt.Circle((0,0), radio, color='gray', alpha=0.5, ec='black'))
                ax_sec.set_xlim(-radio*2, radio*2); ax_sec.set_ylim(-radio*2, radio*2)
            ax_sec.set_aspect('equal')
            st.pyplot(fig_sec)

        tabs = st.tabs(["📉 Momento Flector", "🌊 Curva de Deflexión"])
        with tabs[0]: st.pyplot(ss.show_bending_moment(show=False))
        with tabs[1]: st.pyplot(ss.show_displacement(show=False))

    except Exception as e:
        st.error(f"Error en el proceso: {e}")
