import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Ingeniería de Succión Clinker Pro", layout="wide")

st.title("🌪️ Diagnóstico Integral de Succión y Capacidad")
st.markdown("---")

# --- BARRA LATERAL ---
st.sidebar.header("📊 Datos de Entrada")

with st.sidebar.expander("Ficha Técnica Ventilador", expanded=True):
    cfm_nominal = st.sidebar.number_input("Caudal Nominal (CFM)", value=7600)
    sp_ventilador = st.sidebar.number_input("Presión Máxima (in H2O)", value=17.0)
    hp_motor_placa = st.sidebar.number_input("Potencia Motor (HP)", value=30.0)
    eficiencia_fan = st.sidebar.slider("Eficiencia (%)", 40, 90, 65) / 100
    altitud = st.sidebar.number_input("Altitud (msnm)", value=2500)
    v_transp_target = st.sidebar.slider("Velocidad Transporte Objetivo (m/s)", 20, 40, 25)

st.sidebar.markdown("### 🛑 Simulación de Obstrucción")
pct_obstruccion = st.sidebar.slider("% Obstrucción Principal", 0, 90, 0)

with st.sidebar.expander("Línea Principal (Hardox)"):
    diam_ppal_mm = st.number_input("Ø Ducto Principal (mm)", value=400)
    long_ppal = st.number_input("Longitud Principal (m)", value=15.0)
    n_codos_ppal = st.number_input("Codos Línea Principal", value=2)
    
    st.markdown("**Boca de Línea Principal**")
    diam_boca_ppal = st.number_input("Ø Boca Principal (mm)", value=500)
    area_c_ppal = math.pi * (diam_boca_ppal / 1000)**2 / 4

st.sidebar.markdown("### 🛠️ Configuración de Ramales")
n_ramales = st.sidebar.number_input("Número de Ramales Abiertos", min_value=1, value=2)

datos_ramales = []
for i in range(n_ramales):
    with st.sidebar.expander(f"Ramal #{i+1}", expanded=False):
        d_r = st.number_input(f"Ø Ducto Ramal {i+1} (mm)", value=150, key=f"dr_{i}")
        l_r = st.number_input(f"Longitud Ramal {i+1} (m)", value=3.0, key=f"lr_{i}")
        c_r = st.number_input(f"N° Codos R{i+1}", value=2, key=f"cr_{i}")
        a_r = st.number_input(f"Ø Boca Campana R{i+1} (mm)", value=250, key=f"dc_{i}")
        area_c = math.pi * (a_r / 1000)**2 / 4
        datos_ramales.append({"id": i+1, "diam": d_r, "long": l_r, "codos": c_r, "area_c": area_c, "boca_mm": a_r})

with st.sidebar.expander("Filtro de Mangas"):
    n_mangas_act = st.number_input("Número de Mangas Instaladas", value=120)
    diam_manga = st.number_input("Ø Manga (mm)", value=120)
    largo_manga = st.number_input("Largo Manga (mm)", value=2115)
    dp_filtro = st.number_input("DP Filtro (in H2O)", value=5.0)

# --- LÓGICA DE CÁLCULO ---
densidad_aire = 1.225 * math.exp(-altitud / 8500)

def calcular_sistema_detallado(obs_pct):
    d_m_ppal = diam_ppal_mm / 1000
    area_real_ppal = (math.pi * (d_m_ppal**2) / 4) * (1 - obs_pct / 100)
    v_ppal = (cfm_nominal * 1.699 / 3600) / max(0.01, area_real_ppal)
    le_ppal = long_ppal + (n_codos_ppal * 25 * d_m_ppal)
    p_ppal_pa = (0.022 * le_ppal / d_m_ppal) * (0.5 * densidad_aire * v_ppal**2)
    p_obs_pa = ((obs_pct/10)**2 * 0.5 * densidad_aire * v_ppal**2) if obs_pct > 0 else 0
    p_ramales_pa = 0
    for r in datos_ramales:
        d_m_r = r["diam"] / 1000
        v_r = ((cfm_nominal * 1.699 / n_ramales) / 3600) / (math.pi * d_m_r**2 / 4)
        le_r = r["long"] + (r["codos"] * 25 * d_m_r) + (20 * d_m_r)
        p_ramales_pa += (0.022 * le_r / d_m_r) * (0.5 * densidad_aire * v_r**2)
    p_total_in = ((p_ppal_pa + p_obs_pa + (p_ramales_pa / n_ramales)) / 249.08) + dp_filtro
    f_q = math.sqrt(max(0.05, sp_ventilador / p_total_in)) if p_total_in > sp_ventilador else 1.0
    return cfm_nominal * 1.699 * f_q, p_total_in, area_real_ppal

q_real_m3h, p_real_in, a_real_ppal = calcular_sistema_detallado(pct_obstruccion)
hp_req = (q_real_m3h / 1.699 * p_real_in) / (6356 * eficiencia_fan)
v_real_ppal = (q_real_m3h / 3600) / a_real_ppal
v_cap_ppal = (q_real_m3h / 3600) / area_c_ppal
q_por_ramal = q_real_m3h / n_ramales

# --- PESTAÑAS ---
tab1, tab2 = st.tabs(["📊 Diagnóstico y Gráficas", "💡 Recomendaciones Técnicas"])

