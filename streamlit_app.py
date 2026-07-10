import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------
# CONFIGURACION DE PAGINA
# ----------------------------------------
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
    st.info("⬆️ Seleccione un archivo Excel para iniciar.")
    st.stop()

# ----------------------------------------
# LEER EXCEL
# ----------------------------------------
try:
    df = pd.read_excel(
        archivo,
        engine="openpyxl"
    )
except Exception as e:
    st.error(f"Error al leer el archivo Excel: {e}")
    st.stop()

# ----------------------------------------
# LIMPIAR COLUMNAS
# ----------------------------------------
df.columns = df.columns.str.strip()

# ----------------------------------------
# VALIDAR COLUMNAS NECESARIAS
# ----------------------------------------
columnas_necesarias = [
    "FECHA",
    "AREA",
    "EQUIPO",
    "ESTADO E",
    "PUNTO DE MEDICIÓN"
]

columnas_faltantes = [
    col for col in columnas_necesarias if col not in df.columns
]

if columnas_faltantes:
    st.error("Faltan las siguientes columnas en el archivo Excel:")
    st.write(columnas_faltantes)
    st.stop()

# ----------------------------------------
# CONVERTIR FECHA
# ----------------------------------------
df["FECHA"] = pd.to_datetime(
    df["FECHA"],
    dayfirst=True,
    errors="coerce"
)

# ----------------------------------------
# CONVERTIR ESTADO E A NUMERICO
# ----------------------------------------
df["ESTADO E"] = pd.to_numeric(
    df["ESTADO E"],
    errors="coerce"
)

# Si ESTADO E viene en escala 0 a 100, se convierte a 0 a 1
if df["ESTADO E"].max() > 1:
    df["ESTADO E"] = df["ESTADO E"] / 100

# Eliminar filas sin datos importantes
df = df.dropna(
    subset=[
        "FECHA",
        "AREA",
        "EQUIPO",
        "ESTADO E",
        "PUNTO DE MEDICIÓN"
    ]
)

if df.empty:
    st.warning("El archivo no contiene datos válidos para mostrar.")
    st.stop()

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

if df_equipo.empty:
    st.warning("No existen datos para el equipo seleccionado.")
    st.stop()

# ----------------------------------------
# ULTIMA FECHA
# ----------------------------------------
ultima_fecha = df_equipo["FECHA"].max()

df_actual = df_equipo[
    df_equipo["FECHA"] == ultima_fecha
]

if df_actual.empty:
    st.warning("No existen datos para la última fecha seleccionada.")
    st.stop()

# ----------------------------------------
# SALUD ACTUAL
# ----------------------------------------
salud_actual = df_actual["ESTADO E"].mean()

# ----------------------------------------
# ESTADO GENERAL
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
    df_actual["ESTADO E"].idxmin()
]

# ----------------------------------------
# KPI PRINCIPAL
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

    st.write("### Valor Punto Crítico")
    st.write(
        f'{critico["ESTADO E"]:.0%}'
    )

# ----------------------------------------
# HISTORICO
# ----------------------------------------
st.divider()

st.subheader("📈 Tendencia Histórica")

historico = (
    df_equipo
    .groupby("FECHA", as_index=False)["ESTADO E"]
    .mean()
    .sort_values("FECHA")
)

fig_hist = px.line(
    historico,
    x="FECHA",
    y="ESTADO E",
    markers=True,
    title="Tendencia de Salud del Equipo"
)

fig_hist.update_yaxes(
    tickformat=".0%",
    range=[0, 1]
)

fig_hist.update_layout(
    xaxis_title="Fecha",
    yaxis_title="Salud del equipo"
)

st.plotly_chart(
    fig_hist,
    use_container_width=True
)

# ----------------------------------------
# ELEMENTOS CRITICOS
# ----------------------------------------
st.subheader("🔧 Elementos Críticos")

df_criticos = (
    df_actual[
        [
            "PUNTO DE MEDICIÓN",
            "ESTADO E"
        ]
    ]
    .sort_values(
        "ESTADO E",
        ascending=True
    )
)

fig_crit = px.bar(
    df_criticos,
    x="ESTADO E",
    y="PUNTO DE MEDICIÓN",
    orientation="h",
    text="ESTADO E",
    color="ESTADO E",
    color_continuous_scale="RdYlGn",
    title="Estado por Punto de Medición"
)

fig_crit.update_traces(
    texttemplate="%{x:.0%}",
    textposition="outside"
)

fig_crit.update_yaxes(
    categoryorder="total ascending"
)

fig_crit.update_xaxes(
    tickformat=".0%",
    range=[0, 1]
)

fig_crit.update_layout(
    xaxis_title="Estado",
    yaxis_title="Punto de medición"
)

st.plotly_chart(
    fig_crit,
    use_container_width=True
)

# ----------------------------------------
# TABLA
# ----------------------------------------
st.subheader("📋 Datos Última Inspección")

st.dataframe(
    df_actual,
    use_container_width=True
)
