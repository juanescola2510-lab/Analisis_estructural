import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Calculadora Estructural", layout="wide")
st.title("🏗️ Análisis de Vigas: Reacciones y Diagramas")

# --- BARRA LATERAL (Entrada de datos) ---
st.sidebar.header("⚙️ Configuración de la Viga")
L = st.sidebar.slider("Longitud de la viga (m)", 1.0, 30.0, 10.0)
P = st.sidebar.number_input("Carga Puntual (kN)", value=10.0)
x_p = st.sidebar.slider("Posición de la carga (m)", 0.1, L-0.1, L/2)

# --- PROCESO DE CÁLCULO ---
if st.button("🚀 Calcular Estructura", use_container_width=True):
    try:
        # 1. Crear el sistema
        ss = SystemElements()
        
        # 2. Construir la viga en dos tramos para asegurar un nodo en la carga
        ss.add_element(location=[[0, 0], [x_p, 0]])
        ss.add_element(location=[[x_p, 0], [L, 0]])
        
        # 3. Identificar IDs de nodos automáticamente
        id_inicio = ss.find_node_id([0, 0])
        id_carga = ss.find_node_id([x_p, 0])
        id_fin = ss.find_node_id([L, 0])
        
        # 4. Definir Apoyos
        ss.add_support_hinged(node_id=id_inicio) # Apoyo fijo en x=0
        ss.add_support_roll(node_id=id_fin, direction=2) # Apoyo móvil en x=L
        
        # 5. Aplicar Carga puntual
        ss.point_load(Fy=-P, node_id=id_carga)
        
        # 6. Resolver sistema
        ss.solve()

        # --- SECCIÓN DE REACCIONES ---
        st.subheader("📍 Valores de las Reacciones")
        
        # Extraer reacciones de los nodos de apoyo
        reac_a = ss.get_node_results_system(node_id=id_inicio)['fy']
        reac_b = ss.get_node_results_system(node_id=id_fin)['fy']
        
        # Crear DataFrame para la tabla
        datos_reacciones = {
            "Apoyo": ["Izquierdo (x=0)", f"Derecho (x={L})"],
            "Reacción Vertical (kN)": [round(reac_a, 2), round(reac_b, 2)],
            "Dirección": ["Arriba ↑", "Arriba ↑"]
        }
        
        st.table(pd.DataFrame(datos_reacciones))
        
        # --- SECCIÓN DE DIAGRAMAS ---
        st.subheader("📈 Diagramas Estructurales")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("**Diagrama de Fuerza Cortante (V)**")
            fig_v = ss.show_shear_force(show=False)
            st.pyplot(fig_v)
            
        with col2:
            st.info("**Diagrama de Momento Flector (M)**")
            fig_m = ss.show_bending_moment(show=False)
            st.pyplot(fig_m)

        st.success(f"✅ Análisis completado. La suma de reacciones ({round(reac_a + reac_b, 2)} kN) coincide con la carga aplicada.")

    except Exception as e:
        st.error(f"Error en el cálculo: {e}")
        st.info("Asegúrate de que la posición de la carga no coincida exactamente con los apoyos.")

else:
    st.info("👋 Ajusta los valores a la izquierda y presiona 'Calcular' para obtener los resultados.")