with tab1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Carga Motor", f"{(hp_req/hp_motor_placa)*100:.1f}%")
    c2.metric("Caudal Real", f"{q_real_m3h:.0f} m³/h")
    c3.metric("Resistencia", f"{p_real_in:.2f} in H2O")

    st.subheader("📋 Resumen Real vs Ideal")
    mangas_nec = math.ceil(q_real_m3h / (1.0 * 60 * (math.pi * (diam_manga/1000) * (largo_manga/1000))))
    st.table(pd.DataFrame({
        "Parámetro": ["V. Transporte Ppal", "Mangas Instaladas", "Caudal Sistema", "V. Captación Ppal"],
        "Real": [f"{v_real_ppal:.2f} m/s", f"{n_mangas_act}", f"{q_real_m3h:.0f} m³/h", f"{v_cap_ppal:.2f} m/s"],
        "Ideal": [f"{v_transp_target} m/s", f"{mangas_nec}", f"{cfm_nominal*1.699:.0f} m³/h", "12.00 m/s"]
    }))

    st.subheader("🌿 Detalle Individual por Ramal")
    resumen_r = []
    for r in datos_ramales:
        v_cap_r = (q_por_ramal / 3600) / r["area_c"]
        v_tra_r = (q_por_ramal / 3600) / (math.pi * (r["diam"]/1000)**2 / 4)
        resumen_r.append({"Ramal": f"#{r['id']}", "V. Captación (m/s)": f"{v_cap_r:.2f}", "V. Transporte (m/s)": f"{v_tra_r:.2f}", "Estado": "✅ OK" if v_tra_r >= v_transp_target else "🚨 BAJA"})
    st.dataframe(pd.DataFrame(resumen_r), use_container_width=True)

    st.subheader("📈 Curva del Ventilador")
    q_plot = np.linspace(100, cfm_nominal * 1.5, 50); k = p_real_in / (q_real_m3h/1.699)**2
    fig1, ax1 = plt.subplots(figsize=(10, 3.5)); ax1.plot(q_plot, k*(q_plot**2), color="#00FFAA"); ax1.axhline(y=sp_ventilador, color='red', linestyle='--'); ax1.scatter([q_real_m3h/1.699], [p_real_in], color='yellow', s=100); st.pyplot(fig1)

with tab2:
    st.subheader("🚀 Recomendaciones de Mejora")
    
    # 1. ANÁLISIS DE LA GRÁFICA (NUEVO)
    st.markdown("### 📈 Análisis de Capacidad del Ventilador")
    reserva_presion = sp_ventilador - p_real_in
    if reserva_presion < 0:
        st.error(f"❌ **Diagnóstico Crítico:** El ventilador está saturado. La resistencia ({p_real_in:.2f} inH2O) superó la línea roja ({sp_ventilador} inH2O). El sistema NO tiene fuerza para mover el clinker.")
    elif reserva_presion < 1.5:
        st.warning(f"⚠️ **Diagnóstico Limítrofe:** El punto amarillo está tocando la línea roja. No tienes margen de maniobra; cualquier suciedad en las mangas o un pequeño tapón detendrá la succión.")
    else:
        st.success(f"✅ **Diagnóstico Saludable:** Tienes una reserva de {reserva_presion:.2f} inH2O. El ventilador es adecuado para la configuración actual.")

    st.markdown("---")
    
    # 2. VELOCIDADES Y DIMENSIONAMIENTO
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ⚙️ Motor y Ducto Principal")
        if v_real_ppal >= v_transp_target: st.success(f"✅ **Velocidad Ducto Ppal:** OK ({v_real_ppal:.2f} m/s)")
        else: st.error(f"❌ **Velocidad Ducto Ppal:** BAJA. Disminuir Ø ducto a **{math.sqrt(4*((q_real_m3h/3600)/v_transp_target)/math.pi)*1000:.0f}mm** para evitar sedimentación.")
        
        if hp_req > hp_motor_placa: st.error(f"❌ **Motor:** SOBRECARGA. Instalar motor de **{hp_req*1.15:.0f} HP** para evitar fallos eléctricos.")
        else: st.success(f"✅ **Motor:** OK (Carga al {(hp_req/hp_motor_placa)*100:.1f}%)")
        
    with col2:
        st.markdown("### 🧵 Filtro y Campanas")
        if n_mangas_act < mangas_nec: st.error(f"❌ **Filtro:** Faltan **{mangas_nec - n_mangas_act}** mangas para procesar el aire correctamente.")
        else: st.success(f"✅ **Filtro:** OK")
        
        a_id_r = (q_por_ramal / 3600) / 12
        st.info(f"📢 **Boca de Campana Ramal:** Para 12 m/s el Ø ideal es **{math.sqrt(4*a_id_r/math.pi)*1000:.0f} mm**. (Actualmente: {datos_ramales[0]['boca_mm']} mm)")

    st.markdown("---")
    # Captación Principal
    if v_cap_ppal >= 12: st.success(f"✅ **Captación Principal:** OK ({v_cap_ppal:.2f} m/s)")
    else: st.error(f"❌ **Captación Principal:** BAJA. Reducir boca de campana principal a **{math.sqrt(4*((q_real_m3h/3600)/12)/math.pi)*1000:.0f}mm** para mejorar el arrastre de clinker.")
