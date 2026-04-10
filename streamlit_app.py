import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Analizador Pro", layout="wide")
st.title("🏗️ Analizador Estructural: Cargas y Apoyos")

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
        
        # Ajuste de seguridad para evitar errores de punto exacto
        x_p_adj = x_p
        if x_p == 0: x_p_adj = 0.01
        if x_p == L: x_p_adj = L - 0.01

        # 1. Crear geometría
        if usa_p:
            ss.add_element(location=[[0, 0], [x_p_adj, 0]])
            ss.add_element(location=[[x_p_adj, 0], [L, 0]])
        else:
            ss.add_element(location=[[0, 0], [L, 0]])
        
        # 2. Asignar Apoyos
        id_izq = ss.find_node_id([0, 0])
        id_der = ss.find_node_id([L, 0])
        
        if tipo_izq == "Fijo": ss.add_support_hinged(node_id=id_izq)
        elif tipo_izq == "Empotrado": ss.add_support_fixed(node_id=id_izq)
            
        if tipo_der == "Móvil (Rodillo)": ss.add_support_roll(node_id=id_der, direction=2)
        elif tipo_der == "Fijo": ss.add_support_hinged(node_id=id_der)
        elif tipo_der == "Empotrado": ss.add_support_fixed(node_id=id_der)

        # 3. Aplicar Cargas
        if usa_p:
            nodo_p = ss.find_node_id([x_p_adj, 0])
            ss.point_load(Fy=-P, node_id=nodo_p)
            
        if usa_q:
            for i in range(1, len(ss.element_map) + 1):
                ss.q_load(q=-q_val, element_id=i)

        # --- SECCIÓN 1: ESQUEMA DE LA VIGA ---
        st.subheader("📐 Esquema de la Estructura")
        st.info("Aquí puedes ver la viga con sus apoyos (triángulos/rectángulos) y la posición de las cargas (flechas).")
        fig_base = ss.show_structure(show=False)
        st.pyplot(fig_base)

        # 4. Resolver
        ss.solve()

        # --- SECCIÓN 2: REACCIONES Y DIAGRAMAS ---
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📍 Reacciones")
            reacciones = ss.get_node_results_system()
            res_list = []
            for r in reacciones:
                f_vert = r.get('fy', 0.0)
                m_reac = r.get('m', 0.0)
                if abs(f_vert) > 0.01 or abs(m_reac) > 0.01:
                    res_list.append({
                        "Posición": f"{round(r['x'], 2)} m",
                        "Vertical (kN)": round(f_vert, 2),
                        "Momento (kNm)": round(m_reac, 2)
                    })
            st.table(pd.DataFrame(res_list))

        with col2:
            st.subheader("📈 Diagramas")
            tab1, tab2 = st.tabs(["Corte (V)", "Momento (M)"])
            with tab1:
                st.pyplot(ss.show_shear_force(show=False))
            with tab2:
                st.pyplot(ss.show_bending_moment(show=False))

    except Exception as e:
        st.error(f"Error: {e}")
