import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(
    page_title="Asset Health Dashboard",
    layout="wide"
)

# --------------------------------------------------
# Memoria
# --------------------------------------------------

if "historico" not in st.session_state:
    st.session_state.historico = pd.DataFrame(
        columns=[
            "Fecha",
            "Equipo",
            "Vibracion",
            "Limite_Vibracion",
            "Temperatura",
            "Limite_Temperatura",
            "Ultrasonido",
            "Limite_Ultrasonido"
        ]
    )

# --------------------------------------------------
# Funciones
# --------------------------------------------------

def calcular_salud(fila):

    vib = (fila["Vibracion"] / fila["Limite_Vibracion"]) * 100
    temp = (fila["Temperatura"] / fila["Limite_Temperatura"]) * 100
    ultra = (fila["Ultrasonido"] / fila["Limite_Ultrasonido"]) * 100

    riesgo = (vib + temp + ultra) / 3

    salud = max(0, 100 - riesgo)

    return round(salud, 1)


def obtener_estado(salud):

    if salud >= 90:
        return "
