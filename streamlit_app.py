import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Dashboard Predictivo",
    page_icon="⚙️",
    layout="wide"
)

st.title("📈 Dashboard Salud de Equipos")

archivo = st.file_uploader(
    "Subir archivo Excel",
    type=["xlsx"]
)

if archivo:

    df = pd.read_excel(archivo)

    equipos = sorted(df["EQUIPO"].unique())

    equipo = st.sidebar.selectbox(
        "Seleccionar equipo",
        equipos
    )

    df_equipo = df[df["EQUIPO"] == equipo]

    salud = df_equipo["ESTADO E"].mean()

    if salud >= 0.9:
        estado = "🟢 NORMAL"
        color = "green"

    elif salud >= 0.7:
        estado = "🟡 ALARMA"
        color = "orange"

    else:
        estado = "🔴 INTERVENIR"
        color = "red"

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "SALUD DEL EQUIPO",
            f"{salud:.0%}"
        )

    with c2:
        st.metric(
            "ESTADO",
            estado
        )

    punto_critico = df_equipo.loc[
        df_equipo["ESTADO E"].idxmin(),
        "PUNTO DE MEDICIÓN"
    ]

    with c3:
        st.metric(
            "PUNTO CRÍTICO",
            punto_critico
        )

    # ------------------
    # VELOCÍMETRO
    # ------------------

    fig_gauge = go.Figure(
        go.Indicator(
            mode = "gauge+number",
            value = salud * 100,

            number = {
                'suffix': "%"
            },

            gauge = {
                'axis': {
                    'range': [0,100]
                },

                'bar': {
                    'color': color
                },

                'steps': [
                    {
                        'range': [0,70],
                        'color': 'red'
                    },
                    {
                        'range': [70,90],
                        'color': 'yellow'
                    },
                    {
                        'range': [90,100],
                        'color': 'green'
                    }
                ]
            }
        )
    )

    st.plotly_chart(
        fig_gauge,
        use_container_width=True
    )

    st.subheader("Componentes del Equipo")

    fig_bar = px.bar(
        df_equipo,
        x="ESTADO E",
        y="PUNTO DE MEDICIÓN",
        orientation="h",
        text="ESTADO E",
        color="ESTADO E",
        color_continuous_scale="RdYlGn"
    )

    fig_bar.update_traces(
        texttemplate='%{x:.0%}'
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

    st.subheader("Salud por Tecnología")

    datos = pd.DataFrame({

        "Tecnología":[
            "Ultrasonido",
            "Vibración",
            "Termografía"
        ],

        "Salud":[

            df_equipo["ESTADO U"].mean()*100,

            df_equipo["ESTADO V"].mean()*100,

            df_equipo["ESTADO T"].mean()*100,
        ]
    })

    fig_radar = px.line_polar(
        datos,
        r="Salud",
        theta="Tecnología",
        line_close=True
    )

    fig_radar.update_traces(
        fill="toself"
    )

    st.plotly_chart(
        fig_radar,
        use_container_width=True
    )

    st.subheader("Detalle")

    st.dataframe(df_equipo)
