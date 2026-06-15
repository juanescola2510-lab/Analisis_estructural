import streamlit as st
import random
import pandas as pd
import plotly.express as px
from collections import Counter

# 1. Configuración de la página de Streamlit
st.set_page_config(page_title="Simulador Real-Time Mundial 2026", page_icon="🏆", layout="wide")

st.title("🏆 Simulador Mundial 2026 con Resultados Reales")
st.markdown("### Estado actual: Jornada del 15 de Junio. Datos inyectados de los primeros partidos oficiales.")

# --- 2. BASE DE DATOS DE RATINGS ACTUALIZADA ---
@st.cache_data
def cargar_base_datos_mundial():
    return {
        # UEFA
        "Francia": (2.8, 0.8, 12, 4.5), "España": (2.7, 0.7, 13, 4.0), "Inglaterra": (2.6, 0.9, 11, 4.0), "Alemania": (2.5, 0.9, 11, 3.8),
        "Portugal": (2.5, 0.9, 12, 3.5), "Países Bajos": (2.2, 1.0, 10, 3.0), "Bélgica": (1.8, 1.1, 9, 2.5), "Italia": (1.9, 1.1, 8, 2.0),
        "Croacia": (1.8, 1.0, 9, 2.5), "Dinamarca": (1.8, 1.2, 8, 2.0), "Suiza": (1.8, 1.1, 9, 2.0), "Austria": (1.9, 1.2, 8, 2.0),
        "Noruega": (2.1, 1.3, 8, 3.5), "Ucrania": (1.7, 1.2, 8, 2.0), "Polonia": (1.6, 1.4, 7, 1.5), "Suecia": (2.0, 1.2, 9, 2.5),
        "Turquía": (1.8, 1.4, 8, 2.0), "República Checa": (1.7, 1.3, 8, 1.5), "Escocia": (1.6, 1.4, 8, 1.5), "Bosnia y Herz.": (1.4, 1.5, 7, 1.2),
        # CONMEBOL
        "Argentina": (2.9, 0.6, 14, 4.5), "Brasil": (2.5, 1.0, 10, 3.8), "Uruguay": (2.5, 1.0, 11, 4.0), "Colombia": (2.4, 0.9, 12, 4.2),
        "Ecuador": (2.2, 0.9, 10, 3.5), "Paraguay": (1.4, 1.3, 7, 1.2), "Bolivia": (1.2, 2.1, 5, 0.5),
        # CONCACAF
        "Estados Unidos": (2.2, 1.0, 11, 3.2), "México": (2.0, 1.1, 9, 2.8), "Canadá": (1.9, 1.2, 8, 2.3), "Panamá": (1.7, 1.3, 8, 1.5),
        "Haití": (1.3, 1.7, 6, 1.0), "Curazao": (1.2, 2.2, 4, 0.5), "Jamaica": (1.6, 1.5, 7, 1.5),
        # CAF
        "Marruecos": (2.3, 0.9, 12, 4.0), "Senegal": (2.2, 1.0, 11, 3.5), "Egipto": (2.1, 1.1, 10, 3.0), "Argelia": (2.0, 1.2, 9, 2.5),
        "Túnez": (1.5, 1.5, 7, 1.0), "Nigeria": (2.2, 1.2, 8, 3.0), "Costa de Marfil": (2.2, 1.0, 11, 3.5), "Ghana": (1.8, 1.3, 8, 2.0),
        "Sudáfrica": (1.5, 1.5, 6, 1.0), "Cabo Verde": (1.6, 1.3, 8, 1.5), "Congo": (1.3, 1.7, 6, 1.0),
        # AFC + OFC
        "Japón": (2.4, 1.0, 11, 3.5), "Corea del Sur": (2.3, 1.1, 11, 3.2), "Irán": (1.9, 1.2, 9, 2.0), "Australia": (1.9, 1.2, 9, 2.2),
        "Arabia Saudita": (1.7, 1.4, 8, 1.5), "Catar": (1.6, 1.5, 7, 1.5), "Jordania": (1.4, 1.5, 7, 1.0), "Uzbekistán": (1.5, 1.3, 8, 1.5),
        "Nueva Zelanda": (1.4, 1.7, 6, 1.0), "Irak": (1.5, 1.4, 7, 1.5)
    }

