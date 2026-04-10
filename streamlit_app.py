import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Analizador 2D", layout="wide")
st.title("🏗️ Análisis Estructural con AnaStruct")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Configuración")
L = st.sidebar.slider("Longitud de la viga (m)", 1.0, 30.0, 10.0)
P = st.sidebar.number_input("Carga Puntual (kN)", value=15.0)
x_p = st.sidebar.slider("Posición de la carga (m)", 0.01, L-0.01, L/2) # Evitamos los extremos exactos

if st.button("🚀 Calcular Estructura"):
    try:
        # Crear el sistema
        ss = SystemElements()
        
        # 1. Construir la viga en dos partes para asegurar un nodo en la carga
        # Tramo 1: Desde el inicio hasta la carga
        ss.add_element(location=[[0, 0], [x_p, 0]])
        # Tramo 2: Desde la carga hasta el final
        ss.add_element(location=[[x_p, 0], [L, 0]])
        
        # 2. Añadir Apoyos (Usando IDs de nodos fijos)
        ss.add_support_hinged(node_id=1)  # Inicio (x=0)
        ss.add_support_roll(node_id=3, direction=2)  # Fin (x=L). El nodo 3 es el final del tramo 2.
        
        # 3. Aplicar la carga en el nodo central (Nodo 2)
        ss.point_load(Fy=-P, node_id=2)
        
        # 4. Resolver
        ss.solve()

        # --- MOSTRAR RESULTADOS ---
        st.subheader("📍 Reacciones")
        
        # Obtener reacciones de forma manual para evitar errores de índice
        reac_ini = ss.get_node_results_system(node_id=1)['fy']
        reac_fin = ss.get_node_results_system(node_id=3)['fy']
        
        res_df = pd.DataFrame({
            "Ubicación": ["Apoyo Inicial (x=0)", f"Apoyo Final (x={L})"],
            "Reacción Vertical (kN)": [round(reac_ini, 2), round(reac_fin, 2)]
        })
        st.table(res_df)

        # --- DIAGRAMAS ---
        st.subheader("📈 Diagramas de la Viga")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Fuerza Cortante**")
            fig_v = ss.show_shear_force(show=False)
            # Ajuste de tamaño para Streamlit
            fig_v.set_size_inches(6, 4)
            st.pyplot(fig_v)
            
        with col2:
            st.write("**Momento Flector**")
            fig_m = ss.show_bending_moment(show=False)
            fig_m.set_size_inches(6, 4)
            st.pyplot(fig_m)

        st.success("✅ ¡Análisis completado con éxito!")

    except Exception as e:
        st.error(f"Error en el cálculo: {e}")
        st.info("Asegúrate de que la posición de la carga no sea exactamente igual a los apoyos.")
