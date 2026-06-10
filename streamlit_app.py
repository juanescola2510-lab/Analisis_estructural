import streamlit as st
import random
import pandas as pd

# Configuración inicial
st.set_page_config(page_title="Simulador Pro Copa del Mundo 2026", page_icon="🏆", layout="wide")

st.title("🏆 Simulador Hiperrealista - Copa del Mundo 2026")
st.write("Simulación avanzada considerando plantilla, economía, técnico, localía, estadios, fatiga y lesiones.")

# 1. Base de datos con los nuevos factores estructurales por país
# Estructura: (Rating Plantilla, Factor Económico/Infraestructura, Trayectoria Técnico, Mentalidad Base)
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

# Lista de estadios oficiales asignados aleatoriamente a los partidos
ESTADIOS = [
    "Azteca (CDMX, México) 🏟️", "MetLife Stadium (New York, EE.UU.) 🏟️", 
    "SoFi Stadium (Los Angeles, EE.UU.) 🏟️", "BC Place (Vancouver, Canadá) 🏟️",
    "Mercedes-Benz Stadium (Atlanta, EE.UU.) 🏟️", "Hard Rock Stadium (Miami, EE.UU.) 🏟️",
    "Estadio BBVA (Monterrey, México) 🏟️", "BMO Field (Toronto, Canadá) 🏟️"
]

# Inicializadores de estado interno para registrar fatiga y estado físico
if "desgaste" not in st.session_state:
    st.session_state.desgaste = {pais: 0.0 for pais in TEAM_FACTORS}
if "lesionados" not in st.session_state:
    st.session_state.lesionados = {pais: 0 for pais in TEAM_FACTORS}

def calcular_rating_partido(team, es_eliminatoria):
    base = TEAM_FACTORS[team]
    
    # 1. Poder estructural inicial (50% Plantilla, 20% Técnico, 15% Economía, 15% Mentalidad)
    rating_estructural = (base["plantilla"] * 0.50) + (base["tecnico"] * 0.20) + (base["economia"] * 0.15) + (base["mentalidad"] * 0.15)
    
    # 2. Factor Localía (Bono a México, Estados Unidos y Canadá)
    bono_localia = 4.5 if team in ["México", "Estados Unidos", "Canadá"] else 0.0
    
    # 3. Penalizadores dinámicos por Desgaste Físico y Lesiones activas
    penalizacion_desgaste = st.session_state.desgaste[team] * 5.0  # Hasta -5 puntos si la fatiga es máxima (1.0)
    penalizacion_lesiones = st.session_state.lesionados[team] * 2.5  # -2.5 puntos por cada jugador clave lesionado
    
    # En rondas eliminatorias la mentalidad influye el doble bajo presión
    bono_mentalidad_extra = (base["mentalidad"] - 80) * 0.1 if es_eliminatoria else 0.0
    
    rating_final = rating_estructural + bono_localia - penalizacion_desgaste - penalizacion_lesiones + bono_mentalidad_extra
    return max(50.0, rating_final)

def actualizar_salud_y_fatiga(team):
    # Aumentar la fatiga acumulada tras correr un partido intenso
    st.session_state.desgaste[team] = min(1.0, st.session_state.desgaste[team] + random.uniform(0.08, 0.15))
    
    # Probabilidad del 12% de que ocurra una nueva lesión grave en el plantel
    if random.random() < 0.12:
        st.session_state.lesionados[team] += 1

def simulate_match(team1, team2, knockout=False):
    r1 = calcular_rating_partido(team1, knockout)
    r2 = calcular_rating_partido(team2, knockout)
    
    diff = (r1 - r2) / 10.0
    
    # Goles calculados estadísticamente
    g1 = max(0, int(random.normalvariate(1.2 + diff/2, 1.05)))
    g2 = max(0, int(random.normalvariate(1.2 - diff/2, 1.05)))
    
    # Aplicar desgaste post-partido
    actualizar_salud_y_fatiga(team1)
    actualizar_salud_y_fatiga(team2)
    
    if knockout:
        if g1 > g2: return g1, g2, team1
        elif g2 > g1: return g1, g2, team2
        else:
            # Reporte de penales automático en caso de empate
            ganador_penales = random.choice([team1, team2])
            return g1, g2, ganador_penales
            
    return g1, g2, None

