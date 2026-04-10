import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- BLOQUE DE IMPORTACIÓN INTELIGENTE ---
try:
    from PyNite import FEModel3D
except ImportError:
    try:
        from pynite import FEModel3D
    except ImportError:
        try:
            from pynitefea import FEModel3D
        except ImportError:
            st.error("❌ No se encontró la librería estructural. Verifica que 'pynitefea' esté en requirements.txt")

# Configuración de la interfaz
st.set_page_config(page_title="Analizador de Vigas", layout="wide")
st.title("🏗️ Analizador Estructural Interactivo")
st.write("Configura la viga y obtén reacciones y diagramas al instante.")

# --- BARRA LATERAL: ENTRADA DE DATOS ---
st.sidebar.header("⚙️ Parámetros")
longitud_viga = st.sidebar.slider("Longitud (m)", 1.0, 30.0, 10.0)
magnitud_carga = st.sidebar.number_input("Carga Puntual (kN)", value=20.0)
posicion_carga = st.sidebar.slider("Posición de la carga (m)", 0.0, longitud_viga, longitud_viga/2)

# --- PROCESO DE CÁLCULO ---
if st.button("🚀 Calcular Estructura", use_container_width=True):
    try:
        # 1. Inicializar Modelo
        viga_model = FEModel3D()
        
        # 2. Definir Nodos (Inicio y Fin)
        viga_model.add_node('N1', 0, 0, 0)
        viga_model.add_node('N2', longitud_viga, 0, 0)
        
        # 3. Material y Sección Estándar (Requerido por PyNite)
        viga_model.add_material('Acero', 200e6, 77e6, 0.3, 78.5)
        viga_model.add_section('Sec1', 0.1, 0.01, 0.01, 0.02)
        viga_model.add_member('M1', 'N1', 'N2', 'Acero', 'Sec1')
        
        # 4. Definir Apoyos (N1: Apoyo Fijo, N2: Apoyo Móvil)
        viga_model.def_support('N1', True, True, True, True, True, True)
        viga_model.def_support('N2', False, True, True, False, False, False)
        
        # 5. Aplicar Carga puntual (FY negativa = fuerza hacia abajo)
        viga_model.add_member_pt_load('M1', 'FY', -magnitud_carga, posicion_carga)
        
        # 6. Ejecutar Análisis Estructural
        viga_model.analyze()

        # --- MOSTRAR RESULTADOS ---
        col_res, col_plt = st.columns([1, 2])

        with col_res:
            st.subheader("📍 Reacciones")
            res_data = {
                "Punto de Apoyo": ["Izquierdo (N1)", "Derecho (N2)"],
                "Reacción Vertical (kN)": [
                    round(viga_model.nodes['N1'].RxnFY, 2), 
                    round(viga_model.nodes['N2'].RxnFY, 2)
                ],
                "Momento en Apoyo (kN-m)": [
                    round(viga_model.nodes['N1'].RxnMZ, 2), 
                    round(viga_model.nodes['N2'].RxnMZ, 2)
                ]
            }
            st.table(pd.DataFrame(res_data))

        with col_plt:
            st.subheader("📈 Diagramas de Diseño")
            fig, (ax_v, ax_m) = plt.subplots(2, 1, figsize=(10, 8))
            
            member = viga_model.members['M1']
            steps = 100
            x_range = [i * longitud_viga / steps for i in range(steps + 1)]
            v_vals = [member.shear('FY', x) for x in x_range]
            m_vals = [member.moment('MZ', x) for x in x_range]

            # Gráfico Cortante (V)
            ax_v.plot(x_range, v_vals, color='navy', lw=2)
            ax_v.fill_between(x_range, v_vals, color='navy', alpha=0.1)
            ax_v.set_ylabel("Cortante (kN)")
            ax_v.grid(True, linestyle='--')
            ax_v.axhline(0, color='black', lw=1)

            # Gráfico Momento (M)
            ax_m.plot(x_range, m_vals, color='darkred', lw=2)
            ax_m.fill_between(x_range, m_vals, color='darkred', alpha=0.1)
            ax_m.set_ylabel("Momento (kN-m)")
            ax_m.set_xlabel("Distancia (m)")
            ax_m.grid(True, linestyle='--')
            ax_m.axhline(0, color='black', lw=1)

            st.pyplot(fig)
            
        st.success("✅ Análisis estructural completado con éxito.")

    except Exception as error:
        st.error(f"Error durante el cálculo: {error}")

else:
    st.info("👋 Ajusta los datos en la barra lateral y presiona 'Calcular' para ver los resultados.")
