import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Analizador de Vigas", layout="wide")
st.title("🏗️ Analisis de vigas: Reacciones y Diagramas")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Configuración de la Viga")
L = st.sidebar.slider("Longitud de la viga (m)", 1.0, 30.0, 10.0)
P = st.sidebar.number_input("Carga Puntual (kN)", value=10.0)
x_p = st.sidebar.slider("Posición de la carga (m)", 0.05, L-0.05, L/2)

if st.button("🚀 Calcular Estructura", use_container_width=True):
    try:
        ss = SystemElements()
        
        # 1. Crear viga en dos tramos para asegurar nodo en la carga
        ss.add_element(location=[[0, 0], [x_p, 0]])
        ss.add_element(location=[[x_p, 0], [L, 0]])
        
        # 2. Identificar nodos de apoyo
        id_izq = ss.find_node_id([0, 0])
        id_der = ss.find_node_id([L, 0])
        id_fuerza = ss.find_node_id([x_p, 0])
        
        # 3. Añadir apoyos
        ss.add_support_hinged(node_id=id_izq)
        ss.add_support_roll(node_id=id_der, direction=2)
        
        # 4. Añadir carga
        ss.point_load(Fy=-P, node_id=id_fuerza)
        
        # 5. Resolver
        ss.solve()

        # --- SECCIÓN DE REACCIONES (MÉTODO DIRECTO) ---
        st.subheader("📍 Valores de las Reacciones")
        
        # Extraemos los resultados directamente de los IDs de los apoyos
        res_izq = ss.get_node_results_system(node_id=id_izq)
        res_der = ss.get_node_results_system(node_id=id_der)
        
        # Obtenemos el valor de 'fy' (reacción vertical)
        r_izq = res_izq.get('fy', 0)
        r_der = res_der.get('fy', 0)
        
        # Crear tabla
        datos_reacciones = [
            {"Ubicación": "Apoyo Izquierdo (x=0)", "Reacción Vertical (kN)": round(r_izq, 2)},
            {"Ubicación": f"Apoyo Derecho (x={L})", "Reacción Vertical (kN)": round(r_der, 2)}
        ]
        st.table(pd.DataFrame(datos_reacciones))
        
        # --- DIAGRAMAS ---
        st.subheader("📈 Diagramas Estructurales")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("**Fuerza Cortante (V)**")
            fig_v = ss.show_shear_force(show=False)
            st.pyplot(fig_v)
            
        with col2:
            st.info("**Momento Flector (M)**")
            fig_m = ss.show_bending_moment(show=False)
            st.pyplot(fig_m)

        st.success(f"✅ ¡Cálculo exitoso! Suma de reacciones: {round(r_izq + r_der, 2)} kN")

    except Exception as e:
        st.error(f"Error en el cálculo: {e}")
else:
    st.info("👋 Ajusta los valores y presiona 'Calcular'.")