db_mundial = cargar_base_datos_mundial()

# --- 3. CONFIGURACIÓN ESTRUCTURAL DE GRUPOS ---
GRUPOS_2026 = {
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

# --- 4. DICCIONARIO DE RESULTADOS OFICIALES (PARTIDOS YA JUGADOS) ---
PARTIDOS_REALES = {
    ("México", "Sudáfrica"): (2, 0),
    ("Corea del Sur", "República Checa"): (2, 1),
    ("Canadá", "Bosnia y Herz."): (1, 1),
    ("Suiza", "Catar"): (1, 1),
    ("Brasil", "Marruecos"): (1, 1),
    ("Escocia", "Haití"): (1, 0),
    ("Estados Unidos", "Paraguay"): (4, 1),
    ("Australia", "Turquía"): (2, 0),
    ("Alemania", "Curazao"): (7, 1),
    ("Costa de Marfil", "Ecuador"): (1, 0),
    ("Países Bajos", "Japón"): (2, 2),
    ("Suecia", "Túnez"): (5, 1)
}

# --- 5. MOTOR DE RATINGS Y SIMULADOR ---
def calcular_rating_dinamico(nombre_equipo):
    gf, gc, racha, factor_motivacion = db_mundial[nombre_equipo]
    base_poder = 78.0 + (gf * 6.5) - (gc * 4) + ((racha - 8) * 0.5)
    bono_localia = 4.5 if nombre_equipo in ["Estados Unidos", "México", "Canadá"] else 0.0
    return max(50.0, base_poder + bono_localia + (factor_motivacion * 1.2) + random.uniform(-4.0, 4.0))

def simular_partido_torneo(eq1, eq2):
    r1 = calcular_rating_dinamico(eq1)
    r2 = calcular_rating_dinamico(eq2)
    diff = r1 - r2
    lambda1 = max(0.9, 1.75 + (diff * 0.05))
    lambda2 = max(0.9, 1.75 - (diff * 0.05))
    
    g1 = max(0, int(random.gammavariate(lambda1, 1.35 + (max(0.0, diff) * 0.02))))
    g2 = max(0, int(random.gammavariate(lambda2, 1.15)))
    
    if g1 > g2: return eq1, eq2
    elif g2 > g1: return eq2, eq1
    return (eq1, eq2) if random.random() > 0.5 else (eq2, eq1)

# --- 6. INTERFAZ ---
st.sidebar.header("⚙️ Configuración del Analítico")
num_simulaciones = st.sidebar.number_input("Mundiales a Simular", min_value=1, max_value=100000, value=30000, step=5000)

if st.button("🚀 Iniciar Simulación en Tiempo Real", type="primary", use_container_width=True):
    status_text = st.empty()
    status_text.info(f"⏳ Procesando {num_simulaciones:,} escenarios continuos a partir de los datos reales...")
    
    conteos_campeon = Counter()
    conteos_podio = {pais: {"2° Lugar": 0, "3° Lugar": 0, "4° Lugar": 0, "Llegó a 16avos": 0} for pais in db_mundial}
    
    # Inicialización del diccionario histórico para registrar los marcadores de cada cruce
    historial_marcadores_cruces = {}
    for grupo, eqs in GRUPOS_2026.items():
        for i, eq1 in enumerate(eqs):
            for eq2 in eqs[i+1:]:
                historial_marcadores_cruces[f"{eq1} vs {eq2}"] = Counter()
                
    grupos_items = list(GRUPOS_2026.items())
    
    for n in range(1, int(num_simulaciones) + 1):
        clasificados_por_grupo = []
        mejores_terceros_pool = []
        
        for grupo, equipos in grupos_items:
            tabla = {eq: {"eq": eq, "pts": 0, "dg": 0, "gf": 0, "gc": 0} for eq in equipos}
            
            for i in range(4):
                for j in range(i + 1, 4):
                    team_a = equipos[i]
                    team_b = equipos[j]
                    llave_partido = f"{team_a} vs {team_b}"
                    
                    # SI EL PARTIDO YA SE JUGÓ EN LA REALIDAD, USAR SU RESULTADO
                    if (team_a, team_b) in PARTIDOS_REALES:
                        g1, g2 = PARTIDOS_REALES[(team_a, team_b)]
                    elif (team_b, team_a) in PARTIDOS_REALES:
                        g2, g1 = PARTIDOS_REALES[(team_b, team_a)]
                    else:
                        # SIMULAR CON MOTOR PROBABILÍSTICO
                        r1 = calcular_rating_dinamico(team_a)
                        r2 = calcular_rating_dinamico(team_b)
                        diff = r1 - r2
                        l1 = max(0.9, 1.75 + (diff * 0.05))
                        l2 = max(0.9, 1.75 - (diff * 0.05))
                        g1 = max(0, int(random.gammavariate(l1, 1.35 + (max(0.0, diff) * 0.02))))
                        g2 = max(0, int(random.gammavariate(l2, 1.15)))
                    
                    # Guardar el marcador obtenido en esta iteración particular
                    if llave_partido in historial_marcadores_cruces:
                        historial_marcadores_cruces[llave_partido][f"{g1} - {g2}"] += 1
                    
                    if g1 > g2:
                        tabla[team_a]["pts"] += 3
                    elif g2 > g1:
                        tabla[team_b]["pts"] += 3
                    else:
                        tabla[team_a]["pts"] += 1; tabla[team_b]["pts"] += 1
                        
                    tabla[team_a]["gf"] += g1; tabla[team_a]["gc"] += g2
                    tabla[team_b]["gf"] += g2; tabla[team_b]["gc"] += g1
            
            for eq in equipos:
                tabla[eq]["dg"] = tabla[eq]["gf"] - tabla[eq]["gc"]
            ordenados = sorted(tabla.values(), key=lambda x: (x["pts"], x["dg"], x["gf"]), reverse=True)
            
            clasificados_por_grupo.append(ordenados[0]["eq"])
            clasificados_por_grupo.append(ordenados[1]["eq"])
            mejores_terceros_pool.append(ordenados[2])
            
        mejores_terceros_ordenados = sorted(mejores_terceros_pool, key=lambda x: (x["pts"], x["dg"], x["gf"]), reverse=True)
        for k in range(8):
            clasificados_por_grupo.append(mejores_terceros_ordenados[k]["eq"])
            
        # Marcado de equipos que superaron grupos
        for clasificado in clasificados_por_grupo:
            conteos_podio[clasificado]["Llegó a 16avos"] += 1

        # --- KNOCKOUTS (Con almacenamiento de llaves más frecuentes) ---
        if n == 1:
            # Inicializar contadores históricos de llaves en la primera corrida
            conteos_llaves = {
                "R32": Counter(), "R16": Counter(), "Cuartos": Counter(), 
                "Semis": Counter(), "Tercero": Counter(), "Final": Counter()
            }

        r32_ganadores = []
        random.shuffle(clasificados_por_grupo)
        for i in range(0, 32, 2):
            eq_a, eq_b = clasificados_por_grupo[i], clasificados_por_grupo[i+1]
            conteos_llaves["R32"][f"{eq_a} vs {eq_b}"] += 1
            ganador, _ = simular_partido_torneo(eq_a, eq_b)
            r32_ganadores.append(ganador)
            
        r16_ganadores = []
        for i in range(0, 16, 2):
            eq_a, eq_b = r32_ganadores[i], r32_ganadores[i+1]
            conteos_llaves["R16"][f"{eq_a} vs {eq_b}"] += 1
            ganador, _ = simular_partido_torneo(eq_a, eq_b)
            r16_ganadores.append(ganador)
            
        r8_ganadores = []
        for i in range(0, 8, 2):
            eq_a, eq_b = r16_ganadores[i], r16_ganadores[i+1]
            conteos_llaves["Cuartos"][f"{eq_a} vs {eq_b}"] += 1
            ganador, _ = simular_partido_torneo(eq_a, eq_b)
            r8_ganadores.append(ganador)
            
        conteos_llaves["Semis"][f"{r8_ganadores[0]} vs {r8_ganadores[1]}"] += 1
        semi1_ganador, semi1_perdedor = simular_partido_torneo(r8_ganadores[0], r8_ganadores[1])
        
        conteos_llaves["Semis"][f"{r8_ganadores[2]} vs {r8_ganadores[3]}"] += 1
        semi2_ganador, semi2_perdedor = simular_partido_torneo(r8_ganadores[2], r8_ganadores[3])
        
        conteos_llaves["Tercero"][f"{semi1_perdedor} vs {semi2_perdedor}"] += 1
        tercer_lugar, cuarto_lugar = simular_partido_torneo(semi1_perdedor, semi2_perdedor)
        
        conteos_llaves["Final"][f"{semi1_ganador} vs {semi2_ganador}"] += 1
        campeon, subcampeon = simular_partido_torneo(semi1_ganador, semi2_ganador)
        
        conteos_campeon[campeon] += 1
        conteos_podio[subcampeon]["2° Lugar"] += 1
        conteos_podio[tercer_lugar]["3° Lugar"] += 1
        conteos_podio[cuarto_lugar]["4° Lugar"] += 1

    status_text.success("✅ ¡Procesamiento estadístico completado!")
    
    # --- DESPLIEGUE ---
    st.header("📊 Resultados Estadísticos del Análisis Probabilístico")
    
    df_campeones = pd.DataFrame(conteos_campeon.items(), columns=["Selección", "Títulos"]).sort_values(by="Títulos", ascending=False)
    df_campeones["Probabilidad de Campeonar"] = (df_campeones["Títulos"] / num_simulaciones * 100).round(2).astype(str) + "%"
    
    df_podio = pd.DataFrame.from_dict(conteos_podio, orient='index').reset_index().rename(columns={'index': 'Selección'})
    df_podio["% Clasificación a 16avos"] = (df_podio["Llegó a 16avos"] / num_simulaciones * 100).round(1).astype(str) + "%"
    
    df_final = pd.merge(df_campeones, df_podio, on="Selección", how="left")
    
    tab1, tab2, tab3 = st.tabs(["🏆 Cuadro de Honor", "⚽ Análisis de Partidos (Grupos)", "🌿 Árbol de Eliminación Más Probable"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Top de Candidatos al Título")
            st.dataframe(df_final[["Selección", "Probabilidad de Campeonar", "% Clasificación a 16avos"]].head(15), use_container_width=True)
        with col2:
            st.subheader("🇪🇨 Situación de Ecuador")
            ecuador_data = df_final[df_final["Selección"] == "Ecuador"]
            if not ecuador_data.empty:
                prob_pase = ecuador_data["% Clasificación a 16avos"].values
                st.metric(label="Opciones de avanzar a 16avos", value=prob_pase, delta="Obligado a vencer a Curazao")
                st.markdown("**Nota metodológica:** El tropiezo real en el debut ante Costa de Marfil (1-0) reduce el margen de error para clasificar entre los mejores terceros.")
            else:
                st.error("Sin datos consolidados para Ecuador.")

    with tab2:
        st.subheader("📋 Resultados Reales y Predicciones de Marcador Más Probable")
        st.write("🟢 Partidos jugados en la realidad. 🔮 Predicciones basadas en la moda estadística de la simulación masiva.")
        
        datos_partidos = []
        for grupo, equipos in GRUPOS_2026.items():
            for i in range(4):
                for j in range(i + 1, 4):
                    t_a = equipos[i]
                    t_b = equipos[j]
                    llave_str = f"{t_a} vs {t_b}"
                    
                    if (t_a, t_b) in PARTIDOS_REALES:
                        marcador_final = f"{PARTIDOS_REALES[(t_a, t_b)][0]} - {PARTIDOS_REALES[(t_a, t_b)][1]}"
                        tipo = "🟢 Real (Fijo)"
                    elif (t_b, t_a) in PARTIDOS_REALES:
                        marcador_final = f"{PARTIDOS_REALES[(t_b, t_a)][0]} - {PARTIDOS_REALES[(t_b, t_a)][1]}"
                        tipo = "🟢 Real (Fijo)"
                    else:
                        if llave_str in historial_marcadores_cruces and historial_marcadores_cruces[llave_str]:
                            marcador_final = historial_marcadores_cruces[llave_str].most_common(1)[0][0]
                        else:
                            marcador_final = "0 - 0"
                        tipo = "🔮 Proyectado (Frecuente)"
                    
                    datos_partidos.append({
                        "Grupo": grupo, "Partido": llave_str, "Marcador Más Probable": marcador_final, "Condición": tipo
                    })
        
        df_partidos_analisis = pd.DataFrame(datos_partidos)
        st.dataframe(df_partidos_analisis, use_container_width=True, height=400)

    with tab3:
        st.subheader("🌿 Estructura del Árbol de Eliminación Directa Predictivo")
        st.write("A continuación se grafican las llaves KO más concurrentes resultantes del análisis estadístico general:")
        
        # Obtener las llaves modales más comunes de las simulaciones
        top_r32 = [x[0] for x in conteos_llaves["R32"].most_common(4)]
        top_r16 = [x[0] for x in conteos_llaves["R16"].most_common(2)]
        top_qf = [x[0] for x in conteos_llaves["Cuartos"].most_common(2)]
        top_sf = [x[0] for x in conteos_llaves["Semis"].most_common(1)]
        top_3ro = [x[0] for x in conteos_llaves["Tercero"].most_common(1)]
        top_fi = [x[0] for x in conteos_llaves["Final"].most_common(1)]
        
        # Renderizado del árbol de flujo utilizando Graphviz sintáctico nativo
        codigo_grafica = f"""
        digraph G {{
            rankdir=LR;
            node [shape=box, style=filled, color="lightblue", fontname="Arial"];
            
            subgraph cluster_32 {{
                label = "Dieciseisavos de Final (Ejemplos Comunes)";
                color = lightgrey;
                "{top_r32[0] if len(top_r32) > 0 else 'Llave A'}";
                "{top_r32[1] if len(top_r32) > 1 else 'Llave B'}";
            }}
            
            subgraph cluster_16 {{
                label = "Octavos de Final Más Repetidos";
                color = blue;
                "{top_r16[0] if len(top_r16) > 0 else 'Octavos 1'}";
                "{top_r16[1] if len(top_r16) > 1 else 'Octavos 2'}";
            }}
            
            subgraph cluster_4s {{
                label = "Cuartos de Final Tendencia";
                color = green;
                "{top_qf[0] if len(top_qf) > 0 else 'Cuartos 1'}";
            }}
            
            subgraph cluster_finales {{
                label = "Etapa Definitoria";
                color = gold;
                "Semifinal: {top_sf[0] if len(top_sf) > 0 else 'Semi 1'}" -> "Gran Final: {top_fi[0] if len(top_fi) > 0 else 'Final'}";
                "Semifinal: {top_sf[0] if len(top_sf) > 0 else 'Semi 1'}" -> "3er Puesto: {top_3ro[0] if len(top_3ro) > 0 else '3er Lugar'}";
            }}
            
            "{top_r32[0] if len(top_r32) > 0 else 'Llave A'}" -> "{top_r16[0] if len(top_r16) > 0 else 'Octavos 1'}";
            "{top_r16[0] if len(top_r16) > 0 else 'Octavos 1'}" -> "{top_qf[0] if len(top_qf) > 0 else 'Cuartos 1'}";
            "{top_qf[0] if len(top_qf) > 0 else 'Cuartos 1'}" -> "Semifinal: {top_sf[0] if len(top_sf) > 0 else 'Semi 1'}";
        }}
        """
        st.graphviz_chart(codigo_grafica, use_container_width=True)
        
        # Despliegue de apoyo en formato texto limpio para asegurar scannability
        st.markdown("### 📋 Top Llaves más Frecuentes por Instancia")
        c_r1, c_r2, c_r3 = st.columns(3)
        with c_r1:
            st.write("**Octavos de Final Populares:**")
            for llave, cant in conteos_llaves["R16"].most_common(3):
                st.caption(f"• {llave}")
        with c_r2:
            st.write("**Cuartos de Final Populares:**")
            for llave, cant in conteos_llaves["Cuartos"].most_common(3):
                st.caption(f"• {llave}")
        with c_r3:
            st.write("**Finales y 3er Puesto de Tendencia:**")
            st.caption(f"🏆 **Final:** {top_fi[0] if len(top_fi) > 0 else 'Sin datos'}")
            st.caption(f"🥉 **3er Lugar:** {top_3ro[0] if len(top_3ro) > 0 else 'Sin datos'}")
