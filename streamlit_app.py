import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Analizador Estructural PRO", layout="wide")
st.title("🏗️ Analizador de Vigas Multi-Carga")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Geometría y Apoyos")
L = st.sidebar.slider("Longitud total (m)", 1.0, 50.0, 10.0)

tipo_izq = st.sidebar.selectbox("Apoyo Izquierdo (x=0)", ["Fijo", "Empotrado", "Libre"])
tipo_der = st.sidebar.selectbox("Apoyo Derecho (x=L)", ["Móvil", "Fijo", "Empotrado", "Libre"])

# --- SECCIÓN DE CARGAS ---
st.header("⚖️ Configuración de Cargas")
st.info("Puedes añadir varias filas. Las filas vacías serán ignoradas automáticamente.")
col_p, col_q = st.columns(2)

with col_p:
    st.subheader("📍 Cargas Puntuales")
    df_puntuales = st.data_editor(
        pd.DataFrame([{"x": L/2, "P (kN)": 10.0}]),
        num_rows="dynamic", key="puntuales", use_container_width=True
    )

with col_q:
    st.subheader("📏 Cargas Distribuidas (UDL)")
    df_distribuidas = st.data_editor(
        pd.DataFrame([{"x_inicio": 0.0, "x_fin": L, "q (kN/m)": 5.0}]),
        num_rows="dynamic", key="distribuidas", use_container_width=True
    )

# --- PROCESAMIENTO Y CÁLCULO ---
if st.button("🚀 Calcular Estructura Combinada", use_container_width=True):
    try:
        ss = SystemElements()
        
        # 1. Crear nodos basados en posiciones de cargas y apoyos
        puntos_x = {0.0, L}
        
        # Limpiar y agregar puntos de cargas puntuales
        p_validas = df_puntuales.dropna(subset=["x", "P (kN)"])
        for x in p_validas["x"]:
            if 0 <= x <= L: puntos_x.add(float(x))
            
        # Agregar puntos de inicio y fin de cargas distribuidas para segmentar bien
        q_validas = df_distribuidas.dropna(subset=["x_inicio", "x_fin", "q (kN/m)"])
        for _, row in q_validas.iterrows():
            if 0 <= row["x_inicio"] <= L: puntos_x.add(float(row["x_inicio"]))
            if 0 <= row["x_fin"] <= L: puntos_x.add(float(row["x_fin"]))
        
        puntos_ordenados = sorted(list(puntos_x))
        
        # 2. Crear los elementos segmentados
        for i in range(len(puntos_ordenados) - 1):
            ss.add_element(location=[[puntos_ordenados[i], 0], [puntos_ordenados[i+1], 0]])
        
        # 3. Aplicar Apoyos
        n_final = len(puntos_ordenados)
        if tipo_izq == "Fijo": ss.add_support_hinged(node_id=1)
        elif tipo_izq == "Empotrado": ss.add_support_fixed(node_id=1)
        
        if tipo_der == "Móvil": ss.add_support_roll(node_id=n_final, direction=2)
        elif tipo_der == "Fijo": ss.add_support_hinged(node_id=n_final)
        elif tipo_der == "Empotrado": ss.add_support_fixed(node_id=n_final)

        # 4. Aplicar Cargas Puntuales (Evitando NoneType)
        for _, row in p_validas.iterrows():
            pos_x = float(row["x"])
            val_p = float(row["P (kN)"])
            # Encontrar el ID del nodo comparando con tolerancia pequeña por decimales
            for idx, coord in enumerate(puntos_ordenados):
                if abs(coord - pos_x) < 1e-5:
                    ss.point_load(Fy=-val_p, node_id=idx + 1)

        # 5. Aplicar Cargas Distribuidas por tramos
        for _, row in q_validas.iterrows():
            xi, xf, val_q = float(row["x_inicio"]), float(row["x_fin"]), float(row["q (kN/m)"])
            # Aplicar a cada elemento que esté contenido en el rango [xi, xf]
            for i in range(len(puntos_ordenados) - 1):
                p_mediano = (puntos_ordenados[i] + puntos_ordenados[i+1]) / 2
                if xi <= p_mediano <= xf:
                    ss.q_load(q=-val_q, element_id=i+1)

        ss.solve()

        # --- VISUALIZACIÓN DE RESULTADOS ---
        st.header("📊 Resultados del Análisis")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📐 DCL", "📉 Cortante (V)", "📈 Momento (M)", "🌊 Deflexión"])
        
        with tab1:
            st.subheader("Diagrama de Cuerpo Libre")
            st.pyplot(ss.show_structure(show=False))
        with tab2:
            st.subheader("Diagrama de Fuerza Cortante (kN)")
            st.pyplot(ss.show_shear_force(show=False))
        with tab3:
            st.subheader("Diagrama de Momento Flector (kNm)")
            st.pyplot(ss.show_bending_moment(show=False))
        with tab4:
            st.subheader("Curva de Deflexión (m)")
            st.pyplot(ss.show_displacement(show=False))

        # --- REACCIONES ---
        st.subheader("📍 Reacciones en Apoyos")
        reacciones = ss.get_node_results_system()
        res_list = []
        for r in reacciones:
            if r['id'] in [1, n_final]:
                ubi = "Izquierdo (x=0)" if r['id'] == 1 else f"Derecho (x={L})"
                res_list.append({"Ubicación": ubi, "Reacción Vertical (kN)": round(abs(r.get('fy', 0)), 2)})
        st.table(res_list)

    except Exception as e:
        st.error(f"Error detectado: {e}")
        st.warning("Verifica que no haya valores incoherentes (ej: x_inicio > x_f
