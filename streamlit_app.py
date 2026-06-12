import streamlit as st
import random
import pandas as pd
import plotly.express as px
from collections import Counter

# Configuración de página
st.set_page_config(page_title="Simulador de Marcadores Ofensivo 2026", page_icon="⚽", layout="wide")

st.title("⚽ Simulador Ofensivo de Alta Velocidad - Mundial 2026")
st.write("Modelo calibrado con escala adaptativa: goles dinámicos, impacto de cracks y motivación extrema.")

# --- BASE DE DATOS MEJORADA (GF_promedio, GC_promedio, Racha, Factor_Motivacion_O_Cracks) ---
@st.cache_data
def cargar_base_datos_mundial():
    ratings_48 = {
        # UEFA
        "Francia": (2.8, 0.8, 12, 4.5), "España": (2.7, 0.7, 13, 4.0), "Inglaterra": (2.6, 0.9, 11, 4.0), "Alemania": (2.4, 1.0, 10, 3.5),
        "Portugal": (2.5, 0.9, 12, 3.5), "Países Bajos": (2.2, 1.0, 10, 3.0), "Bélgica": (1.8, 1.1, 9, 2.5), "Italia": (1.9, 1.1, 8, 2.0),
        "Croacia": (1.8, 1.0, 9, 2.5), "Dinamarca": (1.8, 1.2, 8, 2.0), "Suiza": (1.8, 1.1, 9, 2.0), "Austria": (1.9, 1.2, 8, 2.0),
        "Noruega": (2.1, 1.3, 8, 3.5), "Ucrania": (1.7, 1.2, 8, 2.0), "Polonia": (1.6, 1.4, 7, 1.5), "Suecia": (1.9, 1.3, 8, 2.0),
        "Turquía": (1.9, 1.3, 9, 2.5), "República Checa": (1.7, 1.3, 8, 1.5), "Escocia": (1.5, 1.5, 7, 1.0), "Bosnia y Herz.": (1.4, 1.6, 6, 1.0),
        # CONMEBOL
        "Argentina": (2.9, 0.6, 14, 4.5), "Brasil": (2.6, 0.9, 11, 4.0), "Uruguay": (2.5, 1.0, 11, 4.0), "Colombia": (2.4, 0.9, 12, 4.2),
        "Ecuador": (2.2, 0.9, 10, 3.5), "Paraguay": (1.5, 1.1, 8, 1.5), "Bolivia": (1.2, 2.1, 5, 0.5),
        # CONCACAF
        "Estados Unidos": (2.1, 1.1, 10, 3.0), "México": (1.9, 1.2, 8, 2.5), "Canadá": (2.0, 1.2, 9, 2.5), "Panamá": (1.7, 1.3, 8, 1.5),
        "Haití": (1.4, 1.7, 6, 1.0), "Curazao": (1.3, 1.9, 5, 0.5), "Jamaica": (1.6, 1.5, 7, 1.5),
        # CAF (África)
        "Marruecos": (2.3, 0.9, 12, 4.0), "Senegal": (2.2, 1.0, 11, 3.5), "Egipto": (2.1, 1.1, 10, 3.0), "Argelia": (2.0, 1.2, 9, 2.5),
        "Túnez": (1.6, 1.3, 8, 1.5), "Nigeria": (2.2, 1.2, 8, 3.0), "Costa de Marfil": (2.1, 1.1, 10, 3.0), "Ghana": (1.8, 1.3, 8, 2.0),
        "Sudáfrica": (1.6, 1.4, 7, 1.5), "Cabo Verde": (1.6, 1.3, 8, 1.5), "Congo": (1.3, 1.7, 6, 1.0),
        # AFC (Asia) + OFC (Oceanía)
        "Japón": (2.4, 1.0, 11, 3.5), "Corea del Sur": (2.2, 1.1, 10, 3.0), "Irán": (1.9, 1.2, 9, 2.0), "Australia": (1.8, 1.3, 9, 2.0),
        "Arabia Saudita": (1.7, 1.4, 8, 1.5), "Catar": (1.6, 1.5, 7, 1.5), "Jordania": (1.4, 1.5, 7, 1.0), "Uzbekistán": (1.5, 1.3, 8, 1.5),
        "Nueva Zelanda": (1.4, 1.7, 6, 1.0)
    }
    return ratings_48

db_mundial = cargar_base_datos_mundial()

# --- LÓGICA DE RATINGS DINÁMICOS ---
def calcular_rating_dinamico(nombre_equipo, fatiga, lesionados):
    gf, gc, racha, factor_motivacion = db_mundial[nombre_equipo]
    base_poder = 78.0 + (gf * 6.5) - (gc * 4) + ((racha - 8) * 0.5)
    bono_localia = 4.5 if nombre_equipo in ["Estados Unidos", "México", "Canadá"] else 0.0
    penalizacion_fatiga = fatiga * 6.0
    penalizacion_lesiones = lesionados * 3.5
    bono_estrellas = factor_motivacion * 1.2
    factor_inspiracion = random.uniform(-4.0, 4.0)
    
    return max(50.0, base_poder + bono_localia + bono_estrellas - penalizacion_fatiga - penalizacion_lesiones + factor_inspiracion)

