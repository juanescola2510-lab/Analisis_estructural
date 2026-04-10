import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd

# Configuración de la aplicación
st.set_page_config(page_title="Analizador Pro v1.2", layout="wide")
st.title("🏗️ Analizador Estructural: Cargas, Apoyos y Valores Máximos")

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
        
        # Ajuste de seguridad para evitar errores en puntos exactos
        x_p_adj = x_p
        if x_p == 0: x_p_adj = 0.01
        if x_p == L: x_p_adj = L - 0.01

        # 1. Geometría
        if usa_p:
            ss.add_element(location=[[0, 0], [x_p_adj, 0]])
            ss.add_element(location=[[x_p_adj, 0], [L, 0]])
        else:
            ss.add_element(location=[[0, 0], [L, 0]])
        
        # 2. Apoyos
        id_izq = ss.find_node_id([0, 0])
        id_der = ss.find_node_id([L, 0])
        
        if tipo_izq == "Fijo": ss.add_support_hinged(node_id=id_izq)
        elif tipo_izq == "Empotrado": ss.add_support_fixed(node_id=id_izq)
            
        if tipo_der == "Móvil (Rodillo)": ss.add_support_roll(node_id=id_der, direction=2)
        elif tipo_der == "Fijo": ss.add_support_hinged(node_id=id_der)
        elif tipo_der == "Empotrado": ss.add_support_fixed(node_id=id_der)

        # 3. Cargas
        if usa_p:
            nodo_p = ss.find_node_id([x_p_adj, 0])
            ss.point_load(Fy=-P, node_id=nodo_p)
            
        if usa_q:
            for i in range(1, len(ss.element_map) + 1):
                ss.q_load(q=-q_val, element_id=i)

        # 4. Resolver
        ss.solve()

        # --- VISUALIZACIÓN: ESQUEMA Y REACCIONES ---
        st.subheader("📐 Esquema y Reacciones")
        # annotations=True muestra los valores de carga y reacción en el dibujo
        fig_base = ss.show_structure(show=False, annotations=True)
        st.pyplot(fig_base)

        # --- VISUALIZACIÓN: DIAGRAMAS CON VALORES ---
        st.subheader("📈 Diagramas con Valores Críticos")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("**Fuerza Cortante (V) [kN]**")
            # values=True añade los números al diagrama
            fig_v = ss.show_shear_force(show=False, values=True)
            st.pyplot(fig_v)
            
        with col2:
            st.info("**Momento Flector (M) [kNm]**")
            # values=True añade los números al diagrama
            fig_m = ss.show_bending_moment(show=False, values=True)
            st.pyplot(fig_m)

        # --- TABLA DE RESULTADOS ---
        st.subheader("📍 Resumen de Reacciones")
        reacciones = ss.get_node_results_system()
        res_list = []
        for r in reacciones:
            f_v = r.get('fy', 0.0)
            m_r = r.get('m', 0.0)
            if abs(f_v) > 0.01 or abs(m_r) > 0.01:
                res_list.append({
                    "Posición": f"{round(r['x'], 2)} m",
                    "Vertical (kN)": round(f_v, 2),
                    "Momento (kNm)": round(m_r, 2)
                })
        st.table(pd.DataFrame(res_list))
        
        st.success("✅ Análisis finalizado con éxito.")

    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Verifica que no tengas una viga inestable (ej. dos apoyos libres).")
