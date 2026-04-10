import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Analizador 1.6.2 PRO", layout="wide")
st.title("🏗️ Analizador de Vigas (AnaStruct 1.6.2)")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Configuración de la Viga")
L = st.sidebar.slider("Longitud total (m)", 1.0, 30.0, 10.0)

st.sidebar.subheader("🗜️ Tipos de Apoyo")
tipo_izq = st.sidebar.selectbox("Apoyo Izquierdo (x=0)", ["Fijo", "Empotrado", "Libre"])
tipo_der = st.sidebar.selectbox("Apoyo Derecho (x=L)", ["Móvil", "Fijo", "Empotrado", "Libre"])

st.sidebar.subheader("⚖️ Carga Puntual")
P = st.sidebar.number_input("Magnitud P (kN)", value=10.0)
x_p = st.sidebar.slider("Posición de la carga (m)", 0.05, L-0.05, L/2)

# Botón principal
if st.button("🚀 Calcular Estructura", use_container_width=True):
    try:
        # Inicializar sistema
        ss = SystemElements()
        
        # 1. Definición de Geometría (Nodo 1: 0, Nodo 2: Carga, Nodo 3: L)
        ss.add_element(location=[[0, 0], [x_p, 0]])
        ss.add_element(location=[[x_p, 0], [L, 0]])
        
        # 2. Asignación de Apoyos
        # Izquierdo (Nodo 1)
        if tipo_izq == "Fijo": ss.add_support_hinged(node_id=1)
        elif tipo_izq == "Empotrado": ss.add_support_fixed(node_id=1)
        
        # Derecho (Nodo 3)
        if tipo_der == "Móvil": ss.add_support_roll(node_id=3, direction=2)
        elif tipo_der == "Fijo": ss.add_support_hinged(node_id=3)
        elif tipo_der == "Empotrado": ss.add_support_fixed(node_id=3)

        # 3. Aplicar Carga y Resolver
        ss.point_load(Fy=-P, node_id=2)
        ss.solve()

        # --- SECCIÓN 1: DIAGRAMA DE CUERPO LIBRE (DCL) ---
        st.header("📐 1. Diagrama de Cuerpo Libre")
        col_dcl, col_info = st.columns([2, 1])
        
        with col_dcl:
            fig_dcl = ss.show_structure(show=False)
            plt.title("Esquema de la Estructura")
            st.pyplot(fig_dcl)
            plt.close(fig_dcl)
            
        with col_info:
            st.write("**Resumen del Modelo:**")
            st.write(f"- Longitud: {L} m")
            st.write(f"- Carga: {P} kN en x = {x_p} m")
            st.write(f"- Apoyo Izq: {tipo_izq}")
            st.write(f"- Apoyo Der: {tipo_der}")

        # --- SECCIÓN 2: REACCIONES ---
        st.header("📍 2. Reacciones en Apoyos")
        resultados = ss.get_node_results_system()
        filas = []
        for r in resultados:
            node_id = r.get('id')
            if node_id in [1, 3]:
                val_fy = r.get('fy', 0.0)
                reaccion_final = abs(val_fy) 
                label = "Izquierdo (x=0)" if node_id == 1 else f"Derecho (x={L})"
                filas.append({
                    "Ubicación": label,
                    "Reacción Vertical": f"{round(reaccion_final, 2)} kN"
                })
        
        if filas:
            st.table(pd.DataFrame(filas))

        # --- SECCIÓN 3: DIAGRAMAS MECÁNICOS ---
        st.header("📊 3. Diagramas de Esfuerzos")
        tab1, tab2, tab3 = st.tabs(["Corte (V)", "Momento (M)", "Deflexión (δ)"])
        
        with tab1:
            fig_v = ss.show_shear_force(show=False)
            st.pyplot(fig_v)
            plt.close(fig_v)
            
        with tab2:
            fig_m = ss.show_bending_moment(show=False)
            st.pyplot(fig_m)
            plt.close(fig_m)
            
        with tab3:
            fig_d = ss.show_displacement(show=False)
            st.pyplot(fig_d)
            plt.close(fig_d)

    except Exception as e:
        st.error(f"Error en el cálculo: {e}")
        st.warning("Asegúrate de que la estructura no sea hipostática (inestable).")
