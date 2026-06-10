import streamlit as st
import random
import pandas as pd

# Configuración inicial
st.set_page_config(page_title="Simulador Pro Copa del Mundo 2026", page_icon="🏆", layout="wide")

st.title("🏆 Simulador Masivo e Hiperrealista - Copa del Mundo 2026")
st.write("Simulación avanzada considerando plantilla, economía, técnico, localía, estadios, fatiga y lesiones.")

# 1. Base de datos con los nuevos factores estructurales por país
TEAM_FACTORS = {
    # Grupo A
    "México":          {"plantilla": 81, "economia": 85, "tecnico": 78, "mentalidad": 80},
    "Sudáfrica":       {"plantilla": 72, "economia": 75, "tecnico": 72, "mentalidad": 74},
    "Corea del Sur":   {"plantilla": 77, "economia": 88, "tecnico": 76, "mentalidad": 85},
    "República Checa": {"plantilla": 76, "economia": 82, "tecnico": 75, "mentalidad": 78},
    # Grupo B
    "Suiza":           {"plantilla": 79, "economia": 92, "tecnico": 80, "mentalidad": 82},
    "Canadá":          {"plantilla": 77, "economia": 89, "tecnico": 75, "mentalidad": 79},
    "Catar":           {"plantilla": 68, "economia": 95, "tecnico": 74, "mentalidad": 72},
    "Bosnia y Herz.":  {"plantilla": 73, "economia": 70, "tecnico": 71, "mentalidad": 73},
    # Grupo C
    "Brasil":          {"plantilla": 92, "economia": 84, "tecnico": 88, "mentalidad": 89},
    "Marruecos":       {"plantilla": 83, "economia": 80, "tecnico": 84, "mentalidad": 87},
    "Escocia":         {"plantilla": 75, "economia": 83, "tecnico": 74, "mentalidad": 76},
    "Haití":           {"plantilla": 64, "economia": 55, "tecnico": 65, "mentalidad": 70},
    # Grupo D
    "Estados Unidos":  {"plantilla": 82, "economia": 96, "tecnico": 80, "mentalidad": 83},
    "Turquía":         {"plantilla": 78, "economia": 79, "tecnico": 77, "mentalidad": 81},
    "Australia":       {"plantilla": 75, "economia": 86, "tecnico": 74, "mentalidad": 78},
    "Paraguay":        {"plantilla": 74, "economia": 72, "tecnico": 73, "mentalidad": 76},
    # Grupo E
    "Alemania":        {"plantilla": 89, "economia": 93, "tecnico": 87, "mentalidad": 88},
    "Ecuador":         {"plantilla": 80, "economia": 73, "tecnico": 78, "mentalidad": 79},
    "Costa de Marfil": {"plantilla": 78, "economia": 71, "tecnico": 76, "mentalidad": 80},
    "Curazao":         {"plantilla": 65, "economia": 68, "tecnico": 63, "mentalidad": 66},
    # Grupo F
    "Países Bajos":    {"plantilla": 86, "economia": 91, "tecnico": 85, "mentalidad": 84},
    "Japón":           {"plantilla": 82, "economia": 92, "tecnico": 81, "mentalidad": 88},
    "Suecia":          {"plantilla": 78, "economia": 89, "tecnico": 76, "mentalidad": 79},
    "Túnez":           {"plantilla": 72, "economia": 70, "tecnico": 71, "mentalidad": 74},
    # Grupo G
    "Bélgica":         {"plantilla": 85, "economia": 90, "tecnico": 82, "mentalidad": 80},
    "Irán":            {"plantilla": 74, "economia": 72, "tecnico": 73, "mentalidad": 77},
    "Egipto":          {"plantilla": 76, "economia": 74, "tecnico": 75, "mentalidad": 79},
    "Nueva Zelanda":   {"plantilla": 67, "economia": 82, "tecnico": 66, "mentalidad": 72},
    # Grupo H
    "España":          {"plantilla": 91, "economia": 90, "tecnico": 90, "mentalidad": 89},
    "Uruguay":         {"plantilla": 85, "economia": 75, "tecnico": 86, "mentalidad": 92},
    "Arabia Saudita":  {"plantilla": 72, "economia": 96, "tecnico": 78, "mentalidad": 75},
    "Cabo Verde":      {"plantilla": 70, "economia": 62, "tecnico": 68, "mentalidad": 73},
    # Grupo I
    "Francia":         {"plantilla": 93, "economia": 92, "tecnico": 91, "mentalidad": 90},
    "Senegal":         {"plantilla": 79, "economia": 70, "tecnico": 78, "mentalidad": 82},
    "Noruega":         {"plantilla": 78, "economia": 94, "tecnico": 75, "mentalidad": 77},
    "Irak":            {"plantilla": 68, "economia": 67, "tecnico": 69, "mentalidad": 74},
    # Grupo J
    "Argentina":       {"plantilla": 93, "economia": 76, "tecnico": 92, "mentalidad": 95},
    "Argelia":         {"plantilla": 76, "economia": 75, "tecnico": 74, "mentalidad": 78},
    "Austria":         {"plantilla": 78, "economia": 88, "tecnico": 78, "mentalidad": 79},
    "Jordania":        {"plantilla": 66, "economia": 72, "tecnico": 65, "mentalidad": 71},
    # Grupo K
    "Portugal":        {"plantilla": 89, "economia": 88, "tecnico": 84, "mentalidad": 85},
    "Colombia":        {"plantilla": 84, "economia": 74, "tecnico": 82, "mentalidad": 83},
    "Congo":           {"plantilla": 70, "economia": 60, "tecnico": 66, "mentalidad": 72},
    "Uzbekistán":      {"plantilla": 71, "economia": 73, "tecnico": 70, "mentalidad": 74},
    # Grupo L
    "Inglaterra":      {"plantilla": 91, "economia": 94, "tecnico": 86, "mentalidad": 84},
    "Croacia":         {"plantilla": 82, "economia": 80, "tecnico": 83, "mentalidad": 88},
    "Panamá":          {"plantilla": 71, "economia": 76, "tecnico": 72, "mentalidad": 75},
    "Ghana":           {"plantilla": 73, "economia": 68, "tecnico": 73, "mentalidad": 76}
}

