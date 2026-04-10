import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Analizador Estructural PRO", layout="wide")
st.title("🏗️ Analizador de Vigas Multi-Carga")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Geometría y Apoyos")
L = st.sidebar.slider("Longitud total (m)", 1.0, 30.0, 10.0)

tipo_izq = st.sidebar.selectbox("Apoyo Izquierdo (x=0)", ["Fijo", "Empotrado", "Libre"])
tipo_der = st.sidebar.selectbox("Apoyo Derecho (x=L)", ["Móvil", "Fijo", "Empotrado", "Libre"])

# --- SECCIÓN DE CARGAS (DINÁMICA) ---
st.header("⚖️ Configuración de Cargas")
col_p, col_q = st.columns(2)

with col_p:
    st.subheader("Cargas Puntuales")
    df_puntuales = st.data_editor(
        pd.DataFrame([{"x": L/2, "P (kN)": 10.0}]),
        num_rows="dynamic",
        key="puntuales"
    )

with col_q:
    st.subheader("Cargas Distribuidas")
    df_distribuidas = st.data_editor(
        pd.DataFrame([{"x_inicio": 0.0, "x_fin": L, "q (kN/m)": 5.0}]),
        num_rows="dynamic",
        key="distribuidas"
    )

# --- PROCESAMIENTO Y CÁLCULO ---
if st.button("🚀 Calcular Estructura Combinada", use_container_width=True):
    try:
        ss = SystemElements()
        
        # 1. Crear la geometría base (un solo elemento de 0 a L para simplificar)
        # Nota: AnaStruct subdivide internamente al aplicar cargas
        ss.add_element(location=[[0, 0], [L, 0]])
        
        # 2. Aplicar Apoyos
        if tipo_izq == "Fijo": ss.add_support_hinged(node_id=1)
        elif tipo_izq == "Empotrado": ss.add_support_fixed(node_id=1)
        
        # El nodo final por defecto es el 2 al crear un solo elemento
        n_final = 2
        if tipo_der == "Móvil": ss.add_support_roll(node_id=n_final, direction=2)
        elif tipo_der == "Fijo": ss.add_support_hinged(node_id=n_final)
        elif tipo_der == "Empotrado": ss.add_support_fixed(node_id=n_final)

        # 3. Aplicar Cargas Puntuales
        for _, row in df_puntuales.iterrows():
            if 0 <= row["x"] <= L:
                ss.point_load(Fy=-row["P (kN)"], x=row["x"])

        # 4. Aplicar Cargas Distribuidas
        for _, row in df_distribuidas.iterrows():
            xi, xf = row["x_inicio"], row["x_fin"]
            if xi < xf:
                # q_load en AnaStruct se aplica a elementos. 
                # Al usar x= en point_load, AnaStruct divide la viga automáticamente.
                ss.q_load(q=-row["q (kN/m)"], element_id=1) # Simplificado para viga continua

        ss.solve()

        # --- VISUALIZACIÓN ---
        st.header("📐 Resultados")
        
        tabs = st.tabs(["DCL", "Corte (V)", "Momento (M)", "Deflexión"])
        
        with tabs[0]:
            st.subheader("Diagrama de Cuerpo Libre")
            fig = ss.show_structure(show=False)
            st.pyplot(fig)
            plt.close(fig)

        with tabs[1]:
            st.subheader("Diagrama de Fuerza Cortante")
            fig_v = ss.show_shear_force(show=False)
            st.pyplot(fig_v)
            plt.close(fig_v)

        with tabs[2]:
            st.subheader("Diagrama de Momento Flector")
            fig_m = ss.show_bending_moment(show=False)
            st.pyplot(fig_m)
            plt.close(fig_m)

        with tabs[3]:
            st.subheader("Curva de Deflexión")
            fig_d = ss.show_displacement(show=False)
            st.pyplot(fig_d)
            plt.close(fig_d)

    except Exception as e:
        st.error(f"Hubo un error en el cálculo: {e}")
        st.info("Tip: Asegúrate de que los valores de X estén dentro del rango de la viga.")
