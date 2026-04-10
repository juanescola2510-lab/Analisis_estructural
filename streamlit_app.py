import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Calculadora Estructural", layout="wide")
st.title("🏗️ Análisis de Vigas: Reacciones y Diagramas")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Configuración de la Viga")
L = st.sidebar.slider("Longitud de la viga (m)", 1.0, 30.0, 10.0)
P = st.sidebar.number_input("Carga Puntual (kN)", value=10.0)
x_p = st.sidebar.slider("Posición de la carga (m)", 0.1, L-0.1, L/2)

# --- PROCESO DE CÁLCULO ---
if st.button("🚀 Calcular Estructura", use_container_width=True):
    try:
        # 1. Crear el sistema
        ss = SystemElements()
        
        # 2. Construir la viga en dos tramos
        ss.add_element(location=[[0, 0], [x_p, 0]])
        ss.add_element(location=[[x_p, 0], [L, 0]])
        
        # 3. Definir Apoyos usando coordenadas exactas
        ss.add_support_hinged(node_id=ss.find_node_id([0, 0])) 
        ss.add_support_roll(node_id=ss.find_node_id([L, 0]), direction=2)
        
        # 4. Aplicar Carga puntual
        ss.point_load(Fy=-P, node_id=ss.find_node_id([x_p, 0]))
        
        # 5. Resolver sistema
        ss.solve()

        # --- SECCIÓN DE REACCIONES (MÉTODO ROBUSTO) ---
        st.subheader("📍 Valores de las Reacciones")
        
        # Obtenemos todos los resultados de los nodos
        nodos_res = ss.get_node_results_system()
        reacciones_finales = []

        for nodo in nodos_res:
            # Solo nos interesan los nodos que tienen una fuerza de reacción vertical (fy)
            # y que están en las posiciones de los apoyos (0 o L)
            fuerza_y = nodo.get('fy', 0)
            if abs(fuerza_y) > 0.001:
                pos_x = nodo.get('x', 0)
                label = "Apoyo Izquierdo (x=0)" if abs(pos_x) < 0.01 else f"Apoyo Derecho (x={L})"
                reacciones_finales.append({
                    "Ubicación": label,
                    "Reacción Vertical (kN)": round(fuerza_y, 2)
                })

        if reacciones_finales:
            st.table(pd.DataFrame(reacciones_finales))
        else:
            st.warning("El sistema no detectó reacciones verticales. Revisa los apoyos.")
        
        # --- SECCIÓN DE DIAGRAMAS ---
        st.subheader("📈 Diagramas Estructurales")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("**Fuerza Cortante (V)**")
            st.pyplot(ss.show_shear_force(show=False))
            
        with col2:
            st.info("**Momento Flector (M)**")
            st.pyplot(ss.show_bending_moment(show=False))

    except Exception as e:
        st.error(f"Error técnico: {e}")
        st.info("Intenta mover ligeramente el control de la posición de la carga.")

else:
    st.info("👋 Ajusta los valores y presiona 'Calcular'.")