GRUPS_2026 = {
    "Grupo A": ["México", "Sudáfrica", "Corea del Sur", "República Checa"],
    "Grupo B": ["Suiza", "Canadá", "Catar", "Bosnia y Herz."],
    "Grupo C": ["Brasil", "Marruecos", "Escocia", "Haití"],
    "Grupo D": ["Estados Unidos", "Turquía", "Australia", "Paraguay"],
    "Grupo E": ["Alemania", "Ecuador", "Costa de Marfil", "Curazao"],
    "Grupo F": ["Países Bajos", "Japón", "Suecia", "Túnez"],
    "Grupo G": ["Bélgica", "Irán", "Egipto", "Nueva Zelanda"],
    "Grupo H": ["España", "Uruguay", "Arabia Saudita", "Cabo Verde"],
    "Grupo I": ["Francia", "Senegal", "Noruega", "Irak"],
    "Grupo J": ["Argentina", "Argelia", "Austria", "Jordania"],
    "Grupo K": ["Portugal", "Colombia", "Congo", "Uzbekistán"],
    "Grupo L": ["Inglaterra", "Croacia", "Panamá", "Ghana"]
}

# Inicializadores de estados globales para almacenar fatigas y bajas temporales por partido
if "desgaste" not in st.session_state:
    st.session_state.desgaste = {pais: 0.0 for pais in TEAM_FACTORS}
if "lesionados" not in st.session_state:
    st.session_state.lesionados = {pais: 0 for pais in TEAM_FACTORS}

