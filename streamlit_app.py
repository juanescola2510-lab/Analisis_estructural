import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge

st.set_page_config(page_title="Diagrama Interactivo UNACEM", layout="wide")

st.title("🧩 Diseñador de Procesos Interactivo")
st.subheader("Mantenimiento y Operaciones - Molino Vertical")

# 1. Definición de los Nodos (Las cajas)
# Posiciones (x, y) iniciales en la pantalla
nodes = [
    StreamlitFlowNode('1', (50, 100), {'content': 'Alimentación Materia Prima'}, 'input', 'bottom', 'right'),
    StreamlitFlowNode('2', (300, 100), {'content': 'Molino Vertical (VRM)'}, 'default', 'left', 'right'),
    StreamlitFlowNode('3', (550, 50), {'content': 'Separador (Finos)'}, 'default', 'left', 'bottom'),
    StreamlitFlowNode('4', (550, 150), {'content': 'Retorno (Gruesos)'}, 'default', 'left', 'top'),
    StreamlitFlowNode('5', (800, 50), {'content': 'Silo de Cemento'}, 'output', 'left', 'top'),
]

# 2. Definición de las Conexiones (Las flechas)
edges = [
    StreamlitFlowEdge('1-2', '1', '2', animated=True),
    StreamlitFlowEdge('2-3', '2', '3', label='Flujo Aire'),
    StreamlitFlowEdge('2-4', '2', '4'),
    StreamlitFlowEdge('3-5', '3', '5', animated=True, label='Producto OK'),
    StreamlitFlowEdge('4-2', '4', '2', label='Re-molienda'),
]

# 3. Renderizar el Diagrama
st.write("---")
st.info("💡 Puedes arrastrar los nodos, hacer zoom y mover el lienzo.")

selected_id = streamlit_flow(
    'flujo_proceso_vrm', 
    nodes, 
    edges, 
    fit_view=True, 
    get_selected_id=True,
    enable_node_menu=True,
    enable_edge_menu=True
)

# 4. Interactividad: Mostrar detalles del nodo seleccionado
if selected_id:
    st.sidebar.success(f"Seleccionado: Elemento ID {selected_id}")
    # Aquí podrías añadir lógica: si selecciona "Molino", mostrar manual de mantenimiento
    if selected_id == '2':
        st.sidebar.write("**Manual del Molino:**")
        st.sidebar.info("Revisar presión hidráulica y desgaste de pista cada 500h.")

st.sidebar.divider()
st.sidebar.button("Reiniciar Diagrama")
