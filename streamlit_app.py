import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd

# Configuración
st.set_page_config(page_title="Analizador Pro v1.3", layout="wide")
st.title("🏗️ Analizador Estructural: Cargas, Apoyos y Deformada")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Configuración")
L = st.sidebar.slider("Longitud de la viga (m)", 1.0, 30.0, 10.0)

st.sidebar.subheader("🗜️ Tipos de Apoyos")
tipo_izq = st.sidebar.selectbox("Apoyo Izquierdo (x=0)", ["Fijo", "Empotrado", "Libre"])
tipo_der = st.sidebar.selectbox("Apoyo Derecho (x=L)", ["Móvil (Rodillo)", "Fijo", "Empotrado", "Libre"])

st.sidebar.subheader("⚖️ Cargas")
usa_p = st.sidebar.checkbox("Carga Puntual", value=True)
if usa_p:
    P = st.sidebar.number_input("Magnitud P (kN)", value=10.0)
    x_p = st.sidebar.slider("Posición x (m)", 0.0, L, L/2)

usa_q = st.sidebar.checkbox("Carga Distribuida")
if usa_q:
    q_val = st.sidebar.number_input("Carga q (kN/m)", value=5.0)

# --- PROCESO DE CÁLCULO ---
if st.button("🚀 Calcular Estructura", use_container_width=True):
    try:
        ss = SystemElements()
        x_p_adj = x_p if 0 < x_p < L else (0.01 if x_p == 0 else L - 0.01)

        # 1. Geometría
        if usa_p:
            ss.add_element(location=[[0, 0], [x_p_adj, 0]])
            ss.add_element(location=[[x_p_adj, 0], [L, 0]])
        else:
            ss.add_element(location=[[0, 0], [L, 0]])
        
        # 2. Apoyos
        id_izq, id_der = ss.find_node_id([0, 0]), ss.find_node_id([L, 0])
        if tipo_izq == "Fijo": ss.add_support_hinged(node_id=id_izq)
        elif tipo_izq == "Empotrado": ss.add_support_fixed(node_id=id_izq)
        if tipo_der == "Móvil (Rodillo)": ss.add_support_roll(node_id=id_der, direction=2)
        elif tipo_der == "Fijo": ss.add_support_hinged(node_id=id_der)
        elif tipo_der == "Empotrado": ss.add_support_fixed(node_id=id_der)

        # 3. Cargas
        if usa_p: ss.point_load(Fy=-P, node_id=ss.find_node_id([x_p_adj, 0]))
        if usa_q:
            for i in range(1, len(ss.element_map) + 1): ss.q_load(q=-q_val, element_id=i)

        # 4. Resolver
        ss.solve()

        # --- VISUALIZACIÓN ---
        st.subheader("📐 Esquema, Reacciones y Deformada")
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.info("Estructura y Reacciones")
            st.pyplot(ss.show_structure(show=False))
        with col_v2:
            st.info("Deformada (Pandeo exagerado)")
            st.pyplot(ss.show_displacement(show=False))

        st.subheader("📈 Diagramas de Diseño")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Fuerza Cortante (V)**")
            st.pyplot(ss.show_shear_force(show=False))
        with col2:
            st.write("**Momento Flector (M)**")
            st.pyplot(ss.show_bending_moment(show=False))

        # --- TABLA DE RESULTADOS ---
        st.subheader("📍 Resumen Numérico")
        reacciones = ss.get_node_results_system()
        res_list = [{"Posición": f"{round(r['x'], 2)} m", "Vertical (kN)": round(r.get('fy', 0), 2), "Momento (kNm)": round(r.get('m', 0), 2)} 
                    for r in reacciones if abs(r.get('fy', 0)) > 0.01 or abs(r.get('m', 0)) > 0.01]
        st.table(pd.DataFrame(res_list))

    except Exception as e:
        st.error(f"Error: {e}")