def calcular_rating_partido(team, es_eliminatoria):
    base = TEAM_FACTORS[team]
    rating_estructural = (base["plantilla"] * 0.50) + (base["tecnico"] * 0.20) + (base["economia"] * 0.15) + (base["mentalidad"] * 0.15)
    bono_localia = 4.5 if team in ["México", "Estados Unidos", "Canadá"] else 0.0
    penalizacion_desgaste = st.session_state.desgaste[team] * 5.0  
    penalizacion_lesiones = st.session_state.lesionados[team] * 2.5  
    bono_mentalidad_extra = (base["mentalidad"] - 80) * 0.1 if es_eliminatoria else 0.0
    
    return max(50.0, rating_estructural + bono_localia - penalizacion_desgaste - penalizacion_lesiones + bono_mentalidad_extra)

def actualizar_salud_y_fatiga(team):
    st.session_state.desgaste[team] = min(1.0, st.session_state.desgaste[team] + random.uniform(0.08, 0.15))
    if random.random() < 0.12:
        st.session_state.lesionados[team] += 1

def simulate_match(team1, team2, knockout=False):
    r1 = calcular_rating_partido(team1, knockout)
    r2 = calcular_rating_partido(team2, knockout)
    
    diff = r1 - r2
    lambda1 = max(0.5, 1.4 + (diff * 0.05))
    lambda2 = max(0.5, 1.4 - (diff * 0.05))
    
    goles1 = max(0, int(random.gammavariate(lambda1, 1.1)))
    goles2 = max(0, int(random.gammavariate(lambda2, 1.1)))
    
    actualizar_salud_y_fatiga(team1)
    actualizar_salud_y_fatiga(team2)
    
    ganador = None
    perdedor = None
    
    if goles1 > goles2:
        ganador, perdedor = team1, team2
    elif goles2 > goles1:
        ganador, perdedor = team2, team1
    else:
        if knockout:
            # Desempate rápido por penales si requiere ganador directo
            ganador, perdedor = (team1, team2) if random.random() > 0.5 else (team2, team1)
        else:
            ganador, perdedor = None, None # Empate en fase de grupos
            
    return goles1, goles2, ganador, perdedor

# --- CONFIGURACIÓN DE LA SIMULACIÓN MASIVA ---
st.sidebar.header("⚙️ Opciones de Simulación")
num_simulaciones = st.sidebar.number_input("Número de Mundiales a simular", min_value=1, max_value=500, value=10, step=5)

