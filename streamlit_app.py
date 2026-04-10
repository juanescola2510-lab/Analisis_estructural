import streamlit as st
from pynitefea import FEModel3D
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="Ingeniería 3D PRO", layout="wide")
st.title("🚀 Analizador Estructural 3D (Pórtico Espacial)")

# --- CONFIGURACIÓN EN BARRA LATERAL ---
with st.sidebar:
    st.header("🏗️ Dimensiones del Pórtico")
    L = st.number_input("Ancho (X) [m]", value=5.0)
    H = st.number_input("Alto (Y) [m]", value=3.5)
    D = st.number_input("Profundidad (Z) [m]", value=4.0)
    
    st.header("🛠️ Propiedades Material (Acero)")
    E = 200e9  # Modulo Elasticidad (Pa)
    G = 77e9   # Modulo Cortante (Pa)
    
    st.header("📐 Sección Transversal")
    A = st.number_input("Área [m2]", value=0.005)
    Iz = st.number_input("Inercia Iz (Fuerte) [m4]", value=1e-4, format="%.1e")
    Iy = st.number_input("Inercia Iy (Débil) [m4]", value=5e-5, format="%.1e")
    J = st.number_input("Constante Torsión [m4]", value=2e-6, format="%.1e")

# --- CARGAS ---
st.header("⚖️ Cargas en Nodos Superiores")
col1, col2 = st.columns(2)
with col1:
    fz = st.number_input("Carga Viento (Z) [kN]", value=10.0) * 1000
with col2:
    fy = st.number_input("Carga Gravedad (Y) [kN]", value=50.0) * 1000

if st.button("🚀 ANALIZAR ESTRUCTURA 3D", use_container_width=True):
    try:
        # 1. Inicializar Modelo
        model = FEModel3D()

        # 2. Definir Nodos (X, Y, Z)
        # Base
        model.add_node("N1", 0, 0, 0)
        model.add_node("N2", L, 0, 0)
        model.add_node("N3", 0, 0, D)
        model.add_node("N4", L, 0, D)
        # Techo
        model.add_node("N5", 0, H, 0)
        model.add_node("N6", L, H, 0)
        model.add_node("N7", 0, H, D)
        model.add_node("N8", L, H, D)

        # 3. Soportes (Empotrados en la base)
        for n in ["N1", "N2", "N3", "N4"]:
            model.def_support(n, True, True, True, True, True, True)

        # 4. Miembros (Columnas y Vigas)
        # Columnas
        model.add_member("C1", "N1", "N5", E, G, Iy, Iz, J, A)
        model.add_member("C2", "N2", "N6", E, G, Iy, Iz, J, A)
        model.add_member("C3", "N3", "N7", E, G, Iy, Iz, J, A)
        model.add_member("C4", "N4", "N8", E, G, Iy, Iz, J, A)
        # Vigas Techo
        model.add_member("V1", "N5", "N6", E, G, Iy, Iz, J, A)
        model.add_member("V2", "N7", "N8", E, G, Iy, Iz, J, A)
        model.add_member("V3", "N5", "N7", E, G, Iy, Iz, J, A)
        model.add_member("V4", "N6", "N8", E, G, Iy, Iz, J, A)

        # 5. Aplicar Cargas
        model.add_node_load("N5", "FY", -fy)
        model.add_node_load("N5", "FZ", fz)

        # 6. Resolver
        model.analyze()

        # --- VISUALIZACIÓN INTERACTIVA CON PLOTLY ---
        st.header("🌐 Visualización 3D")
        
        fig = go.Figure()

        # Dibujar miembros
        for m in model.members.values():
            x = [m.i_node.X, m.j_node.X]
            y = [m.i_node.Y, m.j_node.Y]
            z = [m.i_node.Z, m.j_node.Z]
            fig.add_trace(go.Scatter3d(x=x, y=z, z=y, mode='lines', line=dict(color='blue', width=4), name=m.Name))

        fig.update_layout(scene=dict(xaxis_title='X (Ancho)', yaxis_title='Z (Profundidad)', zaxis_title='Y (Altura)'))
        st.plotly_chart(fig, use_container_width=True)

        # --- RESULTADOS ---
        st.header("📊 Resultados de Reacciones")
        reacciones = []
        for n in ["N1", "N2", "N3", "N4"]:
            node = model.nodes
            reacciones.append({
                "Nodo": n,
                "Rx": round(node.RxnFX, 2),
                "Ry (Carga)": round(node.RxnFY, 2),
                "Rz": round(node.RxnFZ, 2)
            })
        st.table(pd.DataFrame(reacciones))

    except Exception as e:
        st.error(f"Error: {e}")
