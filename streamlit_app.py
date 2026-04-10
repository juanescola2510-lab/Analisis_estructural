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
x_p = st.sidebar.slider("Posición de la carga (m)", 0.01, L-0.01, L/2)

if st.button("🚀 Calcular Estructura"):
    try:
        ss = SystemElements()
        
        # 1. Crear viga en dos tramos
        ss.add_element(location=[[0, 0], [x_p, 0]])
        ss.add_element(location=[[x_p, 0], [L, 0]])
        
        # 2. Apoyos (Buscando IDs por coordenadas)
        id_inicio = ss.find_node_id([0, 0])
        id_fin = ss.find_node_id([L, 0])
        id_carga = ss.find_node_id([x_p, 0])
        
        ss.add_support_hinged(node_id=id_inicio)
        ss.add_support_roll(node_id=id_fin, direction=2)
        
        # 3. Carga
        ss.point_load(Fy=-P, node_id=id_carga)
        
        # 4. Resolver
        ss.solve()

        # --- REACCIONES (Método ultra-seguro) ---
        st.subheader("📍 Reacciones")
        
        reacciones_lista = []
        for nid in [id_inicio, id_fin]:
            res = ss.get_node_results_system(node_id=nid)
            # Si no encuentra 'fy', usamos 0.0 como respaldo
            val_fy = res.get('fy', 0.0)
            label = "Inicio (x=0)" if nid == id_inicio else f"Fin (x={L})"
            reacciones_lista.append({"Ubicación": label, "Reacción Vertical (kN)": round(val_fy, 2)})
        
        st.table(pd.DataFrame(reacciones_lista))

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

        st.success("✅ ¡Análisis completado!")

    except Exception as e:
        st.error(f"Error inesperado: {e}")
