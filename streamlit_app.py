import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Dashboard Salud Equipos",
    layout="wide"
)

st.title("⚙️ Dashboard Salud de Equipos")

# ----------------------------------------
# CARGAR EXCEL
# ----------------------------------------

archivo = st.file_uploader(
    "Seleccione archivo Excel",
    type=["xlsx"]
)

if archivo is None:

    st.info(
        "⬆️ Seleccione un archivo Excel para iniciar."
    )

    st.stop()

# ----------------------------------------
# LEER EXCEL
# ----------------------------------------

df = pd.read_excel(
    archivo,
    engine="openpyxl"
)

# ----------------------------------------
# LIMPIAR COLUMNAS
# ----------------------------------------

df.columns = df.columns.str.strip()

# ----------------------------------------
# FECHA
# ----------------------------------------

df["FECHA"] = pd.to_datetime(
    df["FECHA"],
    dayfirst=True,
    errors="coerce"
)

# ----------------------------------------
# FILTRO AREA
# ----------------------------------------

areas = sorted(
    df["AREA"].dropna().unique()
)

area = st.sidebar.selectbox(
    "Área",
    areas
)

df_area = df[
    df["AREA"] == area
]

# ----------------------------------------
# FILTRO EQUIPO
# ----------------------------------------

equipos = sorted(
    df_area["EQUIPO"].dropna().unique()
)

equipo = st.sidebar.selectbox(
    "Equipo",
    equipos
)

df_equipo = df_area[
    df_area["EQUIPO"] == equipo
]

# ----------------------------------------
# ULTIMA FECHA
# ----------------------------------------

ultima_fecha = df_equipo["FECHA"].max()

df_actual = df_equipo[
    df_equipo["FECHA"] == ultima_fecha
]

# ----------------------------------------
# SALUD ACTUAL
# ----------------------------------------

salud_actual = (
    df_actual["ESTADO E"]
    .astype(float)
    .mean()
)

# ----------------------------------------
# ESTADO
# ----------------------------------------

if salud_actual >= 0.90:

    estado = "🟢 NORMAL"
    color = "#28a745"

elif salud_actual >= 0.70:

    estado = "🟡 ALARMA"
    color = "#ffc107"

else:

    estado = "🔴 INTERVENIR"
    color = "#dc3545"

# ----------------------------------------
# PUNTO CRITICO
# ----------------------------------------

critico = df_actual.loc[
    df_actual["ESTADO E"].astype(float).idxmin()
]

# ----------------------------------------
# KPI
# ----------------------------------------

col1, col2 = st.columns(2)

with col1:

    fig = go.Figure()

    fig.add_trace(
        go.Pie(
            values=[
                salud_actual * 100,
                100 - salud_actual * 100
            ],
            hole=0.75,
            marker=dict(
                colors=[
                    color,
                    "#e5e5e5"
                ]
            ),
            textinfo="none"
        )
    )

    fig.update_layout(
        showlegend=False,
        height=400,
        annotations=[
            dict(
                text=f"{salud_actual:.0%}",
                x=0.5,
                y=0.5,
                showarrow=False,
                font_size=40
            )
        ]
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    st.metric(
        "Salud Actual",
        f"{salud_actual:.0%}"
    )

    st.write("### Estado")
    st.write(estado)

    st.write("### Última Fecha")
    st.write(
        ultima_fecha.strftime("%d/%m/%Y")
    )

    st.write("### Punto Más Crítico")
    st.write(
        critico["PUNTO DE MEDICIÓN"]
    )

# ----------------------------------------
# HISTORICO
# ----------------------------------------

st.divider()

st.subheader(
    "📈 Tendencia Histórica"
)

historico = (
    df_equipo
    .groupby("FECHA")["ESTADO E"]
    .mean()
    .reset_index()
)

fig_hist = px.line(
    historico,
    x="FECHA",
    y="ESTADO E",
    markers=True
)

fig_hist.update_yaxes(
    tickformat=".0%"
)

#st.plotly_chart(
   # fig_hist,
   # use_container_width=True
#)

# ----------------------------------------
# ELEMENTOS CRITICOS
# ----------------------------------------

st.subheader(
    "🔧 Elementos Críticos"
)

df_criticos = (
    df_actual[
        [
            "PUNTO DE MEDICIÓN",
            "ESTADO E"
        ]
    ]
    .sort_values(
        "ESTADO E"
    )
)

fig_crit = px.bar(
    df_criticos,
    x="ESTADO E",
    y="PUNTO DE MEDICIÓN",
    orientation="h",
    text="ESTADO E",
    color="ESTADO E",
    color_continuous_scale="RdYlGn"
)

fig_crit.update_traces(
    texttemplate="%{x:.0%}"
)

fig_crit.update_yaxes(
    categoryorder="total ascending"
)

#st.plotly_chart(
   # fig_crit,
 #  use_container_width=True
#)

# ----------------------------------------
# TABLA
# ----------------------------------------

st.subheader(
    "📋 Datos Última Inspección"
)

st.dataframe(
    df_actual,
    use_container_width=True
)
