import streamlit as st
import random
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Simulador Match-by-Match Mundial 2026", page_icon="⚽", layout="wide")

st.title("⚽ Simulador Profesional Partido por Partido - Mundial 2026")
st.write("Modelo predictivo basado en convocatorias reales, nivel de jugadores, fatiga acumulada y racha histórica.")

# --- MODELO DE DATOS DEPORTIVOS ---
class Jugador:
    def __init__(self, nombre, posicion, nivel):
        self.nombre = nombre
        self.posicion = posicion  # 'DEL', 'MED', 'DEF', 'POR'
        self.nivel = nivel        # 'Elite' (90), 'Bueno' (80), 'Regular' (70)
        
        # Asignar rating según calidad
        if nivel == "Elite":
            self.rating = 90
        elif nivel == "Bueno":
            self.rating = 80
        else:
            self.rating = 70

class Seleccion:
    def __init__(self, nombre, es_local, gf_ultimos, gc_ultimos, racha_puntos, lista_jugadores):
        self.nombre = nombre
        self.es_local = es_local
        self.gf_promedio = gf_ultimos / 5.0  # Métrica de ataque histórico
        self.gc_promedio = gc_ultimos / 5.0  # Métrica de defensa histórica
        self.racha_bono = (racha_puntos - 7) * 0.5  # Bono si viene ganando mucho
        self.jugadores = lista_jugadores
        
        # Calcular poder de la plantilla basado en sus jugadores
        total_rating = sum([j.rating for j in lista_jugadores])
        self.rating_plantilla = total_rating / len(lista_jugadores) if lista_jugadores else 70.0

    def obtener_rating_dinamico(self, fatiga, lesionados):
        # 1. Poder Base (Plantilla + Historial de goles)
        base = (self.rating_plantilla * 0.6) + (self.gf_promedio * 20) - (self.gc_promedio * 15) + self.racha_bono
        
        # 2. Factor Localía
        bono_casa = 4.5 if self.es_local else 0.0
        
        # 3. Penalizadores físicos y bajas
        penalizacion_fatiga = fatiga * 6.0  # Hasta -6 puntos por fatiga crítica
        penalizacion_lesiones = lesionados * 3.0
        
        # Contar cuántos jugadores de alto nivel ('Elite') tiene disponibles en el campo
        bono_elite = sum([1.5 for j in self.jugadores if j.nivel == "Elite"]) - (lesionados * 0.5)
        
        rating_final = base + bono_casa + bono_elite - penalizacion_fatiga - penalizacion_lesiones
        return max(50.0, rating_final)

# --- BASE DE DATOS ESTRUCTURADA DE SELECCIONES ---
@st.cache_data
def cargar_base_datos():
    # Jugadores de ejemplo (puedes ampliar las listas con más nombres y posiciones oficiales)
    convocados_ecuador = [
        Jugador("Piero Hincapié", "DEF", "Elite"),
        Jugador("Moises Caicedo", "MED", "Elite"),
        Jugador("Enner Valencia", "DEL", "Bueno"),
        Jugador("Willian Pacho", "DEF", "Bueno"),
        Jugador("Kendry Páez", "MED", "Bueno"),
        Jugador("Hernán Galíndez", "POR", "Regular")
    ]
    
    convocados_argentina = [
        Jugador("Lionel Messi", "DEL", "Elite"),
        Jugador("Emiliano Martínez", "POR", "Elite"),
        Jugador("Rodrigo de Paul", "MED", "Bueno"),
        Jugador("Cristian Romero", "DEF", "Elite"),
        Jugador("Lautaro Martínez", "DEL", "Bueno"),
        Jugador("Enzo Fernández", "MED", "Bueno")
    ]
    
    convocados_francia = [
        Jugador("Kylian Mbappé", "DEL", "Elite"),
        Jugador("Antoine Griezmann", "MED", "Elite"),
        Jugador("William Saliba", "DEF", "Elite"),
        Jugador("Aurélien Tchouaméni", "MED", "Bueno"),
        Jugador("Ousmane Dembélé", "DEL", "Bueno"),
        Jugador("Mike Maignan", "POR", "Bueno")
    ]

    convocados_mexico = [
        Jugador("Santiago Giménez", "DEL", "Bueno"),
        Jugador("Edson Álvarez", "MED", "Elite"),
        Jugador("César Montes", "DEF", "Bueno"),
        Jugador("Luis Chávez", "MED", "Bueno"),
        Jugador("Malagón", "POR", "Regular")
    ]

    db = {
        "Ecuador": Seleccion("Ecuador", es_local=False, gf_ultimos=8, gc_ultimos=4, racha_puntos=11, lista_jugadores=convocados_ecuador),
        "Argentina": Seleccion("Argentina", es_local=False, gf_ultimos=12, gc_ultimos=3, racha_puntos=13, lista_jugadores=convocados_argentina),
        "Francia": Seleccion("Francia", es_local=False, gf_ultimos=11, gc_ultimos=5, racha_puntos=10, lista_jugadores=convocados_francia),
        "México": Seleccion("México", es_local=True, gf_ultimos=7, gc_ultimos=6, racha_puntos=8, lista_jugadores=convocados_mexico)
    }
    return db

db_equipos = cargar_base_datos()

