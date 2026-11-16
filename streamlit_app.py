import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

st.set_page_config(
    page_title="Asset Health Dashboard",
    page_icon="🏭",
    layout="wide"
)

# =====================================================
# FUNCIONES
# =====================================================

def calcular_salud(vib_pct, temp_pct, ultra_pct):

    riesgo = (vib_pct + temp_pct + ultra_pct) / 3

    salud = max(0, 100 - riesgo)

    return round(salud, 1)


def clasificar(salud):

    if salud >= 70:
        return "🟢 Normal"

    elif salud >= 50:
        return "🟡 Atención"

    elif salud >= 30:
        return "🟠 Alarma"

    else:
        return "🔴 Crítico"


# =====================================================
# BASE DE DATOS
# =====================================================

if "historico" not in st.session_state:

    st.session_state.historico = pd.DataFrame(
        columns=[
            "Fecha",
            "Equipo",
            "Vib_Actual",
            "Vib_Limite",
            "Temp_Actual",
            "Temp_Limite",
            "Ultra_Actual",
            "Ultra_Limite"
        ]
    )

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("Ingreso de Inspección")

fecha = st.sidebar.date_input(
    "Fecha",
    date.today()
)

equipo = st.sidebar.text_input(
    "Equipo"
)

st.sidebar.markdown("### Vibración")

vib_actual = st.sidebar.number_input(
    "Vibración Actual (mm/s)",
    min_value=0.0,
    value=10.0
)

vib_limite = st.sidebar.number_input(
    "Límite Vibración",
    min_value=1.0,
    value=30.0
)

st.sidebar.markdown("### Temperatura")

temp_actual = st.sidebar.number_input(
    "Temperatura Actual (°C)",
    min_value=0.0,
    value=60.0
)

temp_limite = st.sidebar.number_input(
    "Límite Temperatura",
    min_value=1.0,
    value=90.0
)

st.sidebar.markdown("### Ultrasonido")

ultra_actual = st.sidebar.number_input(
    "Ultrasonido Actual",
    min_value=0.0,
    value=15.0
)

ultra_limite = st.sidebar.number_input(
    "Límite Ultrasonido",
    min_value=1.0,
    value=30.0
)

if st.sidebar.button
