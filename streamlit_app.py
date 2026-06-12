import streamlit as st
import random
import pandas as pd
import plotly.express as px
from collections import Counter

# 1. Configuración de la página de Streamlit
st.set_page_config(page_title="Simulador Masivo Mundial 2026", page_icon="🏆", layout="wide")

st.title("🏆 Simulador de Alta Velocidad: 50,000 Mundiales Completos")
st.markdown("### Análisis probabilístico masivo del torneo completo (Formatos de Grupos y Eliminatorias Oficiales)")

# 2. Base de datos con los 48 equipos oficiales calibrados (Ataque, Defensa, Racha, Cracks)
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
        # CAF
        "Marruecos": (2.3, 0.9, 12, 4.0), "Senegal": (2.2, 1.0, 11, 3.5), "Egipto": (2.1, 1.1, 10, 3.0), "Argelia": (2.0, 1.2, 9, 2.5),
        "Túnez": (1.6, 1.3, 8, 1.5), "Nigeria": (2.2, 1.2, 8, 3.0), "Costa de Marfil": (2.1, 1.1, 10, 3.0), "Ghana": (1.8, 1.3, 8, 2.0),
        "Sudáfrica": (1.6, 1.4, 7, 1.5), "Cabo Verde": (1.6, 1.3, 8, 1.5), "Congo": (1.3, 1.7, 6, 1.0),
        # AFC + OFC
        "Japón": (2.4, 1.0, 11, 3.5), "Corea del Sur": (2.2, 1.1, 10, 3.0), "Irán": (1.9, 1.2, 9, 2.0), "Australia": (1.8, 1.3, 9, 2.0),
        "Arabia Saudita": (1.7, 1.4, 8, 1.5), "Catar": (1.6, 1.5, 7, 1.5), "Jordania": (1.4, 1.5, 7, 1.0), "Uzbekistán": (1.5, 1.3, 8, 1.5),
        "Nueva Zelanda": (1.4, 1.7, 6, 1.0)
    }
    return ratings_48

db_mundial = cargar_base_datos_mundial()

# 3. Configuración estructural de los 12 grupos del Mundial 2026
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

# 4. Función de cálculo de potencia en tiempo real (Incluye bono estricto de localía)
def calcular_rating_dinamico(nombre_equipo):
    gf, gc, racha, factor_motivacion = db_mundial[nombre_equipo]
    base_poder = 78.0 + (gf * 6.5) - (gc * 4) + ((racha - 8) * 0.5)
    bono_localia = 4.5 if nombre_equipo in ["Estados Unidos", "México", "Canadá"] else 0.0
    bono_estrellas = factor_motivacion * 1.2
    factor_inspiracion = random.uniform(-4.0, 4.0)
    return max(50.0, base_poder + bono_localia + bono_estrellas + factor_inspiracion)

# 5. Función de simulación con escala ofensiva adaptativa para evitar el bucle del 1-0
def simular_partido_torneo(eq1, eq2, knockout=False, contador_goles=None):
    r1 = calcular_rating_dinamico(eq1)
    r2 = calcular_rating_dinamico(eq2)
    
    diff = r1 - r2
    lambda1 = max(0.9, 1.75 + (diff * 0.05))
    lambda2 = max(0.9, 1.75 - (diff * 0.05))
    
    escala_goles1 = 1.35 + (max(0.0, diff) * 0.02)
    escala_goles2 = 1.15
    
    goles1 = max(0, int(random.gammavariate(lambda1, escala_goles1)))
    goles2 = max(0, int(random.gammavariate(lambda2, escala_goles2)))
    
    if contador_goles is not None:
        contador_goles[f"{goles1} - {goles2}"] += 1
        
    ganador = None
    if goles1 > goles2:
        ganador = eq1
    elif goles2 > goles1:
        ganador = eq2
    else:
        if knockout:
            ganador = eq1 if random.random() > 0.5 else eq2
            
    return ganador

