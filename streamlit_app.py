import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(
    page_title="Asset Health Dashboard",
    page_icon="🏭",
    layout="wide"
)

# ===============================
# BASE DE DATOS EN MEMORIA
# ===============================

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

# ===============================
# FUNCIONES
# ===============================

def calcular_salud(row):

    vib = min(
        (row["Vibracion"] / row["Limite_Vibracion"]) * 100,
        150
    )

    temp = min(
        (row["Temperatura"] / row["Limite_Temperatura"]) * 100,
        150
    )

    ultra = min(
        (row["Ultrasonido"] / row["Limite_Ultrasonido"]) * 100,
        150
    )

    riesgo = (vib + temp + ultra) / 3

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
        return "🔴 Crí
