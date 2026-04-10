import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd

# Configuración
st.set_page_config(page_title="Analizador 1.6.2", layout="wide")
st.title("🏗️ Analizador de Vigas (AnaStruct 1.6.2)")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Configuración")
L = st.sidebar.slider("Longitud de la viga (m)", 1.0, 30.0, 10.0)

st.sidebar.subheader("🗜️ Apoyos")
tipo_izq = st.sidebar.selectbox("Apoyo Izquierdo (x=0)", ["Fijo", "Empotrado", "Libre"])
tipo_der = st.sidebar.selectbox("Apoyo Derecho (x=L)", ["Móvil", "Fijo", "Empotrado", "Libre"])

st.sidebar.subheader("⚖️ Carga Puntual")
P = st.sidebar.number_input("Magnitud P (kN)", value=10.0)
x_p = st.sidebar.slider("Posición x (m)", 0.05, L-0.05, L/2)

if st.button("🚀 Calcular Estructura", use_container_width=True):
    try:
        ss = SystemElements()
        
        # 1. Geometría en dos tramos (Nodo 1: Inicio, Nodo 2: Carga, Nodo 3: Fin)
        ss.add_element(location=[[0, 0], [x_p, 0]])
        ss.add_element(location=[[x_p, 0], [L, 0]])
        
        # 2. Apoyos
        if tipo_izq == "Fijo": ss.add_support_hinged(node_id=1)
        elif tipo_izq == "Empotrado": ss.add_support_fixed(node_id=1)
        
        if tipo_der == "Móvil": ss.add_support_roll(node_id=3, direction=2)
        elif tipo_der == "Fijo": ss.add_support_hinged(node_id=3)
        elif tipo_der == "Empotrado": ss.add_support_fixed(node_id=3)

        # 3. Carga y Resolución
        ss.point_load(Fy=-P, node_id=2)
        ss.solve()

        # --- SECCIÓN DE REACCIONES (MÉTODO COMPATIBLE 1.6.2) ---
        st.subheader("📍 Reacciones Calculadas")
        
        # Obtenemos todos los resultados del sistema
        resultados = ss.get_node_results_system()
        
        filas = []
        # Buscamos en los resultados los nodos 1 y 3 que son los apoyos
        for r in resultados:
            node_id = r.get('id')
            if node_id in [1, 3]:
                # En 1.6.2 fy es la fuerza interna, necesitamos la fuerza de reacción
                # Si fy es 0 o pequeño, buscamos si hay carga aplicada ahí
                val_fy = r.get('fy', 0.0)
                
                # Pequeño ajuste: AnaStruct a veces muestra la fuerza con signo cambiado
                # Multiplicamos por -1 para mostrar la reacción hacia ARRIBA (positiva)
                reaccion_final = abs(val_fy) 
                
                label = "Apoyo Izquierdo (x=0)" if node_id == 1 else f"Apoyo Derecho (x={L})"
                filas.append({
                    "Ubicación": label,
                    "Reacción Vertical (kN)": f"{round(reaccion_final, 2)} kN"
                })

        if filas:
            st.table(pd.DataFrame(filas))
        else:
            st.error("No se pudieron extraer los valores numéricos. Revisa los diagramas.")

        # --- DIAGRAMAS ---
        col1, col2 = st.columns(2)
        with col1:
            st.info("**Corte (V)**")
            st.pyplot(ss.show_shear_force(show=False))
        with col2:
            st.info("**Momento (M)**")
            st.pyplot(ss.show_bending_moment(show=False))

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("Configura los datos y presiona Calcular.")
