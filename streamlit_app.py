import streamlit as st
import random
import pandas as pd
import plotly.express as px
from collections import Counter

# Configuración de página
st.set_page_config(page_title="Simulador de Marcadores Pro 2026", page_icon="⚽", layout="wide")

st.title("⚽ Simulador de Alta Velocidad Partido por Partido - Mundial 2026")
st.write("Análisis probabilístico masivo con Gráfico de Pastel interactivo.")

# --- BASE DE DATOS MUNDIAL DE 48 EQUIPOS (Calibración Competitiva) ---
@st.cache_data
def cargar_base_datos_mundial():
    # Estructura: (Goles a Favor promedio, Goles en Contra promedio, Puntos Racha)
    ratings_48 = {
        # UEFA
        "Francia": (2.4, 0.8, 12), "España": (2.3, 0.7, 13), "Inglaterra": (2.2, 0.9, 11), "Alemania": (2.1, 1.0, 10),
        "Portugal": (2.3, 0.9, 12), "Países Bajos": (2.0, 1.0, 10), "Bélgica": (1.8, 1.1, 9), "Italia": (1.7, 1.1, 8),
        "Croacia": (1.6, 1.0, 9), "Dinamarca": (1.6, 1.2, 8), "Suiza": (1.6, 1.1, 9), "Austria": (1.7, 1.2, 8),
        "Noruega": (1.8, 1.3, 8), "Ucrania": (1.5, 1.2, 8), "Polonia": (1.4, 1.4, 7), "Suecia": (1.7, 1.3, 8),
        "Turquía": (1.7, 1.3, 9), "República Checa": (1.5, 1.3, 8), "Escocia": (1.3, 1.5, 7), "Bosnia y Herz.": (1.2, 1.6, 6),
        # CONMEBOL
        "Argentina": (2.5, 0.6, 14), "Brasil": (2.2, 0.9, 11), "Uruguay": (2.1, 1.0, 11), "Colombia": (2.0, 0.9, 12),
        "Ecuador": (1.8, 0.9, 10), "Paraguay": (1.3, 1.1, 8), "Bolivia": (1.1, 2.1, 5),
        # CONCACAF
        "Estados Unidos": (1.9, 1.1, 10), "México": (1.7, 1.2, 8), "Canadá": (1.8, 1.2, 9), "Panamá": (1.5, 1.3, 8),
        "Haití": (1.2, 1.7, 6), "Curazao": (1.1, 1.9, 5), "Jamaica": (1.4, 1.5, 7),
        # CAF (África)
        "Marruecos": (1.9, 0.9, 12), "Senegal": (1.8, 1.0, 11), "Egipto": (1.7, 1.1, 10), "Argelia": (1.7, 1.2, 9),
        "Túnez": (1.4, 1.3, 8), "Nigeria": (1.8, 1.2, 8), "Costa de Marfil": (1.7, 1.1, 10), "Ghana": (1.5, 1.3, 8),
        "Sudáfrica": (1.4, 1.4, 7), "Cabo Verde": (1.4, 1.3, 8), "Congo": (1.1, 1.7, 6),
        # AFC (Asia) + OFC (Oceanía)
        "Japón": (2.1, 1.0, 11), "Corea del Sur": (1.9, 1.1, 10), "Irán": (1.7, 1.2, 9), "Australia": (1.6, 1.3, 9),
        "Arabia Saudita": (1.5, 1.4, 8), "Catar": (1.4, 1.5, 7), "Jordania": (1.2, 1.5, 7), "Uzbekistán": (1.3, 1.3, 8),
        "Nueva Zelanda": (1.2, 1.7, 6)
    }
    return ratings_48

db_mundial = cargar_base_datos_mundial()

# --- LÓGICA DE RATINGS DINÁMICOS ---
def calcular_rating_dinamico(nombre_equipo, fatiga, lesionados):
    gf, gc, racha = db_mundial[nombre_equipo]
    
    # 1. Poder Base según estadísticas actuales
    base_poder = 75.0 + (gf * 5) - (gc * 4) + ((racha - 8) * 0.5)
    
    # 2. Factor Localía ÚNICAMENTE para los tres organizadores oficiales
    bono_localia = 4.5 if nombre_equipo in ["Estados Unidos", "México", "Canadá"] else 0.0
    
    # 3. Penalizadores físicos
    penalizacion_fatiga = fatiga * 6.0
    penalizacion_lesiones = lesionados * 3.0
    
    # 4. Factor Sorpresa e Inspiración del día (Fluctuación aleatoria por partido)
    factor_inspiracion = random.uniform(-4.0, 4.0)
    
    return max(50.0, base_poder + bono_localia - penalizacion_fatiga - penalizacion_lesiones + factor_inspiracion)

# --- INTERFAZ DE CONFIGURACIÓN DE EQUIPOS ---
col_ui1, col_ui2 = st.columns(2)
with col_ui1:
    st.subheader("🏠 Selección 1 / Local")
    eq1_nombre = st.selectbox("Equipo 1", sorted(list(db_mundial.keys())), index=11) # Ecuador por defecto
    fatiga_1 = st.slider("Fatiga Acumulada (Eq 1)", 0.0, 1.0, 0.10, step=0.05)
    lesiones_1 = st.number_input("Lesiones (Eq 1)", min_value=0, max_value=4, value=0)

