import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="OEE Molino Vertical - UNACEM", layout="wide")

# Inicializar historial en la sesión si no existe
if 'historial_oee' not in st.session_state:
    # Creamos unos datos de ejemplo para que la gráfica no nazca vacía (opcional)
    st.session_state.historial_oee = []

st.title("🏭 Gestión de Activos: Monitor OEE")
st.subheader("Optimización de Molinos Verticales de Rodillos")

# --- BARRA LATERAL: ENTRADA DE DATOS ---
st.sidebar.header("📥 Datos del Turno")
fecha = st.sidebar.date_input("Fecha de Reporte", datetime.date.today())
molino = st.sidebar.selectbox("Equipo", ["Molino de Crudo 1", "Molino de Cemento 1", "Molino de Cemento 2"])

st.sidebar.divider()
st.sidebar.write("**1. Disponibilidad**")
t_programado = st.sidebar.number_input("Tiempo Programado (Horas)", min_value=0.1, value=24.0)
t_paradas = st.sidebar.number_input("Paradas No Programadas (Horas)", min_value=0.0, value=2.0)

st.sidebar.write("**2. Rendimiento**")
capacidad_diseno = st.sidebar.number_input("Capacidad Diseño (TM/h)", min_value=1.0, value=150.0)
tm_totales = st.sidebar.number_input("Toneladas Producidas (TM)", min_value=0.0, value=3100.0)

st.sidebar.write("**3. Calidad**")
tm_rechazo = st.sidebar.number_input("TM Fuera de Especificación", min_value=0.0, value=30.0)

# --- CÁLCULOS LÓGICOS ---
t_operativo = t_programado - t_paradas
disponibilidad = (t_operativo / t_programado) if t_programado > 0 else 0
tm_teoricas = t_operativo * capacidad_diseno
rendimiento = (tm_totales / tm_teoricas) if tm_teoricas > 0 else 0
calidad = ((tm_totales - tm_rechazo) / tm_totales) if tm_totales > 0 else 0
oee = disponibilidad * rendimiento * calidad

# --- PANTALLA PRINCIPAL: INDICADORES ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("OEE TOTAL", f"{oee:.1%}")
m2.metric("Disponibilidad", f"{disponibilidad:.1%}")
m3.metric("Rendimiento", f"{rendimiento:.1%}")
m4.metric("Calidad", f"{calidad:.1%}")

# --- SECCIÓN DE GRÁFICAS ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.write("### Desglose de Pilares (%)")
    df_stats = pd.DataFrame({
        'Indicador': ['Disponibilidad', 'Rendimiento', 'Calidad'],
        'Valor': [disponibilidad * 100, rendimiento * 100, calidad * 100]
    })
    fig_bar = px.bar(df_stats, x='Indicador', y='Valor', color='Indicador', range_y=[0,110])
    st.plotly_chart(fig_bar, use_container_width=True)

with col_graf2:
    st.write("### 📈 Tendencia Histórica del OEE")
    if len(st.session_state.historial_oee) > 0:
        df_hist = pd.DataFrame(st.session_state.historial_oee)
        # Convertir OEE de texto "85.0%" a flotante 0.85 para graficar
        df_hist['OEE_Float'] = df_hist['OEE'].str.rstrip('%').astype('float')
        
        fig_line = px.line(df_hist, x='Fecha', y='OEE_Float', markers=True, title="Evolución OEE")
        fig_line.update_yaxes(range=[0, 110])
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Guarda el primer registro para ver la tendencia.")

# --- BOTÓN PARA GUARDAR ---
if st.button("💾 Guardar Datos del Turno"):
    nuevo_registro = {
        "Fecha": str(fecha),
        "Molino": molino,
        "OEE": f"{oee*100:.1f}%",
        "Disp": f"{disponibilidad*100:.1f}%",
        "Rend": f"{rendimiento*100:.1f}%",
        "Cal": f"{calidad*100:.1f}%",
        "TM": tm_totales
    }
    st.session_state.historial_oee.append(nuevo_registro)
    st.rerun() # Refrescar para mostrar la gráfica inmediatamente

# --- TABLA DE DATOS ---
st.divider()
if st.session_state.historial_oee:
    st.subheader("📋 Registro de Mediciones")
    st.dataframe(pd.DataFrame(st.session_state.historial_oee), use_container_width=True)
    
    if st.button("🗑️ Limpiar Historial"):
        st.session_state.historial_oee = []
        st.rerun()
