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
        
        # 1. Crear viga en dos tramos (asegura que haya un nodo exacto en la carga)
        ss.add_element(location=[[0, 0], [x_p, 0]])
        ss.add_element(location=[[x_p, 0], [L, 0]])
        
        # 2. Añadir apoyos en los extremos exactos
        # Buscamos los nodos por posición para no fallar
        ss.add_support_hinged(node_id=ss.find_node_id([0, 0]))
        ss.add_support_roll(node_id=ss.find_node_id([L, 0]), direction=2)
        
        # 3. Añadir carga
        ss.point_load(Fy=-P, node_id=ss.find_node_id([x_p, 0]))
        
        # 4. Resolver
        ss.solve()

        # --- SECCIÓN DE REACCIONES (MÉTODO DE BÚSQUEDA POR COORDENADAS) ---
        st.subheader("📍 Valores de las Reacciones")
        
        # Obtenemos TODOS los resultados de los nodos
        todos_los_resultados = ss.get_node_results_system()
        
        r_izq, r_der = 0, 0
        
        # Recorremos los resultados buscando los nodos en x=0 y x=L
        for nodo in todos_los_resultados:
            if abs(nodo['x'] - 0) < 0.01: # Nodo en el inicio
                r_izq = nodo.get('fy', 0)
            if abs(nodo['x'] - L) < 0.01: # Nodo en el final
                r_der = nodo.get('fy', 0)
        
        # Crear tabla con los valores encontrados
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
