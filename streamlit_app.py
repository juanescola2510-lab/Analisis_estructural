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

    if salud >= 70:
        return "NORMAL"

    elif salud >= 50:
        return "ATENCION"

    elif salud >= 30:
        return "ALARMA"

    else:
        return "CRITICO"


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.title("Ingreso de Inspeccion")

fecha = st.sidebar.date_input(
    "Fecha",
    value=date.today()
)

equipo = st.sidebar.text_input(
    "Nombre del Equipo"
)

st.sidebar.subheader("Vibracion")

vibracion = st.sidebar.number_input(
    "Valor Vibracion",
    min_value=0.0,
    value=10.0
)

lim_vibracion = st.sidebar.number_input(
    "Limite Vibracion",
    min_value=1.0,
    value=30.0
)

st.sidebar.subheader("Temperatura")

temperatura = st.sidebar.number_input(
    "Valor Temperatura",
    min_value=0.0,
    value=60.0
)

lim_temperatura = st.sidebar.number_input(
    "Limite Temperatura",
    min_value=1.0,
    value=90.0
)

st.sidebar.subheader("Ultrasonido")

ultrasonido = st.sidebar.number_input(
    "Valor Ultrasonido",
    min_value=0.0,
    value=20.0
)

lim_ultrasonido = st.sidebar.number_input(
    "Limite Ultrasonido",
    min_value=1.0,
    value=40.0
)

if st.sidebar.button("Guardar Inspeccion"):

    if equipo.strip():

        nuevo = pd.DataFrame(
            [{
                "Fecha": fecha,
                "Equipo": equipo.upper(),
                "Vibracion": vibracion,
                "Limite_Vibracion": lim_vibracion,
                "Temperatura": temperatura,
                "Limite_Temperatura": lim_temperatura,
                "Ultrasonido": ultrasonido,
                "Limite_Ultrasonido": lim_ultrasonido
            }]
        )

        st.session_state.historico = pd.concat(
            [st.session_state.historico, nuevo],
            ignore_index=True
        )

# --------------------------------------------------
# Dashboard
# --------------------------------------------------

st.title("ASSET HEALTH DASHBOARD")

historico = st.session_state.historico.copy()

if len(historico) == 0:

    st.info("Ingrese la primera inspeccion")

else:

    historico["Fecha"] = pd.to_datetime(
        historico["Fecha"]
    )

    ultimos = (
        historico
        .sort_values("Fecha")
        .groupby("Equipo")
        .tail(1)
        .copy()
    )

    ultimos["Salud"] = ultimos.apply(
        calcular_salud,
        axis=1
    )

    ultimos["Estado"] = ultimos["Salud"].apply(
        obtener_estado
    )

    salud_general = round(
        ultimos["Salud"].mean(),
        1
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Salud General",
        f"{salud_general}%"
    )

    c2.metric(
        "Equipos",
        len(ultimos)
    )

    c3.metric(
        "Inspecciones",
        len(historico)
    )

    fig_estado = px.pie(
        ultimos,
        names="Estado",
        title="Estado de Equipos"
    )

    st.plotly_chart(
        fig_estado,
        use_container_width=True
    )

    ranking = ultimos.sort_values(
        "Salud"
    )

    fig_ranking = px.bar(
        ranking,
        x="Equipo",
        y="Salud",
        color="Salud",
        text="Salud"
    )

    st.plotly_chart(
        fig_ranking,
        use_container_width=True
    )

    equipo_sel = st.selectbox(
        "Seleccione Equipo",
        sorted(historico["Equipo"].unique())
    )

    equipo_hist = historico[
        historico["Equipo"] == equipo_sel
    ].sort_values("Fecha")

    st.subheader("Tendencia Vibracion")

    fig_vib = px.line(
        equipo_hist,
        x="Fecha",
        y="Vibracion",
        markers=True
    )

    fig_vib.add_hline(
        y=equipo_hist["Limite_Vibracion"].iloc[-1],
        line_dash="dash"
    )

    st.plotly_chart(
        fig_vib,
        use_container_width=True
    )

    st.subheader("Tendencia Temperatura")

    fig_temp = px.line(
        equipo_hist,
        x="Fecha",
        y="Temperatura",
        markers=True
    )

    fig_temp.add_hline(
        y=equipo_hist["Limite_Temperatura"].iloc[-1],
        line_dash="dash"
    )

    st.plotly_chart(
        fig_temp,
        use_container_width=True
    )

    st.subheader("Tendencia Ultrasonido")

    fig_ultra = px.line(
        equipo_hist,
        x="Fecha",
        y="Ultrasonido",
        markers=True
    )

    fig_ultra.add_hline(
        y=equipo_hist["Limite_Ultrasonido"].iloc[-1],
        line_dash="dash"
    )

    st.plotly_chart(
        fig_ultra,
        use_container_width=True
    )

    st.subheader("Ultima Condicion")

    st.dataframe(
        ultimos,
        use_container_width=True
    )

    st.subheader("Historico Completo")

    st.dataframe(
        historico.sort_values(
            "Fecha",
            ascending=False
        ),
        use_container_width=True
    )
