import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuración de la página
st.set_page_config(
    page_title="Salud de Activos - Mantenimiento Predictivo",
    page_icon="⚙️",
    layout="wide"
)

# 2. Simulación de tus datos (Reemplaza esto con la carga de tu archivo)
@st.cache_data
def cargar_datos_activos():
    # Aquí simulamos tu archivo con los equipos y ponderaciones
    np.random.seed(42)
    equipos = [f"Motor Principal {i}" for i in range(1, 11)] + [f"Bomba Centrífuga {i}" for i in range(1, 11)]
    
    # Valores de 0 a 100% (100% es salud perfecta, menos de 60% es crítico)
    datos = pd.DataFrame({
        "Activo": equipos,
        "Vibración": np.random.randint(40, 100, 20),
        "Ultrasonido": np.random.randint(50, 100, 20),
        "Termografía": np.random.randint(30, 100, 20),
        "Balanceo": np.random.randint(60, 100, 20),
        "Alineación": np.random.randint(60, 100, 20),
    })
    
    # Calculamos la Salud Global (Promedio ponderado simulado)
    datos["Salud_Global"] = datos[["Vibración", "Ultrasonido", "Termografía", "Balanceo", "Alineación"]].mean(axis=1).round(1)
    
    # Asignar Estado según la Salud Global
    def asignar_estado(score):
        if score >= 85: return "Bueno ✅"
        elif score >= 70: return "Alerta ⚠️"
        else: return "Crítico 🚨"
        
    datos["Estado"] = datos["Salud_Global"].apply(asignar_estado)
    return datos

# --- CARGA DE ARCHIVO REAL ---
# Si quieres usar tu propio archivo Excel/CSV, descomenta las líneas de abajo:
# st.sidebar.header("Cargar Datos")
# archivo = st.sidebar.file_uploader("Sube tu archivo de activos", type=["xlsx", "csv"])
# if archivo:
#     if archivo.name.endswith('.csv'): df = pd.read_csv(archivo)
#     else: df = pd.read_excel(archivo)
# else: df = cargar_datos_activos()

df = cargar_datos_activos() # Borra esta línea si usas el cargador de arriba

# 3. Título Principal
st.title("⚙️ Dashboard de Salud de Activos Industriales")
st.markdown("Monitoreo predictivo basado en Vibración, Ultrasonido, Termografía, Balanceo y Alineación.")
st.markdown("---")

# 4. Filtros en la barra lateral
st.sidebar.header("Filtros de Inspección")
estado_seleccionado = st.sidebar.multiselect(
    "Filtrar por Condición:",
    options=df["Estado"].unique(),
    default=df["Estado"].unique()
)
df_filtrado = df[df["Estado"].isin(estado_seleccionado)]

# 5. KPIs de Flota
Criticos = sum(df_filtrado["Estado"] == "Crítico 🚨")
Alertas = sum(df_filtrado["Estado"] == "Alerta ⚠️")
Buenos = sum(df_filtrado["Estado"] == "Bueno ✅")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Activos Monitoreados", len(df_filtrado))
kpi2.metric("Equipos Críticos 🚨", Criticos, delta=f"{Criticos} urgente", delta_color="inverse")
kpi3.metric("Equipos en Alerta ⚠️", Alertas, delta_color="off")
kpi4.metric("Equipos Saludables ✅", Buenos)

st.markdown("---")

# 6. Gráficos de Estado General
col_izq, col_der = st.columns([1, 2])

with col_izq:
    st.subheader("Distribución de Condiciones")
    fig_pie = px.pie(
        df_filtrado, 
        names="Estado", 
        color="Estado",
        color_discrete_map={"Bueno ✅": "green", "Alerta ⚠️": "orange", "Crítico 🚨": "red"}
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_der:
    st.subheader("Peores Activos por Salud Global")
    df_peores = df_filtrado.sort_values(by="Salud_Global").head(8)
    fig_bar = px.bar(
        df_peores, 
        x="Salud_Global", 
        y="Activo", 
        orientation="h",
        color="Estado",
        color_discrete_map={"Bueno ✅": "green", "Alerta ⚠️": "orange", "Crítico 🚨": "red"},
        text="Salud_Global"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# 7. Análisis Individual por Activo (Gráfico de Radar / Araña)
st.subheader("🔍 Diagnóstico Detallado por Activo")
activo_sel = st.selectbox("Selecciona un equipo para ver su diagnóstico:", df["Activo"].unique())

info_activo = df[df["Activo"] == activo_sel].iloc[0]

# Configurar gráfico de radar para las 5 tecnologías
categorias = ["Vibración", "Ultrasonido", "Termografía", "Balanceo", "Alineación"]
valores = [info_activo[cat] for cat in categorias]

fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(
      r=valores + [valores[0]], # Se duplica el primero para cerrar el círculo
      theta=categorias + [categorias[0]],
      fill='toself',
      name=activo_sel,
      line_color="red" if "Crítico" in info_activo["Estado"] else "orange" if "Alerta" in info_activo["Estado"] else "green"
))

fig_radar.update_layout(
  polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
  showlegend=False
)

col_rad1, col_rad2 = st.columns([1, 1])
with col_rad1:
    st.write(f"### Estado Actual: {info_activo['Estado']}")
    st.write(f"**Puntuación de Salud Global:** {info_activo['Salud_Global']}%")
    st.dataframe(pd.DataFrame({"Técnica": categorias, "Puntuación": valores}))
with col_rad2:
    st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("---")
st.subheader("📋 Matriz Completa de Activos")
st.dataframe(df_filtrado, use_container_width=True)
