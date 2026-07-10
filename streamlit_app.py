import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Tablero Salud de Equipos",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Tablero Salud de Equipos")

archivo = st.file_uploader(
    "Subir archivo Excel",
    type=["xlsx"]
)

if archivo is not None:

    try:

        df = pd.read_excel(
            archivo,
            engine="openpyxl"
        )

        df.columns = df.columns.str.strip()

        st.sidebar.header("Filtros")

        equipos = sorted(
            df["EQUIPO"].dropna().unique()
        )

        equipo = st.sidebar.selectbox(
            "Seleccionar equipo",
            equipos
        )

        df_equipo = df[
            df["EQUIPO"] == equipo
        ]

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

        punto_critico = df_equipo.loc[
            df_equipo["ESTADO E"].idxmin(),
            "PUNTO DE MEDICIÓN"
        ]

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "SALUD DEL EQUIPO",
            f"{salud:.0%}"
        )

        c2.metric(
            "ESTADO",
            estado
        )

        c3.metric(
            "PUNTO MÁS CRÍTICO",
            punto_critico
        )

        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=salud * 100,
                number={'suffix': "%"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, 70], 'color': '#ff4d4d'},
                        {'range': [70, 90], 'color': '#ffd633'},
                        {'range': [90, 100], 'color': '#33cc33'}
                    ]
                }
            )
        )

        st.plotly_chart(
            fig_gauge,
            key="gauge"
        )

        st.subheader("Puntos de Medición")

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
            key="barras"
        )

        st.subheader("Salud por Tecnología")

        radar = pd.DataFrame({

            "Tecnología": [
                "Ultrasonido",
                "Vibración",
                "Termografía"
            ],

            "Salud": [
                df_equipo["ESTADO U"].mean() * 100,
                df_equipo["ESTADO V"].mean() * 100,
                df_equipo["ESTADO T"].mean() * 100
            ]
        })

        fig_radar = px.line_polar(
            radar,
            r="Salud",
            theta="Tecnología",
            line_close=True
        )

        fig_radar.update_traces(
            fill="toself"
        )

        st.plotly_chart(
            fig_radar,
            key="radar"
        )

        st.subheader("Detalle de Mediciones")

        st.dataframe(
            df_equipo,
            use_container_width=True
        )

    except Exception as e:

        st.error(f"Error: {e}")
