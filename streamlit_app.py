import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- IMPORTACIÓN ROBUSTA ---
try:
    from PyNite import FEModel3D
except ImportError:
    try:
        from pynite import FEModel3D
    except ImportError:
        from pynitefea import FEModel3D
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
        # Usamos el objeto FEModel3D que importamos arriba
        viga_model = FEModel3D()
        
        # 1. Nodos
        viga_model.add_node('N1', 0, 0, 0)
        viga_model.add_node('N2', L, 0, 0)
        
        # 2. Material y Sección
        viga_model.add_material('Acero', 200e6, 77e6, 0.3, 78.5)
        viga_model.add_section('Sec1', 0.1, 0.01, 0.01, 0.02)
        viga_model.add_member('M1', 'N1', 'N2', 'Acero', 'Sec1')
        
        # 3. Apoyos
        viga_model.def_support('N1', True, True, True, True, True, True)
        viga_model.def_support('N2', False, True, True, False, False, False)
        
        # 4. Carga
        viga_model.add_member_pt_load('M1', 'FY', -P, x_p)
        
        # 5. Análisis
        viga_model.analyze()

        # --- RESULTADOS ---
        col_res, col_plt = st.columns([1, 2])

        with col_res:
            st.subheader("📍 Reacciones")
            res_data = {
                "Punto": ["Izquierdo (N1)", "Derecho (N2)"],
                "Vertical (kN)": [
                    round(viga_model.nodes['N1'].RxnFY, 2), 
                    round(viga_model.nodes['N2'].RxnFY, 2)
                ],
                "Momento (kN-m)": [
                    round(viga_model.nodes['N1'].RxnMZ, 2), 
                    round(viga_model.nodes['N2'].RxnMZ, 2)
                ]
            }
            st.table(pd.DataFrame(res_data))

        with col_plt:
            st.subheader("📈 Diagramas")
            fig, (ax_v, ax_m) = plt.subplots(2, 1, figsize=(10, 8))
            
            m1 = viga_model.members['M1']
            x_range = [i * L / 100 for i in range(101)]
            v_vals = [m1.shear('FY', x) for x in x_range]
            m_vals = [m1.moment('MZ', x) for x in x_range]

            ax_v.plot(x_range, v_vals, color='blue')
            ax_v.fill_between(x_range, v_vals, color='blue', alpha=0.1)
            ax_v.set_ylabel("Corte (kN)")
            ax_v.grid(True)

            ax_m.plot(x_range, m_vals, color='red')
            ax_m.fill_between(x_range, m_vals, color='red', alpha=0.1)
            ax_m.set_ylabel("Momento (kN-m)")
            ax_m.grid(True)

            st.pyplot(fig)
            
        st.success("✅ Análisis completado.")

    except Exception as e:
        st.error(f"Error en el cálculo: {e}")
        st.info("Asegúrate de que la carga esté dentro de la longitud de la viga.")

else:
    st.info("Configura los datos y presiona 'Calcular'.")
