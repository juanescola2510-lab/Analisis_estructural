import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Analizador Estructural v1.6.2", layout="wide")
st.title("🏗️ Analizador de Vigas (AnaStruct 1.6.2)")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Configuración")
L = st.sidebar.slider("Longitud de la viga (m)", 1.0, 30.0, 10.0)

st.sidebar.subheader("🗜️ Apoyos")
tipo_izq = st.sidebar.selectbox("Apoyo Izquierdo (x=0)", ["Fijo", "Empotrado", "Libre"])
tipo_der = st.sidebar.selectbox("Apoyo Derecho (x=L)", ["Móvil", "Fijo", "Empotrado", "Libre"])

st.sidebar.subheader("⚖️ Carga Puntual")
P = st.sidebar.number_input("Magnitud P (kN)", value=10.0)
x_p = st.sidebar.slider("Posición x (m)", 0.1, L-0.1, L/2)

if st.button("🚀 Calcular Estructura", use_container_width=True):
    try:
        ss = SystemElements()
        
        # 1. Construcción de geometría (Dos tramos para asegurar nodo en carga)
        ss.add_element(location=[[0, 0], [x_p, 0]])
        ss.add_element(location=[[x_p, 0], [L, 0]])
        
        # 2. Asignación de Apoyos (IDs fijos 1 y 3)
        if tipo_izq == "Fijo": ss.add_support_hinged(node_id=1)
        elif tipo_izq == "Empotrado": ss.add_support_fixed(node_id=1)
        
        if tipo_der == "Móvil": ss.add_support_roll(node_id=3, direction=2)
        elif tipo_der == "Fijo": ss.add_support_hinged(node_id=3)
        elif tipo_der == "Empotrado": ss.add_support_fixed(node_id=3)

        # 3. Carga y Resolución
        ss.point_load(Fy=-P, node_id=2)
        ss.solve()

        # --- EXTRACCIÓN DE REACCIONES (ESPECÍFICO v1.6.2) ---
        st.subheader("📍 Reacciones Calculadas")
        
        # En v1.6.2, get_node_results_system() devuelve una lista de diccionarios 
        # pero a veces las etiquetas fallan. Usaremos el validador de seguridad:
        nodos_res = ss.get_node_results_system()
        
        filas = []
        for r in nodos_res:
            # Extraemos valores de forma segura (soporta varios formatos de la v1.6)
            x_pos = r.get('x', 0)
            f_y = r.get('fy', 0)
            m_r = r.get('m', 0)
            
            # Solo mostramos si hay reacción real (evitamos el nodo de la carga)
            if abs(f_y) > 1e-3 or abs(m_r) > 1e-3:
                filas.append({
                    "Ubicación (x)": f"{round(x_pos, 2)} m",
                    "Vertical (kN)": round(f_y, 2),
                    "Momento (kNm)": round(m_r, 2)
                })
        
        if filas:
            st.table(pd.DataFrame(filas))
        else:
            # Plan B: Si la lista anterior falló, intentamos extracción directa por ID
            st.warning("Usando método de extracción directa...")
            r1 = ss.get_node_results_system(node_id=1)
            r3 = ss.get_node_results_system(node_id=3)
            st.write(f"**Reacción Izquierda:** {round(r1.get('fy', 0), 2)} kN")
            st.write(f"**Reacción Derecha:** {round(r3.get('fy', 0), 2)} kN")

        # --- DIAGRAMAS ---
        col1, col2 = st.columns(2)
        with col1:
            st.info("**Corte (V)**")
            st.pyplot(ss.show_shear_force(show=False))
        with col2:
            st.info("**Momento (M)**")
            st.pyplot(ss.show_bending_moment(show=False))

        # --- ESQUEMA ---
        st.subheader("📐 Esquema de la Viga")
        st.pyplot(ss.show_structure(show=False))

    except Exception as e:
        st.error(f"Error en el análisis: {e}")

else:
    st.info("Configura los datos y presiona Calcular.")