# --- INTERFAZ DINÁMICA DE SELECCIÓN DE PARTIDO ---
col_ui1, col_ui2 = st.columns(2)

with col_ui1:
    st.subheader("🏠 Equipo Local / Equipo 1")
    eq1_nombre = st.selectbox("Selecciona Selección 1", list(db_equipos.keys()), index=3)
    fatiga_1 = st.slider("Desgaste Físico Acumulado (Eq 1)", 0.0, 1.0, 0.15, step=0.05, help="0.0 es fresco, 1.0 es fatiga extrema")
    lesiones_1 = st.number_input("Jugadores Clave Lesionados / Bajas (Eq 1)", min_value=0, max_value=4, value=0)

with col_ui2:
    st.subheader("🚀 Equipo Visitante / Equipo 2")
    eq2_nombre = st.selectbox("Selecciona Selección 2", list(db_equipos.keys()), index=0)
    fatiga_2 = st.slider("Desgaste Físico Acumulado (Eq 2)", 0.0, 1.0, 0.20, step=0.05)
    lesiones_2 = st.number_input("Jugadores Clave Lesionados / Bajas (Eq 2)", min_value=0, max_value=4, value=0)

st.divider()

# --- MOTOR DE CÁLCULO Y SIMULACIÓN DE GOLES ---
if st.button("🏟️ Simular Partido Individual", type="primary", use_container_width=True):
    
    if eq1_nombre == eq2_nombre:
        st.warning("⚠️ Debes seleccionar dos equipos diferentes para simular un partido.")
    else:
        obj_eq1 = db_equipos[eq1_nombre]
        obj_eq2 = db_equipos[eq2_nombre]
        
        # Obtener ratings con penalizadores aplicados
        r1 = obj_eq1.obtener_rating_dinamico(fatiga_1, lesiones_1)
        r2 = obj_eq2.obtener_rating_dinamico(fatiga_2, lesiones_2)
        
        # Distribución de Poisson basada en diferencias de rendimiento
        diff = r1 - r2
        lambda1 = max(0.4, 1.35 + (diff * 0.045))
        lambda2 = max(0.4, 1.35 - (diff * 0.045))
        
        goles1 = max(0, int(random.gammavariate(lambda1, 1.15)))
        goles2 = max(0, int(random.gammavariate(lambda2, 1.15)))
        
        # --- PRESENTACIÓN VISUAL MARCADOR ---
        st.markdown("<h2 style='text-align: center;'>🏆 MARCADOR FINAL 🏆</h2>", unsafe_style=True)
        
        m_col1, m_col2, m_col3 = st.columns([2, 1, 2])
        with m_col1:
            st.markdown(f"<h1 style='text-align: right;'>{eq1_nombre}</h1>", unsafe_style=True)
            st.caption(f"Rating de campo calculado: **{r1:.1f}**")
        with m_col2:
            st.markdown(f"<h1 style='text-align: center; color: #ff4b4b;'>{goles1} - {goles2}</h1>", unsafe_style=True)
        with m_col3:
            st.markdown(f"<h1 style='text-align: left;'>{eq2_nombre}</h1>", unsafe_style=True)
            st.caption(f"Rating de campo calculado: **{r2:.1f}**")
            
        # Desempate de Fase Eliminatoria Directa
        if goles1 == goles2:
            st.info("👔 ¡Empate en tiempo reglamentario! Se define por tanda de penaltis.")
            p1, p2 = 0, 0
            while p1 == p2:
                p1 = random.randint(3, 5) + random.randint(0, 2)
                p2 = random.randint(3, 5) + random.randint(0, 2)
            st.subheader(f"🎯 Definición por Penales: {eq1_nombre} ({p1}) - ({p2}) {eq2_nombre}")
            ganador_final = eq1_nombre if p1 > p2 else eq2_nombre
            st.success(f"🎉 Avanza de ronda: **{ganador_final}**")
        elif goles1 > goles2:
            st.success(f"🎉 Ganador del encuentro: **{eq1_nombre}**")
        else:
            st.success(f"🎉 Ganador del encuentro: **{eq2_nombre}**")
            
        # --- DESGLOSE DE ANÁLISIS DE CAMPO ---
        with st.expander("🔍 Ver reporte técnico detallado del partido"):
            st.write("### Ficha de Plantillas e Impacto de Jugadores de Alto Nivel:")
            
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                st.write(f"**Convocados de {eq1_nombre}:**")
                df1 = pd.DataFrame([{"Jugador": j.nombre, "Posición": j.posicion, "Calidad": j.nivel, "Rating": j.rating} for j in obj_eq1.jugadores])
                st.dataframe(df1, use_container_width=True)
                st.metric("Promedio Ataque Histórico", f"{obj_eq1.gf_promedio:.2f} goles/partido")
                
            with c_p2:
                st.write(f"**Convocados de {eq2_nombre}:**")
                df2 = pd.DataFrame([{"Jugador": j.nombre, "Posición": j.posicion, "Calidad": j.nivel, "Rating": j.rating} for j in obj_eq2.jugadores])
                st.dataframe(df2, use_container_width=True)
                st.metric("Promedio Ataque Histórico", f"{obj_eq2.gf_promedio:.2f} goles/partido")