# --- INTERFAZ DE CONFIGURACIÓN ---
col_ui1, col_ui2 = st.columns(2)
with col_ui1:
    st.subheader("🏠 Selección 1 / Local")
    eq1_nombre = st.selectbox("Equipo 1", sorted(list(db_mundial.keys())), index=3) # Alemania por defecto
    fatiga_1 = st.slider("Fatiga Acumulada (Eq 1)", 0.0, 1.0, 0.10, step=0.05)
    lesiones_1 = st.number_input("Lesiones (Eq 1)", min_value=0, max_value=4, value=0)

with col_ui2:
    st.subheader("🚀 Selección 2 / Visitante")
    eq2_nombre = st.selectbox("Equipo 2", sorted(list(db_mundial.keys())), index=12) # Curazao por defecto
    fatiga_2 = st.slider("Fatiga Acumulada (Eq 2)", 0.0, 1.0, 0.15, step=0.05)
    lesiones_2 = st.number_input("Lesiones (Eq 2)", min_value=0, max_value=4, value=0)

st.sidebar.header("⚙️ Control de Simulación Masiva")
num_ejecuciones = st.sidebar.number_input("Volumen de simulaciones", min_value=1, max_value=100000, value=50000, step=5000)

# --- EJECUCIÓN DEL MOTOR ---
if st.button("🏟️ Iniciar Simulación de Alta Velocidad", type="primary", use_container_width=True):
    if eq1_nombre == eq2_nombre:
        st.warning("⚠️ Selecciona dos países distintos para jugar el encuentro.")
    else:
        status_text = st.empty()
        status_text.info(f"⏳ Procesando {num_ejecuciones:,} partidos simulados en segundo plano... Por favor, espera.")
        
        conteo_marcadores = Counter()
        victorias_eq1 = 0
        victorias_eq2 = 0
        empates = 0
        
        for _ in range(int(num_ejecuciones)):
            r1 = calcular_rating_dinamico(eq1_nombre, fatiga_1, lesiones_1)
            r2 = calcular_rating_dinamico(eq2_nombre, fatiga_2, lesiones_2)
            
            diff = r1 - r2
            
            # Límites de Poisson base elevados para empujar marcadores reales
            lambda1 = max(0.9, 1.75 + (diff * 0.05))
            lambda2 = max(0.9, 1.75 - (diff * 0.05))
            
            # MOTOR CORREGIDO: Escala de dispersión adaptativa dinámica
            # Si un equipo es muy superior (diff > 0), abre la ventana para goleadas contundentes
            escala_goles1 = 1.35 + (max(0.0, diff) * 0.02)
            escala_goles2 = 1.15
            
            goles1 = max(0, int(random.gammavariate(lambda1, escala_goles1)))
            goles2 = max(0, int(random.gammavariate(lambda2, escala_goles2)))
            
            conteo_marcadores[f"{goles1} - {goles2}"] += 1
            
            if goles1 > goles2:
                victorias_eq1 += 1
            elif goles2 > goles1:
                victorias_eq2 += 1
            else:
                empates += 1
                
        status_text.empty()
        
        # --- PRESENTACIÓN ---
        st.divider()
        st.subheader(f"📊 Reporte de Probabilidades Acumuladas ({num_ejecuciones:,} partidos)")
        
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric(f"Probabilidad de {eq1_nombre}", f"{(victorias_eq1 / num_ejecuciones * 100):.2f}%")
        with kpi2:
            st.metric("Probabilidad de Empate 🤝", f"{(empates / num_ejecuciones * 100):.2f}%")
        with kpi3:
            st.metric(f"Probabilidad de {eq2_nombre}", f"{(victorias_eq2 / num_ejecuciones * 100):.2f}%")
            
        top_uno = conteo_marcadores.most_common(1)
        marcador_comun = top_uno[0][0]
        total_comun = top_uno[0][1]
        
        st.success(f"🎯 El marcador más probable según el modelo es **{marcador_comun}** con un **{(total_comun / num_ejecuciones * 100):.2f}%** de coincidencia.")
        
        # --- GRÁFICO DE PASTEL ---
        st.markdown("### Pie Distribución Porcentual de Marcadores Más Frecuentes")
        
        top_marcadores = conteo_marcadores.most_common(8)
        total_top_goles = sum([cant for _, cant in top_marcadores])
        otros_goles = num_ejecuciones - total_top_goles
        
        datos_pastel = {"Marcador": [m for m, _ in top_marcadores], "Cantidad": [c for _, c in top_marcadores]}
        if otros_goles > 0:
            datos_pastel["Marcador"].append("Otros marcadores")
            datos_pastel["Cantidad"].append(otros_goles)
            
        df_pastel = pd.DataFrame(datos_pastel)
        
        fig = px.pie(
            df_pastel, 
            values="Cantidad", 
            names="Marcador", 
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.YlOrRd
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("📋 Ver lista completa de frecuencias"):
            df_ranking = pd.DataFrame(conteo_marcadores.items(), columns=["Marcador", "Casos Registrados"]).sort_values(by="Casos Registrados", ascending=False)
            df_ranking["Porcentaje Absoluto"] = (df_ranking["Casos Registrados"] / num_ejecuciones) * 100
            st.dataframe(df_ranking, use_container_width=True, hide_index=True)
