import streamlit as st
from anastruct import SystemElements
import matplotlib.pyplot as plt
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Analizador Estructural PRO", layout="wide")
st.title("🏗️ Analizador de Vigas (Cargas y Momentos)")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Geometría y Apoyos")
L = st.sidebar.number_input("Longitud total de la viga (m)", min_value=0.1, max_value=500.0, value=10.0, step=0.01, format="%.2f")

tipo_izq = st.sidebar.selectbox("Apoyo Izquierdo (x=0)", ["Fijo", "Empotrado", "Libre"])
tipo_der = st.sidebar.selectbox("Apoyo Derecho (x=L)", ["Móvil", "Fijo", "Empotrado", "Libre"])

# --- SECCIÓN DE CARGAS ---
st.header("⚖️ Configuración de Cargas y Momentos")
col_p, col_q, col_m = st.columns(3)

with col_p:
    st.subheader("📍 Cargas Puntuales")
    df_puntuales = st.data_editor(
        pd.DataFrame([{"x": L/2, "P (kN)": 10.0}]),
        num_rows="dynamic", key="puntuales", use_container_width=True
    )

with col_q:
    st.subheader("📏 Cargas Distribuidas")
    df_distribuidas = st.data_editor(
        pd.DataFrame([{"x_inicio": 0.0, "x_fin": L, "q (kN/m)": 5.0}]),
        num_rows="dynamic", key="distribuidas", use_container_width=True
    )

with col_m:
    st.subheader("🔄 Momentos Puntuales")
    st.caption("Sentido horario (+), Anti-horario (-)")
    df_momentos = st.data_editor(
        pd.DataFrame([{"x": L/2, "M (kNm)": 0.0}]),
        num_rows="dynamic", key="momentos", use_container_width=True
    )

# --- PROCESAMIENTO Y CÁLCULO ---
if st.button("🚀 Calcular Estructura Completa", use_container_width=True):
    try:
        ss = SystemElements()
        
        # 1. Limpieza y filtrado de datos (Ignorar Nones y ceros)
        p_validas = df_puntuales.dropna().loc[df_puntuales["P (kN)"] != 0]
        q_validas = df_distribuidas.dropna().loc[df_distribuidas["q (kN/m)"] != 0]
        m_validas = df_momentos.dropna().loc[df_momentos["M (kNm)"] != 0]
        
        # 2. Identificar todos los puntos críticos para segmentar la viga
        puntos_x = {0.0, float(L)}
        for x in p_validas["x"]: puntos_x.add(float(x))
        for x in m_validas["x"]: puntos_x.add(float(x))
        for _, row in q_validas.iterrows():
            puntos_x.add(float(row["x_inicio"]))
            puntos_x.add(float(row["x_fin"]))
        
        # Filtrar puntos fuera de la viga y ordenar
        puntos_ordenados = sorted([x for x in puntos_x if 0 <= x <= L])
        
        # 3. Crear elementos
        for i in range(len(puntos_ordenados) - 1):
            ss.add_element(location=[[puntos_ordenados[i], 0], [puntos_ordenados[i+1], 0]])
        
        # 4. Apoyos
        n_final = len(puntos_ordenados)
        if tipo_izq == "Fijo": ss.add_support_hinged(node_id=1)
        elif tipo_izq == "Empotrado": ss.add_support_fixed(node_id=1)
        if tipo_der == "Móvil": ss.add_support_roll(node_id=n_final, direction=2)
        elif tipo_der == "Fijo": ss.add_support_hinged(node_id=n_final)
        elif tipo_der == "Empotrado": ss.add_support_fixed(node_id=n_final)

        # 5. Aplicar Cargas Puntuales
        for _, row in p_validas.iterrows():
            idx = puntos_ordenados.index(float(row["x"])) + 1
            ss.point_load(Fy=-float(row["P (kN)"]), node_id=idx)

        # 6. Aplicar Momentos (NUEVO)
        for _, row in m_validas.iterrows():
            idx = puntos_ordenados.index(float(row["x"])) + 1
            # AnaStruct usa sentido anti-horario como positivo, ajustamos según convención estándar
            ss.moment_load(Ty=float(row["M (kNm)"]), node_id=idx)

        # 7. Aplicar Cargas Distribuidas
        for _, row in q_validas.iterrows():
            xi, xf, val_q = float(row["x_inicio"]), float(row["x_fin"]), float(row["q (kN/m)"])
            for i in range(len(puntos_ordenados) - 1):
                p_mediano = (puntos_ordenados[i] + puntos_ordenados[i+1]) / 2
                if xi <= p_mediano <= xf:
                    ss.q_load(q=-val_q, element_id=i+1)

        ss.solve()

        # --- VISUALIZACIÓN ---
        st.header("📊 Resultados")
        tabs = st.tabs(["📐 DCL", "📉 Cortante", "📈 Momento", "🌊 Deflexión"])
        
        with tabs[0]: st.pyplot(ss.show_structure(show=False))
        with tabs[1]: st.pyplot(ss.show_shear_force(show=False))
        with tabs[2]: st.pyplot(ss.show_bending_moment(show=False))
        with tabs[3]: st.pyplot(ss.show_displacement(show=False))

        # Tabla de Reacciones
        st.subheader("📍 Reacciones")
        reacciones = ss.get_node_results_system()
        res_list = []
        for r in reacciones:
            if r['id'] in [1, n_final]:
                ubi = "Izquierdo (x=0)" if r['id'] == 1 else f"Derecho (x={L})"
                res_list.append({
                    "Ubicación": ubi, 
                    "Fuerza Vertical (kN)": round(abs(r.get('fy', 0)), 4),
                    "Momento Reacción (kNm)": round(r.get('m', 0), 4)
                })
        st.table(res_list)

    except Exception as e:
        st.error(f"Error: {e}")
