import streamlit as st

st.title("🛠️ Diagrama de Proceso de Molienda")

# Definir el diagrama usando lenguaje DOT
diagrama_proceso = '''
digraph {
    node [shape=box, style=filled, color=lightblue]
    
    A [label="Alimentación de Crudo"]
    B [label="Báscula de Pesaje"]
    C [label="Molino Vertical (VRM)", color=orange]
    D [label="Separador de Alta Eficiencia"]
    E [label="Filtro de Mangas"]
    F [label="Silo de Producto Terminado"]
    G [label="Retorno (Gruesos)"]

    A -> B -> C
    C -> D
    D -> E [label="Finos"]
    D -> G [label="Rechazo"]
    G -> C
    E -> F
}
'''

# Mostrar el diagrama en la app
st.graphviz_chart(diagrama_proceso)
