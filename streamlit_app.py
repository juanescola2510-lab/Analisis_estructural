import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Asset Health Dashboard",
    page_icon="🏭",
    layout="wide"
)

# =====================================================
# FUNCIONES
# =====================================================

def calcular_salud(row):

    vib = min((row["Vib_Actual"] / row["Vib_Critica"]) * 100, 150)
    temp = min((row["Temp_Actual"] / row["Temp_Critica"]) * 100, 150)
    ultra = min((row["Ultra_Actual"] / row["Ultra_Critica"]) * 100, 150)

    riesgo = (vib + temp + ultra) / 3

    salud = max(0, 100 - (riesgo - 50))

    return round(salud, 1)

def estado_salud(valor):

    if valor >= 85:
        return "🟢 Excelente"

    elif valor >= 70:
        return "🟡 Bueno"

    elif valor >= 55:
        return "🟠 Atención"

    else:
        return "🔴 Crítico"

# =====================================================
# BASE DATOS
# =====================================================

if "equipos" not in st.session_state:

    st.session_state.equipos = pd.DataFrame(columns=[
        "Equipo",
        "Vib_Actual",
        "Vib_Critica",
        "Temp_Actual",
        "Temp_Critica",
        "Ultra_Actual",
        "Ultra_Critica"
    ])

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("Ingreso de Datos")

equipo = st.sidebar.text_input(
    "Nombre del Equipo"
)

st.sidebar.markdown("### Vibración")

vib_actual = st.sidebar.number_input(
    "Valor Actual (mm/s)",
    min_value=0.0,
    value=10.0
)

vib_critica = st.sidebar.number_input(
    "Valor Crítico (mm/s)",
    min_value=1.0,
    value=30.0
)

st.sidebar.