# 6. Interfaz del menú lateral de Streamlit
st.sidebar.header("⚙️ Configuración Masiva")
num_simulaciones = st.sidebar.number_input("Mundiales a Simular", min_value=1, max_value=100000, value=50000, step=5000)

# 7. Ejecución principal del Torneo al presionar el botón
if st.button("🚀 Lanzar Simulaciones Completas", type="primary", use_container_width=True):
    status_text = st.empty()
    status_text.info(f"⏳ Procesando {num_simulaciones:,} torneos completos (más de 5.2 millones de partidos)... Por favor, espera.")
    
    conteos_campeon = Counter()
    conteos_podio = {pais: {"2° Lugar": 0, "3° Lugar": 0, "4° Lugar": 0} for pais in db_mundial}
    conteo_general_goles = Counter()
    
    grupos_items = list(GRUPOS_2026.items())
    
    for n in range(1, int(num_simulaciones) + 1):
        clasificados_por_grupo = []
        mejores_terceros_pool = []
        
        # FASE DE GRUPOS
        for grupo, equipos in grupos_items:
            tabla = {eq: {"eq": eq, "pts": 0, "dg": 0, "gf": 0, "gc": 0} for eq in equipos}
            for i in range(4):
                for j in range(i + 1, 4):
                    eq1, eq2 = equipos[i], equipos[j]
                    
                    r1 = calcular_rating_dinamico(eq1)
                    r2 = calcular_rating_dinamico(eq2)
                    diff = r1 - r2
                    l1 = max(0.9, 1.75 + (diff * 0.05))
                    l2 = max(0.9, 1.75 - (diff * 0.05))
                    g1 = max(0, int(random.gammavariate(l1, 1.35 + (max(0.0, diff) * 0.02))))
                    g2 = max(0, int(random.gammavariate(l2, 1.15)))
                    
                    conteo_general_goles[f"{g1} - {g2}"] += 1
                    
                    tabla[eq1]["gf"] += g1; tabla[eq1]["gc"] += g2
                    tabla[eq2]["gf"] += g2; tabla[eq2]["gc"] += g1
                    
                    if g1 > g2: tabla[eq1]["pts"] += 3
                    elif g2 > g1: tabla[eq2]["pts"] += 3
                    else: tabla[eq1]["pts"] += 1; tabla[eq2]["pts"] += 1
            
            for eq in equipos:
                tabla[eq]["dg"] = tabla[eq]["gf"] - tabla[eq]["gc"]
                
            ordenados = sorted(tabla.values(), key=lambda x: (x["pts"], x["dg"], x["gf"]), reverse=True)
            clasificados_por_grupo.append(ordenados[0]["eq"])
            clasificados_por_grupo.append(ordenados[1]["eq"])
            
            mejores_terceros_pool.append(ordenados[2])
            
        mejores_terceros_ordenados = sorted(mejores_terceros_pool, key=lambda x: (x["pts"], x["dg"], x["gf"]), reverse=True)
        for k in range(8):
            clasificados_por_grupo.append(mejores_terceros_ordenados[k]["eq"])
            
        # LLAVES DE ELIMINACIÓN DIRECTA
        equipos_activos = clasificados_por_grupo
        for r_partidos in (16, 8, 4):
            prox = []
            for p in range(r_partidos):
                g = simular_partido_torneo(equipos_activos[p*2], equipos_activos[p*2+1], knockout=True, contador_goles=conteo_general_goles)
                prox.append(g)
            equipos_activos = prox
            
        s1_e1, s1_e2, s2_e1, s2_e2 = equipos_activos
        
        r1_s1, r2_s1 = calcular_rating_dinamico(s1_e1), calcular_rating_dinamico(s1_e2)
        sem1_g = s1_e1 if random.gammavariate(max(0.9, 1.75 + ((r1_s1 - r2_s1) * 0.05)), 1.2) > random.gammavariate(max(0.9, 1.75 - ((r1_s1 - r2_s1) * 0.05)), 1.15) else s1_e2
        sem1_p = s1_e2 if sem1_g == s1_e1 else s1_e1
        
        r1_s2, r2_s2 = calcular_rating_dinamico(s2_e1), calcular_rating_dinamico(s2_e2)
        sem2_g = s2_e1 if random.gammavariate(max(0.9, 1.75 + ((r1_s2 - r2_s2) * 0.05)), 1.2) > random.gammavariate(max(0.9, 1.75 - ((r1_s2 - r2_s2) * 0.05)), 1.15) else s2_e2
        sem2_p = s2_e2 if sem2_g == s2_e1 else s2_e1
        
        tercero = simular_partido_torneo(sem1_p, sem2_p, knockout=True, contador_goles=conteo_general_goles)
        cuarto = sem2_p if tercero == sem1_p else sem1_p
        
        campeon = simular_partido_torneo(sem1_g, sem2_g, knockout=True, contador_goles=conteo_general_goles)
        subcampeon = sem2_g if campeon == sem1_g else sem1_g
        
        conteos_campeon[campeon] += 1
        conteos_podio[subcampeon]["2° Lugar"] += 1
        conteos_podio[tercero]["3° Lugar"] += 1
        conteos_podio[cuarto]["4° Lugar"] += 1
        
        if n % 10000 == 0:
            status_text.info(f"⏳ Procesando lotes... {n:,} / {int(num_simulaciones):,} mundiales calculados.")

    status_text.empty()
    
    # --- RENDERIZADO FINAL DE RESULTADOS GRÁFICOS Y TABLAS ---
    st.divider()
    st.subheader("📊 Reporte Consolidado de Probabilidades del Campeonato")
    
    top_uno_goles = conteo_general_goles.most_common(1)
    
    total_partidos_mundiales = int(num_simulaciones) * 104
    
    # Separación por corchetes limpia e idéntica a la anterior
    marcador_texto = top_uno_goles[0][0]
    cantidad_veces = top_uno_goles[0][1]
    
    porcentaje_marcador_global = (cantidad_veces / total_partidos_mundiales) * 100

    st.success(f"🎯 El marcador más repetido a nivel global en todo el torneo es **{marcador_texto}** (Ocurrió el {porcentaje_marcador_global:.2f}% de las veces en {cantidad_veces:,} partidos).")

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🥧 Probabilidad del Campeón del Mundo (Top 10)")
        top_campeones = conteos_campeon.most_common(10)
        total_top = sum([c for _, c in top_campeones])
        grid_otros = int(num_simulaciones) - total_top
        
        datos_campeon = {"Selección": [p for p, _ in top_campeones], "Títulos": [c for _, c in top_campeones]}
        if grid_otros > 0:
            datos_campeon["Selección"].append("Otros")
            datos_campeon["Títulos"].append(grid_otros)
            
        df_fig = pd.DataFrame(datos_campeon)
        
        fig = px.pie(df_fig, values="Títulos", names="Selección", hole=0.4, color_discrete_sequence=px.colors.sequential.YlOrRd)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 📋 Tabla de Podios Totales Organizada")
        podios_completos = {}
        for pais, titulos in conteos_campeon.items():
            podios_completos[pais] = {
                "1° Lugar (Títulos)": titulos,
                "Porcentaje Ganador": f"{(titulos / int(num_simulaciones) * 100):.2f}%",
                "2° Lugar": conteos_podio[pais]["2° Lugar"],
                "3° Lugar": conteos_podio[pais]["3° Lugar"],
                "4° Lugar": conteos_podio[pais]["4° Lugar"]
            }
            
        df_podios = pd.DataFrame.from_dict(podios_completos, orient="index")
        df_podios = df_podios.sort_values(by="1° Lugar (Títulos)", ascending=False)
        st.dataframe(df_podios, use_container_width=True)
        
    st.balloons()
