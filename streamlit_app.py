import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Asset Health Dashboard",
    page_icon="🏭",
    layout="wide"
)

# ==========================================
# FUNCIONES
# ==========================================

def calcular_porcentaje(actual, limite):
    return round((actual / limite) * 100, 1)

def calcular_salud(row):

    vib = calcular_porcentaje(
        row["Vib_Actual"],
        row["Vib_Limite"]
    )

    temp = calcular_porcentaje(
        row["Temp_Actual"],
        row["Temp_Limite"]
    )

    ultra = calcular_porcentaje(
        row["Ultra_Actual"],
        row["Ultra_Limite"]
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
        return "🔴 Crítico"

# ==========================================
# SESSION STATE
# ==========================================

if "equipos" not in st.session_state:

    st.session_state.equipos = pd.DataFrame(
        columns=[
            "Equipo",
            "Vib_Actual",
            "Vib_Limite",
            "Temp_Actual",
            "Temp_Limite",
            "Ultra_Actual",
            "Ultra_Limite"
        ]
    )

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("Ingreso de Datos")

equipo = st.sidebar.text_input(
    "Nombre del Equipo"
)

st.sidebar.subheader("Vibración")

vib_actual = st.sidebar.number_input(
    "Vibración Actual (mm/s)",
    min_value=0.0,
    value=10.0
)

vib_limite = st.sidebar.number_input(
    "Límite Crítico Vibración",
    min_value=1.0,
    value=30.0
)

st.sidebar.subheader("Temperatura")

temp_actual = st.sidebar.number_input(
    "Temperatura Actual (°C)",
    min_value=0.0,
    value=60.0
)

temp_limite = st.sidebar.number_input(
    "Límite Crítico Temperatura",
    min_value=1.0,
    value=90.0
)

st.sidebar.subheader("Ultrasonido")

ultra_actual = st.sidebar.number_input(
    "Ultrasonido Actual",
    min_value=0.0,
    value=20.0
)

ultra_limite = st.sidebar.number_input(
    "Límite Crítico Ultrasonido",
    min_value=1.0,
    value=40.0
)

if st.sidebar.button("Agregar Equipo"):

    if equipo != "":

        nuevo = pd.DataFrame([{
            "Equipo": equipo,
            "Vib_Actual": vib_actual,
            "Vib_Limite": vib_limite,
            "Temp_Actual": temp_actual,
            "Temp_Limite": temp_limite,
            "Ultra_Actual": ultra_actual,
            "Ultra_Limite": ultra_limite
        }])

        st.session_state.equipos = pd.concat(
            [st.session_state.equipos, nuevo],
            ignore_index=True
        )

        st.success("Equipo agregado")

# ==========================================
# TITULO
# ==========================================

st.title("🏭 Asset Health Dashboard")

df = st.session_state.equipos.copy()

# ==========================================
# CALCULOS
# ==========================================

if len(df) > 0:

    df["Salud"] = df.apply(
        calcular_salud,
        axis=1
    )

    df["Estado"] = df["Salud"].apply(
        clasificar
    )

    salud_general = round(
        df["Salud"].mean(),
        1
    )

    # ======================================
    # KPI
    # ======================================

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Salud General",
        f"{salud_general}%"
    )

    c2.metric(
        "Equipos",
        len(df)
    )

    c3.metric(
        "Críticos",
        len(df[df["Salud"] < 30])
    )

    # ======================================
    # GAUGE
    # ======================================

    gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=salud_general,
            title={"text":"Salud General"},
            gauge={
                "axis":{"range":[0,100]},
                "steps":[
                    {"range":[0,30],"color":"red"},
                    {"range":[30,50],"color":"orange"},
                    {"range":[50,70],"color":"yellow"},
                    {"range":[70,100],"color":"green"}
                ]
            }
        )
    )

    st.plotly_chart(
        gauge,
        use_container_width=True
    )

    # ======================================
    # DISTRIBUCION
    # ======================================

    fig_estado = px.pie(
        df,
        names="Estado",
        title="Estado de Equipos"
    )

    st.plotly_chart(
        fig_estado,
        use_container_width=True
    )

    # ======================================
    # RANKING
    # ======================================

    st.subheader(
        "Ranking de Riesgo"
    )

    ranking = df.sort_values(
        by="Salud"
    )

    fig_riesgo = px.bar(
        ranking,
        x="Equipo",
        y="Salud",
        color="Salud",
        text="Salud",
        color_continuous_scale="RdYlGn"
    )

    st.plotly_chart(
        fig_riesgo,
        use_container_width=True
    )

    # ======================================
    # SELECCION DE EQUIPO
    # ======================================

    st.subheader(
        "Detalle del Equipo"
    )

    seleccionado = st.selectbox(
        "Equipo",
        df["Equipo"]
    )

    fila = df[
        df["Equipo"] == seleccionado
    ].iloc[0]

    vib_pct = (
        fila["Vib_Actual"] /
        fila["Vib_Limite"]
    ) * 100

    temp_pct = (
        fila["Temp_Actual"] /
        fila["Temp_Limite"]
    ) * 100

    ultra_pct = (
        fila["Ultra_Actual"] /
        fila["Ultra_Limite"]
    ) * 100

    radar = go.Figure()

    radar.add_trace(
        go.Scatterpolar(
            r=[
                vib_pct,
                temp_pct,
                ultra_pct
            ],
            theta=[
                "Vibración",
                "Temperatura",
                "Ultrasonido"
            ],
            fill="toself"
        )
    )

    radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0,150]
            )
        )
    )

    st.plotly_chart(
        radar,
        use_container_width=True
    )

    st.subheader(
        "Detalle General"
    )

    st.dataframe(
        df,
        use_container_width=True
    )

else:

    st.info(
        "Ingrese el primer equipo desde el menú lateral."
    )
