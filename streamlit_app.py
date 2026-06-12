import streamlit as st
import random
import pandas as pd
from collections import Counter

# Configuración de página
st.set_page_config(page_title="Simulador Avanzado Mundial 2026", page_icon="⚽", layout="wide")

st.title("⚽ Simulador Experto Partido por Partido - Mundial 2026")
st.write("Historial persistente de resultados y cálculo probabilístico del marcador más repetido.")

# --- INICIALIZADORES DE ESTADO (PERSISTENCIA DE DATOS) ---
if "historial_partidos" not in st.session_state:
    st.session_state.historial_partidos = []

# --- MODELO DE DATOS DEPORTIVOS ---
class Jugador:
    def __init__(self, nombre, posicion, nivel):
        self.nombre = nombre
        self.posicion = posicion  # 'DEL', 'MED', 'DEF', 'POR'
        self.nivel = nivel        # 'Elite' (90), 'Bueno' (80), 'Regular' (70)
        self.rating = 90 if nivel == "Elite" else (80 if nivel == "Bueno" else 70)

class Seleccion:
    def __init__(self, nombre, es_local, gf_ultimos, gc_ultimos, racha_puntos, lista_jugadores):
        self.nombre = nombre
        self.es_local = es_local
        self.gf_promedio = gf_ultimos / 5.0
        self.gc_promedio = gc_ultimos / 5.0
        self.racha_bono = (racha_puntos - 7) * 0.5
        self.jugadores = lista_jugadores
        
        total_rating = sum([j.rating for j in lista_jugadores])
        self.rating_plantilla = total_rating / len(lista_jugadores) if lista_jugadores else 75.0

    def obtener_rating_dinamico(self, fatiga, lesionados):
        base = (self.rating_plantilla * 0.6) + (self.gf_promedio * 20) - (self.gc_promedio * 15) + self.racha_bono
        bono_casa = 4.5 if self.es_local else 0.0
        penalizacion_fatiga = fatiga * 6.0
        penalizacion_lesiones = lesionados * 3.0
        bono_elite = sum([1.5 for j in self.jugadores if j.nivel == "Elite"]) - (lesionados * 0.5)
        
        # Factor sorpresa e inspiración del día
        factor_inspiracion = random.uniform(-4.0, 4.0)
        
        return max(50.0, base + bono_casa + bono_elite - penalizacion_fatiga - penalizacion_lesiones + factor_inspiracion)

# --- BASE DE DATOS MUNDIAL DE 48 EQUIPOS CON RATINGS COMPLETO ---
@st.cache_data
def cargar_base_datos_mundial():
    # Jugadores base para las simulaciones de muestra
    jugadores_por_defecto = [Jugador("Estrella 1", "DEL", "Elite"), Jugador("Estrella 2", "MED", "Bueno"), Jugador("Defensa 1", "DEF", "Bueno"), Jugador("Arquero", "POR", "Regular")]
    
    # Atributos estadísticos por selección
    ratings_48 = {
        # UEFA
        "Francia": (11, 4, 12), "España": (12, 3, 13), "Inglaterra": (10, 4, 11), "Alemania": (11, 5, 10),
        "Portugal": (12, 4, 12), "Países Bajos": (9, 5, 10), "Bélgica": (8, 5, 9), "Italia": (8, 6, 8),
        "Croacia": (7, 5, 9), "Dinamarca": (7, 6, 8), "Suiza": (7, 5, 9), "Austria": (8, 6, 8),
        "Noruega": (9, 6, 8), "Ucrania": (7, 6, 8), "Polonia": (6, 7, 7), "Suecia": (8, 6, 8),
        "Turquía": (8, 6, 9), "República Checa": (7, 6, 8), "Escocia": (6, 7, 7), "Bosnia y Herz.": (5, 8, 6),
        # CONMEBOL
        "Argentina": (12, 3, 14), "Brasil": (11, 5, 11), "Uruguay": (10, 5, 11), "Colombia": (9, 5, 12),
        "Ecuador": (8, 5, 9), "Paraguay": (5, 6, 8), "Bolivia": (5, 10, 5),
        # CONCACAF
        "Estados Unidos": (9, 5, 10), "México": (8, 6, 8), "Canadá": (8, 6, 9), "Panamá": (7, 6, 8),
        "Haití": (5, 8, 6), "Curazao": (4, 9, 5), "Jamaica": (6, 7, 7),
        # CAF (África)
        "Marruecos": (10, 4, 12), "Senegal": (9, 5, 11), "Egipto": (8, 5, 10), "Argelia": (8, 6, 9),
        "Tunisia": (6, 6, 8), "Nigeria": (9, 6, 8), "Costa de Marfil": (8, 5, 10), "Ghana": (7, 6, 8),
        "Sudáfrica": (6, 7, 7), "Cabo Verde": (6, 6, 8), "Congo": (5, 8, 6),
        # AFC (Asia) + OFC (Oceanía)
        "Japón": (10, 5, 11), "Corea del Sur": (9, 5, 10), "Irán": (8, 6, 9), "Australia": (7, 6, 9),
        "Arabia Saudita": (7, 7, 8), "Catar": (6, 7, 7), "Jordania": (5, 7, 7), "Uzbekistán": (6, 6, 8),
        "Nueva Zelanda": (5, 8, 6)
    }
    
    db = {}
    anfitriones = ["Estados Unidos", "México", "Canadá"]
    for pais, (gf, gc, racha) in ratings_48.items():
        db[pais] = Seleccion(pais, es_local=(pais in anfitriones), gf_ultimos=gf, gc_ultimos=gc, racha_puntos=racha, lista_jugadores=jugadores_por_defecto)
    return db