if st.button("🚀 Ejecutar Simulaciones en Serie", type="primary"):
    
    # Estructuras de almacenamiento consolidado para el Podio Histórico
    podios = {pais: {"1° Lugar": 0, "2° Lugar": 0, "3° Lugar": 0, "4° Lugar": 0} for pais in TEAM_FACTORS}
    historial_ganadores = []

    # Barra de progreso visual integrada de Streamlit
    progreso_bar = st.progress(0)
    
    for n in range(1, int(num_simulaciones) + 1):
        # Reiniciar estadísticas físicas al inicio de cada Copa del Mundo individual
        st.session_state.desgaste = {pais: 0.0 for pais in TEAM_FACTORS}
        st.session_state.lesionados = {pais: 0 for pais in TEAM_FACTORS}
        
        # --- FASE DE GRUPOS ---
        clasificados_por_grupo = []
        mejores_terceros_pool = []
        
        for grupo, equipos in GRUPS_2026.items():
            tabla = {eq: {"pts": 0, "gf": 0, "gc": 0} for eq in equipos}
            for i in range(len(equipos)):
                for j in range(i + 1, len(equipos)):
                    eq1, eq2 = equipos[i], equipos[j]
                    g1, g2, g_match, p_match = simulate_match(eq1, eq2, knockout=False)
                    
                    tabla[eq1]["gf"] += g1
                    tabla[eq1]["gc"] += g2
                    tabla[eq2]["gf"] += g2
                    tabla[eq2]["gc"] += g1
                    
                    if g_match == eq1: 
                        tabla[eq1]["pts"] += 3
                    elif g_match == eq2: 
                        tabla[eq2]["pts"] += 3
                    else: 
                        tabla[eq1]["pts"] += 1
                        tabla[eq2]["pts"] += 1
            
            df_t = pd.DataFrame.from_dict(tabla, orient="index")
            df_t["dg"] = df_t["gf"] - df_t["gc"]
            df_t = df_t.sort_values(by=["pts", "dg", "gf"], ascending=False)
            
            # Clasifican los 2 primeros directamente
            clasificados_por_grupo.extend(list(df_t.index[:2]))
            
            # Guardar el 3° lugar de forma correcta usando su posición en el índice
            nombre_tercero = df_t.index[2]
            mejores_terceros_pool.append({
                "equipo": nombre_tercero, 
                "pts": int(df_t.loc[nombre_tercero, "pts"]), 
                "dg": int(df_t.loc[nombre_tercero, "dg"]), 
                "gf": int(df_t.loc[nombre_tercero, "gf"])
            })
            
        # Filtrar los 8 mejores terceros de los 12 grupos
        df_terceros = pd.DataFrame(mejores_terceros_pool).sort_values(by=["pts", "dg", "gf"], ascending=False)
        clasificados_terceros = list(df_terceros["equipo"][:8])
        
        # Consolidación de los 32 equipos que avanzan de ronda
        todos_clasificados = []
        todos_clasificados.extend(clasificados_por_grupo)
        todos_clasificados.extend(clasificados_terceros)
        
        # --- LLAVES ELIMINATORIAS DIRECTAS (Knockout) ---
        # Se genera la lista de rondas mediante una función matemática para evitar pérdidas de texto
        rondas_partidos = list(range(16, 2, -4)) # Esto crea la lista de manera segura y blindada
        
        equipos_activos = todos_clasificados.copy()
        for r_partidos in rondas_partidos:
            proxima_ronda = []
            for p in range(r_partidos):
                eq1 = equipos_activos[p * 2]
                eq2 = equipos_activos[p * 2 + 1]
                _, _, ganador, _ = simulate_match(eq1, eq2, knockout=True)
                proxima_ronda.append(ganador)
            equipos_activos = proxima_ronda.copy()
            
        # Semifinales (Accediendo de forma exacta a los 4 equipos indexados usando variables individuales)
        s1_e1 = equipos_activos[0]
        s1_e2 = equipos_activos[1]
        s2_e1 = equipos_activos[2]
        s2_e2 = equipos_activos[3]
        
        _, _, sem1_ganador, sem1_perdedor = simulate_match(s1_e1, s1_e2, knockout=True)
        _, _, sem2_ganador, sem2_perdedor = simulate_match(s2_e1, s2_e2, knockout=True)
        
        # Partido por el Tercer Puesto (3° y 4°)
        _, _, tercero, cuarto = simulate_match(sem1_perdedor, sem2_perdedor, knockout=True)
        
        # Gran Final (1° y 2°)
        _, _, campeon, subcampeon = simulate_match(sem1_ganador, sem2_ganador, knockout=True)
        
        # Sumar los resultados al registro global estructurado
        podios[campeon]["1° Lugar"] += 1
        podios[subcampeon]["2° Lugar"] += 1
        podios[tercero]["3° Lugar"] += 1
        podios[cuarto]["4° Lugar"] += 1
        
        historial_ganadores.append({"Mundial N°": f"Simulación {n}", "Campeón 🏆": campeon})
        progreso_bar.progress(n / num_simulaciones)

    # --- RENDERIZADO DE RESULTADOS ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 Historial de Ganadores")
        st.dataframe(pd.DataFrame(historial_ganadores), height=450, use_container_width=True)
        
    with col2:
        st.subheader("📊 Tabla de Podios Consolidada")
        df_podios = pd.DataFrame.from_dict(podios, orient="index")
        # Filtrar solo países que hayan alcanzado al menos una semifinal para limpiar la tabla
        df_podios = df_podios[(df_podios != 0).any(axis=1)]
        df_podios = df_podios.sort_values(by=["1° Lugar", "2° Lugar", "3° Lugar", "4° Lugar"], ascending=False)
        st.dataframe(df_podios, height=450, use_container_width=True)

    st.balloons()
