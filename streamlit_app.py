import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Asset Health Dashboard",
    page_icon="🏭",
    layout="wide"
)

# =====================================================
# DATOS
# =====================================================

if "activos" not in st.session_state:

    st.session_state.activos = pd.DataFrame([
        {
            "Equipo":"ID FAN H2",
            "Area":"Horno 2",
            "Vibracion":60,
            "Temperatura":75,
            "Ultrasonido":70,
            "Lubricacion":85,
            "Inspeccion":80
        },
        {
            "Equipo":"Compresor 3",
            "Area":"Aire Comprimido",
            "Vibracion":85,
            "Temperatura":90,
            "Ultrasonido":88,
            "Lubricacion":92,
            "Inspeccion":90
        },
        {
            "Equipo":"Reductor Molino",
            "Area":"Molino Crudo",
            "Vibracion":55,
            "Temperatura":65,
            "Ultrasonido":60,
            "Lubricacion":70,
            "Inspeccion":75
        }
    ])

# =====================================================
# FUNCIONES
# =====================================================

def calcular_health(row):

    health = (
        row["Vibracion"] * 0.30 +
        row["Temperatura"] * 0.20 +
        row["Ultrasonido"] * 0.20 +
        row["Lubricacion"] * 0.15 +
        row["Inspeccion"] * 0.15
    )

    return round(health,1)


def clasificar(valor):

    if valor >= 90:
        return "Excelente"

    elif valor >= 75:
        return "Bueno"

    elif valor >= 60:
        return "Atención"

    elif valor >= 40:
        return "Crítico"

    else:
        return "Riesgo Alto"


df = st.session_state.activos.copy()

df["Health"] = df.apply(calcular_health, axis=1)
df["Estado"] = df["Health"].apply(clasificar)

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("🏭 Asset Health")

st.sidebar.header("Nuevo Activo")

equipo = st.sidebar.text_input("Equipo")

area = st.sidebar.selectbox(
    "Área",
    [
        "Horno 1",
        "Horno 2",
        "Molino Crudo",
        "Molino Cemento",
        "Empaque",
        "Aire Comprimido"
    ]
)

vib = st.sidebar.slider("Vibración",0,100,80)
temp = st.sidebar.slider("Temperatura",0,100,80)
ultra = st.sidebar.slider("Ultrasonido",0,100,80)
lub = st.sidebar.slider("Lubricación",0,100,80)
insp = st.sidebar.slider("Inspección",0,100,80)

if st.sidebar.button("Agregar"):

    nuevo = pd.DataFrame([{
        "Equipo":equipo,
        "Area":area,
        "Vibracion":vib,
        "Temperatura":temp,
        "Ultrasonido":ultra,
        "Lubricacion":lub,
        "Inspeccion":insp
    }])

    st.session_state.activos = pd.concat(
        [st.session_state.activos,nuevo],
        ignore_index=True
    )

    st.rerun()

# =====================================================
# TITULO
# =====================================================

st.title("🏭 Asset Health Dashboard")

salud_general = round(df["Health"].mean(),1)

# =====================================================
# KPIs
# =====================================================

c1,c2,c3,c4 = st.columns(4)

c1.metric("Salud General",f"{salud_general}%")
c2.metric("Activos",len(df))
c3.metric("Críticos",len(df[df["Health"]<60]))
c4.metric("Mejor Equipo",df.loc[df["Health"].idxmax(),"Equipo"])

# =====================================================
# GAUGE
# =====================================================

gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=salud_general,
    title={"text":"Salud General Planta"},
    gauge={
        "axis":{"range":[0,100]},
        "bar":{"color":"darkblue"},
        "steps":[
            {"range":[0,40],"color":"red"},
            {"range":[40,60],"color":"orange"},
            {"range":[60,75],"color":"yellow"},
            {"range":[75,100],"color":"green"},
        ]
    }
))

# =====================================================
# DONA
# =====================================================

pie = px.pie(
    df,
    names="Estado",
    title="Estado de Activos"
)

# =====================================================
# FILA 1
# =====================================================

c1,c2 = st.columns(2)

with c1:
    st.plotly_chart(
        gauge,
        use_container_width=True
    )

with c2:
    st.plotly_chart(
        pie,
        use_container_width=True
    )

# =====================================================
# SALUD POR AREA
# =====================================================

area_df = (
    df.groupby("Area")["Health"]
    .mean()
    .reset_index()
)

fig_area = px.bar(
    area_df,
    x="Health",
    y="Area",
    orientation="h",
    color="Health",
    title="Salud por Área"
)

st.plotly_chart(
    fig_area,
    use_container_width=True
)

# =====================================================
# TOP EQUIPOS CRITICOS
# =====================================================

st.subheader("Top Equipos Críticos")

criticos = df.sort_values(
    "Health"
).head(10)

fig_crit = px.bar(
    criticos,
    x="Equipo",
    y="Health",
    color="Health",
    text="Health"
)

st.plotly_chart(
    fig_crit,
    use_container_width=True
)

# =====================================================
# HEATMAP
# =====================================================

st.subheader("Heatmap de Condición")

heat = df.set_index("Equipo")[
    [
        "Vibracion",
        "Temperatura",
        "Ultrasonido",
        "Lubricacion",
        "Inspeccion"
    ]
]

heatmap = go.Figure(
    data=go.Heatmap(
        z=heat.values,
        x=heat.columns,
        y=heat.index,
        colorscale="RdYlGn"
    )
)

st.plotly_chart(
    heatmap,
    use_container_width=True
)

# =====================================================
# RADAR
# =====================================================

st.subheader("Radar de Equipo")

equipo_sel = st.selectbox(
    "Seleccione Equipo",
    df["Equipo"]
)

sel = df[df["Equipo"]==equipo_sel].iloc[0]

radar = go.Figure()

radar.add_trace(go.Scatterpolar(
    r=[
        sel["Vibracion"],
        sel["Temperatura"],
        sel["Ultrasonido"],
        sel["Lubricacion"],
        sel["Inspeccion"]
    ],
    theta=[
        "Vibración",
        "Temperatura",
        "Ultrasonido",
        "Lubricación",
        "Inspección"
    ],
    fill="toself",
    name=equipo_sel
))

radar.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0,100]
        )
    )
)

st.plotly_chart(
    radar,
    use_container_width=True
)

# =====================================================
# DETALLE
# =====================================================

st.subheader("Detalle de Activos")

st.dataframe(
    df.sort_values(
        "Health",
        ascending=False
    ),
    use_container_width=True
)
