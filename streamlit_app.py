import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PyNite import FEModel3D

# Configuración de la interfaz
st.set_page_config(page_title="Analizador de Vigas", layout="wide")
st.title("🏗️ Analizador Estructural Interactivo")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Parámetros de la Viga")
L = st.sidebar.slider("Longitud de la viga (m)", 1.0, 30.0, 10.0)
P = st.sidebar.number_input("Carga Puntual (kN)", value=20.0)
x_p = st.sidebar.slider("Posición de la carga (m)", 0.0, L, L/2)

# --- PROCESO DE CÁLCULO ---
if st.button("🚀 Calcular Estructura", use_container_width=True):
    try:
        viga_model = FEModel3D()
        
        # 1. Nodos
        viga_model.add_node('N1', 0, 0, 0)
        viga_model.add_node('N2', L, 0, 0)
        
        # 2. Material y Sección
        viga_model.add_material('Acero', 200e6, 77e6, 0.3, 78.5)
        viga_model.add_section('Sec1', 0.1, 0.01, 0.01, 0.02)
        viga_model.add_member('M1', 'N1', 'N2', 'Acero', 'Sec1')
        
        # 3. Apoyos (N1: Fijo, N2: Móvil)
        viga_model.def_support('N1', True, True, True, True, True, True)
        viga_model.def_support('N2', False, True, True, False, False, False)
        
        # 4. Carga puntual
        viga_model.add_member_pt_load('M1', 'FY', -P, x_p)
        
        # 5. Análisis
        viga_model.analyze()

        # --- RESULTADOS ---
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📍 Reacciones")
            res_data = {
                "Punto": ["Izquierdo (N1)", "Derecho (N2)"],
                "Vertical (kN)": [round(viga_model.nodes['N1'].RxnFY, 2), round(viga_model.nodes['N2'].RxnFY, 2)],
                "Momento (kN-m)": [round(viga_model.nodes['N1'].RxnMZ, 2), round(viga_model.nodes['N2'].RxnMZ, 2)]
            }
            st.table(pd.DataFrame(res_data))

        with col2:
            st.subheader("📈 Diagramas")
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            m1 = viga_model.members['M1']
            x_vals = [i * L / 100 for i in range(101)]
            v_vals = [m1.shear('FY', x) for x in x_vals]
            m_vals = [m1.moment('MZ', x) for x in x_vals]

            ax1.plot(x_vals, v_vals, color='blue')
            ax1.set_ylabel("Corte (kN)")
            ax1.grid(True)

            ax2.plot(x_vals, m_vals, color='red')
            ax2.set_ylabel("Momento (kN-m)")
            ax2.set_xlabel("Posición (m)")
            ax2.grid(True)

            st.pyplot(fig)
            
        st.success("✅ Análisis completado.")

    except Exception as e:
        st.error(f"Error en el cálculo: {e}")
else:
    st.info("Configura los datos y presiona 'Calcular'.")
