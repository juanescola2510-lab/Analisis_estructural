import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Analizador 2D", layout="wide")
st.title("🏗️ Análisis Estructural con AnaStruct")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Configuración")
L = st.sidebar.slider("Longitud de la viga (m)", 1.0, 20.0, 10.0)
P = st.sidebar.number_input("Carga Puntual (kN)", value=15.0)
x_p = st.sidebar.slider("Posición de la carga (m)", 0.0, L, L/2)

if st.button("🚀 Calcular Estructura"):
    try:
        # Crear el sistema
        ss = SystemElements()
        
        # 1. Añadir la viga (de 0 a L)
        ss.add_element(location=[[0, 0], [L, 0]])
        
        # 2. Añadir Apoyos
        ss.add_support_hinged(node_id=1)  # Inicio
        ss.add_support_roll(node_id=2, direction=2)  # Fin
        
        # 3. EL TRUCO: Crear un nodo justo donde está la carga para evitar el error 'NoneType'
        id_nodo_carga = ss.find_node_id([x_p, 0])
        if id_nodo_carga is None:
            # Si no existe el nodo en esa posición decimal, lo creamos dividiendo el elemento
            ss.insert_node(element_id=1, location=[x_p, 0])
            id_nodo_carga = ss.find_node_id([x_p, 0])

        # 4. Aplicar la carga en el nodo encontrado/creado
        ss.point_load(Fy=-P, node_id=id_nodo_carga)
        
        # 5. Resolver
        ss.solve()

        # --- MOSTRAR RESULTADOS ---
        st.subheader("📍 Reacciones")
        reacciones = ss.get_node_results_system()
        
        # Crear tabla de reacciones de forma segura
        nodos = [1, 2]
        fuerzas_y = [round(ss.get_node_results_system(node_id=n)['fy'], 2) for n in nodos]
        
        res_df = pd.DataFrame({
            "Ubicación": ["Apoyo Inicial (x=0)", f"Apoyo Final (x={L})"],
            "Reacción Vertical (kN)": fuerzas_y
        })
        st.table(res_df)

        # --- DIAGRAMAS ---
        st.subheader("📈 Diagramas de la Viga")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Fuerza Cortante**")
            fig_v = ss.show_shear_force(show=False)
            st.pyplot(fig_v)
            
        with col2:
            st.write("**Momento Flector**")
            fig_m = ss.show_bending_moment(show=False)
            st.pyplot(fig_m)

        st.success("✅ ¡Cálculo realizado con éxito!")

    except Exception as e:
        st.error(f"Error técnico: {e}")
