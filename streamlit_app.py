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
        # Crear el sistema estructural
        ss = SystemElements()
        
        # Añadir la viga (Elemento de 0 a L)
        ss.add_element(location=[[0, 0], [L, 0]])
        
        # Añadir Apoyos
        # Nodo 1 (id=1): Apoyo fijo (restringe x, y)
        ss.add_support_hinged(node_id=1)
        # Nodo 2 (id=2): Apoyo móvil (restringe y)
        ss.add_support_roll(node_id=2, direction=2)
        
        # Añadir Carga puntual
        # Buscamos el punto exacto. Si no hay nodo, AnaStruct lo crea.
        ss.point_load(Fy=-P, node_id=ss.find_node_id([x_p, 0]))
        
        # Resolver
        ss.solve()

        # --- MOSTRAR RESULTADOS ---
        st.subheader("📍 Reacciones")
        reacciones = ss.get_node_results_system()
        
        # Limpiar datos para tabla
        res_df = pd.DataFrame({
            "Nodo": ["Inicial (1)", "Final (2)"],
            "Reacción Vertical (kN)": [round(ss.get_node_results_system()[0]['fy'], 2), 
                                      round(ss.get_node_results_system()[1]['fy'], 2)]
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

        st.success("✅ ¡Cálculo exitoso!")

    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Tip: Asegúrate de que la carga esté sobre la viga.")
