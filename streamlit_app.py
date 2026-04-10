import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Analizador Pro v1.0", layout="wide")
st.title("🏗️ Analizador Estructural: Cargas y Apoyos")

# --- BARRA LATERAL: CONFIGURACIÓN ---
st.sidebar.header("⚙️ Configuración Global")
L = st.sidebar.slider("Longitud de la viga (m)", 1.0, 30.0, 10.0)

# 1. Selección de Apoyos
st.sidebar.subheader("🗜️ Tipos de Apoyos")
tipo_apoyo_izq = st.sidebar.selectbox("Apoyo Izquierdo (x=0)", ["Fijo", "Empotrado", "Libre"])
tipo_apoyo_der = st.sidebar.selectbox("Apoyo Derecho (x=L)", ["Móvil (Rodillo)", "Fijo", "Empotrado", "Libre"])

# 2. Configuración de Cargas
st.sidebar.subheader("⚖️ Definir Cargas")
usa_puntual = st.sidebar.checkbox("Activar Carga Puntual", value=True)
if usa_puntual:
    P = st.sidebar.number_input("Magnitud P (kN)", value=10.0)
    x_p = st.sidebar.slider("Posición x (m)", 0.0, L, L/2)

usa_dist = st.sidebar.checkbox("Activar Carga Distribuida")
if usa_dist:
    q = st.sidebar.number_input("Carga q (kN/m)", value=5.0)

# --- PROCESO DE CÁLCULO ---
if st.button("🚀 Calcular Estructura", use_container_width=True):
    try:
        ss = SystemElements()
        
        # 1. Crear viga. Si hay carga puntual, la dividimos en dos para asegurar un nodo
        if usa_puntual and 0 < x_p < L:
            ss.add_element(location=[, [x_p, 0]])
            ss.add_element(location=[[x_p, 0], [L, 0]])
        else:
            ss.add_element(location=[, [L, 0]])
        
        # 2. Aplicar Apoyos
        id_izq = ss.find_node_id()
        id_der = ss.find_node_id([L, 0])
        
        # Izquierdo
        if tipo_apoyo_izq == "Fijo": ss.add_support_hinged(node_id=id_izq)
        elif tipo_apoyo_izq == "Empotrado": ss.add_support_fixed(node_id=id_izq)
            
        # Derecho
        if tipo_apoyo_der == "Móvil (Rodillo)": ss.add_support_roll(node_id=id_der, direction=2)
        elif tipo_apoyo_der == "Fijo": ss.add_support_hinged(node_id=id_der)
        elif tipo_apoyo_der == "Empotrado": ss.add_support_fixed(node_id=id_der)

        # 3. Aplicar Cargas
        if usa_puntual:
            id_carga = ss.find_node_id([x_p, 0])
            ss.point_load(Fy=-P, node_id=id_carga)
            
        if usa_dist:
            # Aplica carga distribuida a todos los elementos (la viga completa)
            for i in range(1, len(ss.element_map) + 1):
                ss.q_load(q=-q, element_id=i)

        # 4. Resolver
        ss.solve()

        # --- RESULTADOS ---
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📍 Reacciones")
            reacciones = ss.get_node_results_system()
            # Mostramos solo nodos con reacciones (fuerzas no nulas)
            filas = []
            for r in reacciones:
                if abs(r['fy']) > 0.1 or abs(r['m']) > 0.1:
                    filas.append({
                        "Nodo": r['id'],
                        "X (m)": r['x'],
                        "Vertical (kN)": round(r['fy'], 2),
                        "Momento (kNm)": round(r['m'], 2)
                    })
            if filas:
                st.table(pd.DataFrame(filas))

        with col2:
            st.subheader("📈 Diagramas")
            st.pyplot(ss.show_shear_force(show=False))
            st.pyplot(ss.show_bending_moment(show=False))

        st.success("✅ ¡Análisis completado con éxito!")

    except Exception as e:
        st.error(f"Error en el cálculo: {e}")
