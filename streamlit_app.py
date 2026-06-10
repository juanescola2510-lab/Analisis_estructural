import streamlit as st
import random
import pandas as pd

# Configuración inicial de la página de Streamlit
st.set_page_config(page_title="Simulador Copa del Mundo 2026", page_icon="⚽", layout="wide")

st.title("⚽ Simulador Completo - Copa del Mundo 2026")
st.write("Simula la fase de grupos (48 equipos) y las rondas eliminatorias según el formato oficial.")

# 1. Definición de los 48 equipos con un "Rating de Fuerza" ficticio (del 1 al 99) para dar lógica
TEAMS_RATING = {
    # Grupo A
    "México": 82, "Sudáfrica": 74, "Corea del Sur": 78, "República Checa": 77,
    # Grupo B
    "Suiza": 79, "Canadá": 77, "Catar": 71, "Bosnia y Herzegovina": 74,
    # Grupo C
    "Brasil": 91, "Marruecos": 84, "Escocia": 75, "Haití": 66,
    # Grupo D
    "Estados Unidos": 81, "Turquía": 78, "Australia": 76, "Paraguay": 75,
    # Grupo E
    "Alemania": 89, "Ecuador": 80, "Costa de Marfil": 78, "Curazao": 65,
    # Grupo F
    "Países Bajos": 87, "Japón": 81, "Suecia": 79, "Túnez": 73,
    # Grupo G
    "Bélgica": 86, "Irán": 75, "Egipto": 76, "Nueva Zelanda": 68,
    # Grupo H
    "España": 92, "Uruguay": 86, "Arabia Saudita": 72, "Cabo Verde": 71,
    # Grupo I
    "Francia": 93, "Senegal": 80, "Noruega": 79, "Irak": 70,
    # Grupo J
    "Argentina": 94, "Argelia": 77, "Austria": 79, "Jordania": 68,
    # Grupo K
    "Portugal": 90, "Colombia": 84, "Congo": 71, "Uzbekistán": 72,
    # Grupo L
    "Inglaterra": 91, "Croacia": 83, "Panamá": 72, "Ghana": 74
}

# Grupos oficiales establecidos para el Mundial
GRUPS_2026 = {
    "Grupo A": ["México", "Sudáfrica", "Corea del Sur", "República Checa"],
    "Grupo B": ["Suiza", "Canadá", "Catar", "Bosnia y Herzegovina"],
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

# 2. Motor de simulación de partidos
def simulate_match(team1, team2, knockout=False):
    r1 = TEAMS_RATING[team1]
    r2 = TEAMS_RATING[team2]
    
    diff = (r1 - r2) / 10.0
    
    g1 = max(0, int(random.normalvariate(1.3 + diff/2, 1.1)))
    g2 = max(0, int(random.normalvariate(1.3 - diff/2, 1.1)))
    
    if knockout and g1 == g2:
        if random.choice([True, False]):
            return g1, g2, team1
        else:
            return g1, g2, team2
    return g1, g2, None

# 3. Interfaz de usuario para iniciar la simulación
if st.button("🚀 Comenzar Simulación del Mundial", type="primary"):
    
    st.header("📋 Fase de Grupos - Posiciones Finales")
    
    all_classified = []
    third_places = []
    
    cols = st.columns(3)
    idx_col = 0
    
    for group_name, teams in GRUPS_2026.items():
        table = {t: {"Pts": 0, "GF": 0, "GC": 0, "DG": 0} for t in teams}
        
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                t1, t2 = teams[i], teams[j]
                g1, g2, _ = simulate_match(t1, t2)
                
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
            
        sorted_table = sorted(table.items(), key=lambda x: (x[1]["Pts"], x[1]["DG"], x[1]["GF"]), reverse=True)
        
        # EXTRACCIÓN CORREGIDA: Guardar strings con nombres de países (1º y 2º lugar)
        all_classified.append(sorted_table[0][0])
        all_classified.append(sorted_table[1][0])
        
        # EXTRACCIÓN CORREGIDA: Guardar datos del 3º lugar
        third_places.append({
            "Team": sorted_table[2][0],
            "Pts": sorted_table[2][1]["Pts"],
            "DG": sorted_table[2][1]["DG"],
            "GF": sorted_table[2][1]["GF"]
        })
        
        with cols[idx_col]:
            st.subheader(group_name)
            df_display = pd.DataFrame([
                {"Equipo": item[0], "Pts": item[1]["Pts"], "DG": item[1]["DG"], "GF": item[1]["GF"]}
                for item in sorted_table
            ])
            st.dataframe(df_display, hide_index=True)
            
        idx_col = (idx_col + 1) % 3

    # Filtrar mejores terceros
    best_thirds = sorted(third_places, key=lambda x: (x["Pts"], x["DG"], x["GF"]), reverse=True)[:8]
    best_thirds_names = [x["Team"] for x in best_thirds]
    
    # Lista de los 32 clasificados finales en formato limpio de texto
    r32_teams = all_classified + best_thirds_names
    random.shuffle(r32_teams)  
    
    # 4. Fase Final de Eliminación Directa
    st.divider()
    st.header("🏆 Rondas de Eliminación Directa")
    
    def simulate_knockout_stage(teams, stage_name):
        st.subheader(f"➔ {stage_name}")
        winners = []
        match_summaries = []
        
        for i in range(0, len(teams), 2):
            t1 = teams[i]
            t2 = teams[i+1]
            g1, g2, winner = simulate_match(t1, t2, knockout=True)
            winners.append(winner)
            match_summaries.append(f"**{t1}** {g1} - {g2} **{t2}** ➔ Clasifica: **{winner}**")
            
        col_s1, col_s2 = st.columns(2)
        half = len(match_summaries) // 2
        
        with col_s1:
            with st.container():
                for text in match_summaries[:half]: 
                    st.write(text)
        with col_s2:
            with st.container():
                for text in match_summaries[half:]: 
                    st.write(text)
            
        return winners

    # Secuencia del torneo cronológica
    r16_teams = simulate_knockout_stage(r32_teams, "Dieciseisavos de Final (Ronda de 32)")
    r8_teams = simulate_knockout_stage(r16_teams, "Octavos de Final")
    r4_teams = simulate_knockout_stage(r8_teams, "Cuartos de Final")
    finalists = simulate_knockout_stage(r4_teams, "Semifinales")
    
    # 5. La Gran Final
    st.divider()
    st.subheader("🌟 LA GRAN FINAL (MetLife Stadium) 🌟")
    f1, f2 = finalists[0], finalists[1]
    gf1, gf2, champion = simulate_match(f1, f2, knockout=True)
    
    st.markdown(f"<h3 style='text-align: center;'>{f1} {gf1} vs {gf2} {f2}</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; color: #FFD700;'>🏆 ¡CAMPEÓN DEL MUNDO 2026: {champion.upper()}! 🏆</h1>", unsafe_allow_html=True)