db_mundial = cargar_base_datos_mundial()

# --- INTERFAZ DE CONFIGURACIÓN ---
col_ui1, col_ui2 = st.columns(2)
with col_ui1:
    st.subheader("🏠 Selección 1 / Local")
    eq1_nombre = st.selectbox("Equipo 1", sorted(list(db_mundial.keys())), index=2)
    fatiga_1 = st.slider("Fatiga Acumulada (Eq 1)", 0.0, 1.0, 0.10, step=0.05)
    lesiones_1 = st.number_input("Lesiones (Eq 1)", min_value=0, max_value=4, value=0)

with col_ui2:
    st.subheader("🚀 Selección 2 / Visitante")
    eq2_nombre = st.selectbox("Equipo 2", sorted(list(db_mundial.keys())), index=15)
    fatiga_2 = st.slider("Fatiga Acumulada (Eq 2)", 0.0, 1.0, 0.15, step=0.05)
    lesiones_2 = st.number_input("Lesiones (Eq 2)", min_value=0, max_value=4, value=0)

st.sidebar.header("⚙️ Control de Simulación")
num_ejecuciones = st.sidebar.number_input("Repeticiones del Partido", min_value=1, max_value=5000, value=1, step=10)

if st.sidebar.button("🗑️ Borrar Historial de Partidos"):
    st.session_state.historial_partidos = []
    st.sidebar.success("Historial borrado.")

# --- LÓGICA DEL MOTOR DE ENFRENTAMIENTOS ---
if st.button("🏟️ Simular Encuentro", type="primary", use_container_width=True):
    if eq1_nombre == eq2_nombre:
        st.warning("⚠️ Selecciona dos países distintos.")
    else:
        obj_1 = db_mundial[eq1_nombre]
        obj_2 = db_mundial[eq2_nombre]
        
        for _ in range(int(num_ejecuciones)):
            r1 = obj_1.obtener_rating_dinamico(fatiga_1, lesiones_1)
            r2 = obj_2.obtener_rating_dinamico(fatiga_2, lesiones_2)
            
            diff = r1 - r2
            lambda1 = max(0.4, 1.35 + (diff * 0.045))
            lambda2 = max(0.4, 1.35 - (diff * 0.045))
            
            goles1 = max(0, int(random.gammavariate(lambda1, 1.15)))
            goles2 = max(0, int(random.gammavariate(lambda2, 1.15)))
            
            ganador = eq1_nombre if goles1 > goles2 else (eq2_nombre if goles2 > goles1 else "Empate")
            
            st.session_state.historial_partidos.append({
                "Local 🏠": eq1_nombre,
                "GL": goles1,
                "GV": goles2,
                "Visitante 🚀": eq2_nombre,
                "Resultado Exacto": f"{goles1} - {goles2}",
                "Ganador": ganador
            })

# --- RENDERIZADO ESTADÍSTICO DE RESULTADOS ---
if st.session_state.historial_partidos:
    df_res = pd.DataFrame(st.session_state.historial_partidos)
    
    st.divider()
    st.subheader(f"📊 Análisis Estadístico Acumulado ({len(df_res):,} Partidos Simulado(s))")
    
    # 1. Calcular el marcador más frecuente
    lista_marcadores = df_res["Resultado Exacto"].tolist()
    conteo_marcadores = Counter(lista_marcadores)
    marcador_comun, total_comun = conteo_marcadores.most_common(1)[0]
    porcentaje_comun = (total_comun / len(lista_marcadores)) * 100
    
    # Mostrar KPI métrico en pantalla
    col_kpi1, col_kpi2 = st.columns(2)
    with col_kpi1:
        st.metric(label="🎯 Marcador Más Repetido", value=marcador_comun)
    with col_kpi2:
        st.metric(label="📈 Probabilidad de Coincidencia", value=f"{porcentaje_comun:.2f}%")
        
    # 2. Despliegue de tablas en columnas divididas
    col_v1, col_v2 = st.columns([3, 2])
    with col_v1:
        st.markdown("### 📋 Tabla General de Resultados Recientes")
        st.dataframe(df_res.tail(500), height=400, use_container_width=True) # Muestra los últimos 500 registros para optimizar UI
    with col_v2:
        st.markdown("### 📊 Distribución de Marcadores Frecuentes")
        df_ranking = pd.DataFrame(conteo_marcadores.items(), columns=["Marcador", "Frecuencia"]).sort_values(by="Frecuencia", ascending=False)
        df_ranking["Porcentaje (%)"] = (df_ranking["Frecuencia"] / len(df_res)) * 100
        st.dataframe(df_ranking, height=400, use_container_width=True)
