import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Analizador Pro v1.0", layout="wide")
st.title("🏗️ Analizador Estructural: Cargas y Apoyos")

# --- BARRA LATERAL: CONFIGURACIÓN ---
st.sidebar.header("⚙️ Configuración Global")
L = st.sidebar.slider("Longitud de la viga (m)", 1.0, 30.0, 10.0)

# 1. Selección de Apoyos
st.sidebar.subheader("🗜️ Tipos de Apoyos")
tipo_apoyo_izq = st.sidebar.selectbox("Apoyo Izquierdo (x=0)", ["Fijo", "Empotrado", "Libre"])
tipo_apoyo_der = st.sidebar.selectbox("Apoyo Derecho (x=L)", ["Móvil (Rodillo)", "Fijo", "Empotrado", "Libre"])

# 2. Configuración de Cargas (Uso de Pestañas)
st.sidebar.subheader("⚖️ Definir Cargas")
tab_puntual, tab_distribuida = st.sidebar.tabs(["Puntual", "Distribuida"])

with tab_puntual:
    usa_puntual = st.checkbox("Activar Carga Puntual", value=True)
    P = st.number_input("Magnitud P (kN)", value=10.0)
    x_p = st.slider("Posición x (m)", 0.0, L, L/2)

with tab_distribuida:
    usa_dist = st.checkbox("Activar Carga Distribuida")
    q = st.number_input("Carga q (kN/m)", value=5.0)
    x_q_inicio = st.number_input("Inicia en x (m)", 0.0, L, 0.0)
    x_q_fin = st.number_input("Termina en x (m)", 0.0, L, L)

# --- PROCESO DE CÁLCULO ---
if st.button("🚀 Calcular Estructura", use_container_width=True):
    try:
        ss = SystemElements()
        
        # 1. Crear elemento (viga completa)
        ss.add_element(location=[[0, 0], [L, 0]])
        
        # 2. Aplicar Apoyo Izquierdo
        id_izq = 1
        if tipo_apoyo_izq == "Fijo":
            ss.add_support_hinged(node_id=id_izq)
        elif tipo_apoyo_izq == "Empotrado":
            ss.add_support_fixed(node_id=id_izq)
            
        # 3. Aplicar Apoyo Derecho
        id_der = 2
        if tipo_apoyo_der == "Móvil (Rodillo)":
            ss.add_support_roll(node_id=id_der, direction=2)
        elif tipo_apoyo_der == "Fijo":
            ss.add_support_hinged(node_id=id_der)
        elif tipo_apoyo_der == "Empotrado":
            ss.add_support_fixed(node_id=id_der)

        # 4. Aplicar Cargas
        if usa_puntual:
            # Buscamos o insertamos nodo para la carga puntual
            ss.point_load(Fy=-P, x=x_p)
            
        if usa_dist:
            if x_q_fin > x_q_inicio:
                ss.q_load(q=-q, element_id=1, direction="element") # Simplificado para toda la viga
            else:
                st.warning("La posición final de la carga distribuida debe ser mayor a la inicial.")

        # 5. Resolver
        ss.solve()

        # --- RESULTADOS ---
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📍 Reacciones")
            reacciones = ss.get_node_results_system()
            df_reac = pd.DataFrame(reacciones)
            # Limpiamos para mostrar solo valores relevantes
            if not df_reac.empty:
                st.table(df_reac[['id', 'fx', 'fy', 'm']].rename(columns={'m': 'Momento (kNm)', 'fy': 'Vertical (kN)', 'fx': 'Horiz (kN)'}))

        with col2:
            st.subheader("📈 Diagramas")
            fig_v = ss.show_shear_force(show=False)
            st.pyplot(fig_v)
            fig_m = ss.show_bending_moment(show=False)
            st.pyplot(fig_m)

        st.success("✅ Análisis realizado. ¡Prueba combinando cargas!")

    except Exception as e:
        st.error(f"Error en el cálculo: {e}")
        st.info("Tip: Asegúrate de que la estructura sea estable (no pongas ambos apoyos como 'Libre').")

else:
    st.info("👋 Configura apoyos y cargas, luego presiona Calcular.")