# 3. Interfaz de usuario
if st.button("🚀 Iniciar Torneo con Variables Avanzadas", type="primary"):
    # Reiniciar la simulación física médica al presionar el botón
    st.session_state.desgaste = {pais: 0.0 for pais in TEAM_FACTORS}
    st.session_state.lesionados = {pais: 0 for pais in TEAM_FACTORS}
    
    st.header("📋 Fase de Grupos")
    all_classified = []
    third_places = []
    
    cols = st.columns(3)
    idx_col = 0
    
    for group_name, teams in GRUPS_2026.items():
        table = {t: {"Pts": 0, "GF": 0, "GC": 0, "DG": 0} for t in teams}
        
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                t1, t2 = teams[i], teams[j]
                g1, g2, _ = simulate_match(t1, t2, knockout=False)
                
                table[t1]["GF"] += g1
                table[t1]["GC"] += g2
                table[t2]["GF"] += g2
                table[t2]["GC"] += g1
                
                if g1 > g2: 
                    table[t1]["Pts"] += 3
                elif g2 > g1: 
                    table[t2]["Pts"] += 3
                else:
                    table[t1]["Pts"] += 1
                    table[t2]["Pts"] += 1
                    
        for t in teams:
            table[t]["DG"] = table[t]["GF"] - table[t]["GC"]
            
        sorted_table = sorted(table.items(), key=lambda x: (x["Pts"], x["DG"], x["GF"]), reverse=True)
        
        all_classified.append(sorted_table)
        all_classified.append(sorted_table)
        
        third_places.append({
            "Team": sorted_table, 
            "Pts": sorted_table["Pts"],
            "DG": sorted_table["DG"], 
            "GF": sorted_table["GF"]
        })
        
        with cols[idx_col]:
            st.subheader(group_name)
            df_display = pd.DataFrame([
                {
                    "Equipo": item, "Pts": item["Pts"], "DG": item["DG"],
                    "Fatiga 🏃‍♂️": f"{int(st.session_state.desgaste[item]*100)}%",
                    "Lesionados 🩹": st.session_state.lesionados[item]
                }
                for item in sorted_table
            ])
            st.dataframe(df_display, hide_index=True)
            
        idx_col = (idx_col + 1) % 3

    # Filtrado y estructuración de rondas finales
    best_thirds = sorted(third_places, key=lambda x: (x["Pts"], x["DG"], x["GF"]), reverse=True)[:8]
    best_thirds_names = [x["Team"] for x in best_thirds]
    
    r32_teams = all_classified + best_thirds_names
    random.shuffle(r32_teams)

    # 4. Fase Final
    st.divider()
    st.header("🏆 Rondas de Eliminación Directa")
    
    def simulate_knockout_stage(teams, stage_name):
        st.subheader(f"➔ {stage_name}")
        winners = []
        match_summaries = []
        
        for i in range(0, len(teams), 2):
            t1 = teams[i]
            t2 = teams[i+1]
            estadio = random.choice(ESTADIOS)
            g1, g2, winner = simulate_match(t1, t2, knockout=True)
            winners.append(winner)
            
            detalles = f"🏟️ En {estadio} | 🩹 Lesionados: {t1} ({st.session_state.lesionados[t1]}) vs {t2} ({st.session_state.lesionados[t2]})"
            match_summaries.append(f"**{t1}** {g1} - {g2} **{t2}** ➔ **{winner}** avanza\n\n`{detalles}`")
            
        col_s1, col_s2 = st.columns(2)
        half = len(match_summaries) // 2
        
        with col_s1:
            with st.container():
                for text in match_summaries[:half]: 
                    st.write(text)
                    st.write("")
        with col_s2:
            with st.container():
                for text in match_summaries[half:]: 
                    st.write(text)
                    st.write("")
                    
        return winners

    r16_teams = simulate_knockout_stage(r32_teams, "Dieciseisavos de Final")
    r8_teams = simulate_knockout_stage(r16_teams, "Octavos de Final")
    r4_teams = simulate_knockout_stage(r8_teams, "Cuartos de Final")
    finalists = simulate_knockout_stage(r4_teams, "Semifinales")

    # 5. La Gran Final
    st.divider()
    st.subheader("🌟 LA GRAN FINAL 🌟")
    f1, f2 = finalists, finalists
    gf1, gf2, champion = simulate_match(f1, f2, knockout=True)
    
    st.markdown(f"<h3 style='text-align: center;'>🏟️ Sede: MetLife Stadium (New York)</h3>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center;'>{f1} {gf1} vs {gf2} {f2}</h2>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; color: #FFD700;'>🏆 ¡CAMPEÓN DEL MUNDO 2026: {champion.upper()}! 🏆</h1>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # NUEVA LÓGICA: HISTORIAL ACUMULATIVO Y PORCENTAJES DE CAMPEONES
    # -------------------------------------------------------------
    if "historial_campeones" not in st.session_state:
        st.session_state.historial_campeones = []
        
    # Guardamos el campeón actual en la lista histórica
    st.session_state.historial_campeones.append(champion)

# Mostrar las estadísticas globales fuera del bloque del botón para que no desaparezcan
if "historial_campeones" in st.session_state and len(st.session_state.historial_campeones) > 0:
    st.divider()
    st.header("📊 Estadísticas Históricas de Simulación")
    
    total_simulaciones = len(st.session_state.historial_campeones)
    st.write(f"**Total de Mundiales simulados en esta sesión:** {total_simulaciones}")
    
    # Contar cuántas veces ha ganado cada equipo
    conteo_campeones = pd.Series(st.session_state.historial_campeones).value_counts().reset_index()
    conteo_campeones.columns = ["Equipo", "Títulos"]
    
    # Calcular el porcentaje matemático de efectividad
    conteo_campeones["Porcentaje de Éxito"] = (conteo_campeones["Títulos"] / total_simulaciones * 100).round(1)
    conteo_campeones["Porcentaje de Éxito"] = conteo_campeones["Porcentaje de Éxito"].astype(str) + "%"
    
    # Mostrar el top en una tabla interactiva
    st.dataframe(conteo_campeones, hide_index=True, use_container_width=True)
    
    # Añadir un botón para reiniciar el historial si el usuario quiere volver a empezar desde cero
    if st.button("🗑️ Reiniciar Historial Estadístico"):
        st.session_state.historial_campeones = []
        st.rerun()
