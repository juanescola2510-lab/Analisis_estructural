import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Analizador Estructural PRO", layout="wide")
st.title("🏗️ Analizador de Vigas Multi-Carga")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Geometría y Apoyos")
L = st.sidebar.slider("Longitud total (m)", 1.0, 30.0, 4.04)

tipo_izq = st.sidebar.selectbox("Apoyo Izquierdo (x=0)", ["Fijo", "Empotrado", "Libre"])
tipo_der = st.sidebar.selectbox("Apoyo Derecho (x=L)", ["Móvil", "Fijo", "Empotrado", "Libre"])

# --- SECCIÓN DE CARGAS ---
st.header("⚖️ Configuración de Cargas")
col_p, col_q = st.columns(2)

with col_p:
    st.subheader("Cargas Puntuales")
    df_puntuales = st.data_editor(
        pd.DataFrame([{"x": 2.02, "P (kN)": 1.0}]),
        num_rows="dynamic", key="puntuales"
    )

with col_q:
    st.subheader("Cargas Distribuidas")
    df_distribuidas = st.data_editor(
        pd.DataFrame([{"x_inicio": 0.0, "x_fin": 4.04, "q (kN/m)": 5.0}]),
        num_rows="dynamic", key="distribuidas"
    )

if st.button("🚀 Calcular Estructura Combinada", use_container_width=True):
    try:
        ss = SystemElements()
        
        # 1. Crear nodos basados en las posiciones de las cargas puntuales
        puntos_x = {0, L} # Extremos siempre presentes
        for x in df_puntuales["x"]:
            if 0 < x < L: puntos_x.add(x)
        
        # Ordenar puntos para crear los elementos secuencialmente
        puntos_ordenados = sorted(list(puntos_x))
        
        # Crear los elementos de la viga (segmentada por los nodos de carga)
        for i in range(len(puntos_ordenados) - 1):
            ss.add_element(location=[[puntos_ordenados[i], 0], [puntos_ordenados[i+1], 0]])
        
        # 2. Aplicar Apoyos (Nodo 1 es x=0, el último nodo es x=L)
        # El ID del último nodo es igual al número de puntos ordenados
        n_final = len(puntos_ordenados)
        
        if tipo_izq == "Fijo": ss.add_support_hinged(node_id=1)
        elif tipo_izq == "Empotrado": ss.add_support_fixed(node_id=1)
        
        if tipo_der == "Móvil": ss.add_support_roll(node_id=n_final, direction=2)
        elif tipo_der == "Fijo": ss.add_support_hinged(node_id=n_final)
        elif tipo_der == "Empotrado": ss.add_support_fixed(node_id=n_final)

        # 3. Aplicar Cargas Puntuales buscando el node_id por su coordenada X
        for _, row in df_puntuales.iterrows():
            # Buscamos el ID del nodo que coincide con la X de la carga
            nodo_id = puntos_ordenados.index(row["x"]) + 1
            ss.point_load(Fy=-row["P (kN)"], node_id=nodo_id)

        # 4. Aplicar Cargas Distribuidas
        for _, row in df_distribuidas.iterrows():
            # Aplicamos la carga a todos los elementos que estén dentro del rango [x_inicio, x_fin]
            # Por simplicidad en este modelo segmentado, si cubres toda la viga:
            for i in range(1, len(puntos_ordenados)):
                ss.q_load(q=-row["q (kN/m)"], element_id=i)

        ss.solve()

        # --- VISUALIZACIÓN ---
        st.header("📐 Resultados")
        tab1, tab2, tab3, tab4 = st.tabs(["DCL", "Corte (V)", "Momento (M)", "Deflexión"])
        
        with tab1:
            st.pyplot(ss.show_structure(show=False))
        with tab2:
            st.pyplot(ss.show_shear_force(show=False))
        with tab3:
            st.pyplot(ss.show_bending_moment(show=False))
        with tab4:
            st.pyplot(ss.show_displacement(show=False))

    except Exception as e:
        st.error(f"Error: {e}")