with col_ui2:
    st.subheader("🚀 Selección 2 / Visitante")
    eq2_nombre = st.selectbox("Equipo 2", sorted(list(db_mundial.keys())), index=19) # Francia por defecto
    fatiga_2 = st.slider("Fatiga Acumulada (Eq 2)", 0.0, 1.0, 0.15, step=0.05)
    lesiones_2 = st.number_input("Lesiones (Eq 2)", min_value=0, max_value=4, value=0)

st.sidebar.header("⚙️ Control de Simulación Masiva")
num_ejecuciones = st.sidebar.number_input("Volumen de simulaciones", min_value=1, max_value=100000, value=50000, step=5000)

# --- EJECUCIÓN DEL MOTOR DE SIMULACIÓN ---
if st.button("🏟️ Iniciar Simulación de Alta Velocidad", type="primary", use_container_width=True):
    if eq1_nombre == eq2_nombre:
        st.warning("⚠️ Selecciona dos países distintos para jugar el encuentro.")
    else:
        status_text = st.empty()
        status_text.info(f"⏳ Procesando {num_ejecuciones:,} partidos simulados en segundo plano... Por favor, espera.")
        
        # Contadores rápidos en Python nativo para evitar saturar memoria RAM
        conteo_marcadores = Counter()
        victorias_eq1 = 0
        victorias_eq2 = 0
        empates = 0
        
        # Ejecución a nivel de microprocesador
        for _ in range(int(num_ejecuciones)):
            r1 = calcular_rating_dinamico(eq1_nombre, fatiga_1, lesiones_1)
            r2 = calcular_rating_dinamico(eq2_nombre, fatiga_2, lesiones_2)
            
            diff = r1 - r2
            lambda1 = max(0.4, 1.35 + (diff * 0.045))
            lambda2 = max(0.4, 1.35 - (diff * 0.045))
            
            goles1 = max(0, int(random.gammavariate(lambda1, 1.15)))
            goles2 = max(0, int(random.gammavariate(lambda2, 1.15)))
            
            conteo_marcadores[f"{goles1} - {goles2}"] += 1
            
            if goles1 > goles2:
                victorias_eq1 += 1
            elif goles2 > goles1:
                victorias_eq2 += 1
            else:
                empates += 1
                
        status_text.empty()
        
        # --- DESPLIEGUE ESTADÍSTICO ---
        st.divider()
        st.subheader(f"📊 Reporte de Probabilidades Acumuladas ({num_ejecuciones:,} partidos)")
        
        # KPIs Principales de Tendencia
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric(f"Probabilidad de {eq1_nombre}", f"{(victorias_eq1 / num_ejecuciones * 100):.2f}%")
        with kpi2:
            st.metric("Probabilidad de Empate 🤝", f"{(empates / num_ejecuciones * 100):.2f}%")
        with kpi3:
            st.metric(f"Probabilidad de {eq2_nombre}", f"{(victorias_eq2 / num_ejecuciones * 100):.2f}%")
            
        # Marcador más probable
        marcador_comun, total_comun = conteo_marcadores.most_common(1)[0]
        st.success(f"🎯 El marcador más probable según el modelo es **{marcador_comun}** con un **{(total_comun / num_ejecuciones * 100):.2f}%** de coincidencia.")
        
        # --- CONSTRUCCIÓN DEL GRÁFICO DE PASTEL INTERACTIVO ---
        st.markdown("### 🥧 Distribución Porcentual de Marcadores Más Frecuentes")
        
        # Extraemos los 8 marcadores más repetidos y agrupamos el resto en "Otros"
        top_marcadores = conteo_marcadores.most_common(8)
        total_top_goles = sum([cant for _, cant in top_marcadores])
        otros_goles = num_ejecuciones - total_top_goles
        
        datos_pastel = {"Marcador": [m for m, _ in top_marcadores], "Cantidad": [c for _, c in top_marcadores]}
        if otros_goles > 0:
            datos_pastel["Marcador"].append("Otros marcadores")
            datos_pastel["Cantidad"].append(otros_goles)
            
        df_pastel = pd.DataFrame(datos_pastel)
        
        # Renderizado de Plotly Express
        fig = px.pie(
            df_pastel, 
            values="Cantidad", 
            names="Marcador", 
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(use_container_width=True, margin=dict(t=10, b=10, l=10, r=10))
        
        # Mostrar el pastel en Streamlit
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla detallada complementaria
        with st.expander("📋 Ver lista completa de frecuencias"):
            df_ranking = pd.DataFrame(conteo_marcadores.items(), columns=["Marcador", "Casos Registrados"]).sort_values(by="Casos Registrados", ascending=False)
            df_ranking["Porcentaje Absoluto"] = (df_ranking["Casos Registrados"] / num_ejecuciones) * 100
            st.dataframe(df_ranking, use_container_width=True, hide_index=True)
