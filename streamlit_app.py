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
        
        # 1. Crear geometría (Viga)
        if usa_p and 0 < x_p < L:
            # Dividimos en dos tramos para asegurar un nodo en la carga puntual
            ss.add_element(location=[[0, 0], [x_p, 0]])
            ss.add_element(location=[[x_p, 0], [L, 0]])
        else:
            # Viga de un solo tramo
            ss.add_element(location=[[0, 0], [L, 0]])
        
        # 2. Asignar Apoyos
        id_izq = ss.find_node_id([0, 0])
        id_der = ss.find_node_id([L, 0])
        
        # Lógica para apoyo izquierdo
        if tipo_izq == "Fijo": ss.add_support_hinged(node_id=id_izq)
        elif tipo_izq == "Empotrado": ss.add_support_fixed(node_id=id_izq)
            
        # Lógica para apoyo derecho
        if tipo_der == "Móvil (Rodillo)": ss.add_support_roll(node_id=id_der, direction=2)
        elif tipo_der == "Fijo": ss.add_support_hinged(node_id=id_der)
        elif tipo_der == "Empotrado": ss.add_support_fixed(node_id=id_der)

        # 3. Aplicar Cargas
        if usa_p:
            nodo_p = ss.find_node_id([x_p, 0])
            ss.point_load(Fy=-P, node_id=nodo_p)
            
        if usa_q:
            # Aplicar a todos los elementos creados
            for i in range(1, len(ss.element_map) + 1):
                ss.q_load(q=-q_val, element_id=i)

        # 4. Resolver
        ss.solve()

        # --- RESULTADOS ---
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📍 Reacciones")
            reacciones = ss.get_node_results_system()
            res_list = []
            for r in reacciones:
                # Solo mostrar nodos con reacciones significativas
                if abs(r['fy']) > 0.01 or abs(r['m']) > 0.01:
                    res_list.append({
                        "Nodo": r['id'],
                        "X (m)": r['x'],
                        "Vertical (kN)": round(r['fy'], 2),
                        "Momento (kNm)": round(r['m'], 2)
                    })
            if res_list:
                st.table(pd.DataFrame(res_list))

        with col2:
            st.subheader("📈 Diagramas")
            # Cortante
            st.write("**Fuerza Cortante (V)**")
            st.pyplot(ss.show_shear_force(show=False))
            # Momento
            st.write("**Momento Flector (M)**")
            st.pyplot(ss.show_bending_moment(show=False))

        st.success("✅ ¡Análisis completado!")

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Configura los parámetros y presiona Calcular.")
