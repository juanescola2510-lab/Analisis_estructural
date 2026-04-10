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
# Ajustamos para que la carga nunca esté exactamente en el apoyo
x_p = st.sidebar.slider("Posición de la carga (m)", 0.01, L-0.01, L/2)

if st.button("🚀 Calcular Estructura"):
    try:
        # Crear el sistema
        ss = SystemElements()
        
        # 1. Añadir elementos (Viga dividida en dos para tener un nodo en la carga)
        ss.add_element(location=[[0, 0], [x_p, 0]])
        ss.add_element(location=[[x_p, 0], [L, 0]])
        
        # 2. Añadir Apoyos en los extremos
        ss.add_support_hinged(node_id=ss.find_node_id([0, 0]))
        ss.add_support_roll(node_id=ss.find_node_id([L, 0]), direction=2)
        
        # 3. Aplicar la carga en el nodo central
        ss.point_load(Fy=-P, node_id=ss.find_node_id([x_p, 0]))
        
        # 4. Resolver el sistema
        ss.solve()

        # --- MOSTRAR RESULTADOS ---
        st.subheader("📍 Reacciones")
        
        # Obtenemos todas las reacciones del sistema
        reacciones_raw = ss.get_node_results_system()
        
        # Filtramos solo los nodos que tienen reacción en Y (fy) y creamos la tabla
        datos_tabla = []
        for res in reacciones_raw:
            if abs(res['fy']) > 1e-5: # Si la reacción no es cero
                ubicacion = "Inicio (x=0)" if res['id'] == 1 else f"Fin (x={L})"
                datos_tabla.append({
                    "Ubicación": ubicacion,
                    "Reacción Vertical (kN)": round(res['fy'], 2)
                })
        
        if datos_tabla:
            st.table(pd.DataFrame(datos_tabla))
        else:
            st.warning("No se detectaron reacciones. Revisa la configuración de apoyos.")

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

        st.success("✅ ¡Cálculo realizado con éxito!")

    except Exception as e:
        st.error(f"Error en el cálculo: {e}")
        st.info("Intenta mover ligeramente la posición de la carga.")
