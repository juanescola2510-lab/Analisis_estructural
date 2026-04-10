import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd

# Configuración de la página
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
        
        # 1. Crear viga en dos tramos (Nodo 1: Inicio, Nodo 2: Carga, Nodo 3: Fin)
        ss.add_element(location=[[0, 0], [x_p, 0]])
        ss.add_element(location=[[x_p, 0], [L, 0]])
        
        # 2. Añadir apoyos en los extremos fijos (IDs 1 y 3)
        ss.add_support_hinged(node_id=1)
        ss.add_support_roll(node_id=3, direction=2)
        
        # 3. Añadir carga en el nodo central (ID 2)
        ss.point_load(Fy=-P, node_id=2)
        
        # 4. Resolver
        ss.solve()

        # --- SECCIÓN DE REACCIONES (USANDO IDS DIRECTOS) ---
        st.subheader("📍 Valores de las Reacciones")
        
        # Obtenemos fy directamente de los nodos de apoyo
        # Usamos .get para que si no existe no explote, pero con IDs fijos es seguro
        res_izq = ss.get_node_results_system(node_id=1)
        res_der = ss.get_node_results_system(node_id=3)
        
        r_izq = res_izq.get('fy', 0) if isinstance(res_izq, dict) else res_izq[0].get('fy', 0)
        r_der = res_der.get('fy', 0) if isinstance(res_der, dict) else res_der[0].get('fy', 0)
        
        # Crear tabla
        datos_reacciones = [
            {"Ubicación": "Apoyo Izquierdo (x=0)", "Reacción Vertical (kN)": round(r_izq, 2)},
            {"Ubicación": f"Apoyo Derecho (x={L})", "Reacción Vertical (kN)": round(r_der, 2)}
        ]
        st.table(pd.DataFrame(datos_reacciones))
        
        # --- SECCIÓN DE DIAGRAMAS ---
        st.subheader("📈 Diagramas Estructurales")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("**Fuerza Cortante (V)**")
            st.pyplot(ss.show_shear_force(show=False))
            
        with col2:
            st.info("**Momento Flector (M)**")
            st.pyplot(ss.show_bending_moment(show=False))

        st.success(f"✅ ¡Cálculo exitoso! Equilibrio: Reacciones ({round(r_izq + r_der, 2)} kN) = Carga ({P} kN)")

    except Exception as e:
        st.error(f"Error en el cálculo: {e}")
else:
    st.info("👋 Ajusta los valores y presiona 'Calcular'.")
