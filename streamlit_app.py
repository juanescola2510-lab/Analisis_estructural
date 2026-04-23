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
    long_ppal = st.number_input("Longitud Principal (m)", value=50.0)
    n_codos_ppal = st.number_input("Codos Línea Principal", value=5)
    
    st.markdown("**Boca de Línea Principal**")
    diam_boca_ppal = st.number_input("Ø Boca Principal (mm)", value=500)
    area_c_ppal = math.pi * (diam_boca_ppal / 1000)**2 / 4

st.sidebar.markdown("### 🛠️ Configuración de Ramales")
n_ramales = st.sidebar.number_input("Número de Ramales Abiertos", min_value=0, value=2)

datos_ramales = []
if n_ramales > 0:
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

# --- LÓGICA DE CÁLCULO DE EQUILIBRIO REAL ---
densidad_aire = 1.225 * math.exp(-altitud / 8500)

def calcular_sistema_detallado(obs_pct):
    d_m_ppal = diam_ppal_mm / 1000
    area_nominal_ppal = math.pi * (d_m_ppal**2) / 4
    area_real_ppal = area_nominal_ppal * (1 - obs_pct / 100)
    
    # 1. K Línea Principal (Fricción + Codos + Obstrucción)
    le_ppal = long_ppal + (n_codos_ppal * 25 * d_m_ppal)
    k_ppal_pa = (0.022 * le_ppal / d_m_ppal) * (0.5 * densidad_aire) / (max(0.001, area_real_ppal)**2)
    k_obs_pa = ((obs_pct/10)**2 * 0.5 * densidad_aire) / (max(0.001, area_real_ppal)**2) if obs_pct > 0 else 0
    
    # 2. K Ramales (Paralelo)
    k_ramales_pa_equiv = 0
    if n_ramales > 0:
        sum_inv_sqrt_k = 0
        for r in datos_ramales:
            d_m_r = r["diam"] / 1000
            area_r = math.pi * (d_m_r**2) / 4
            le_r = r["long"] + (r["codos"] * 25 * d_m_r) + (20 * d_m_r)
            k_r = (0.022 * le_r / d_m_r) * (0.5 * densidad_aire) / (area_r**2)
            sum_inv_sqrt_k += 1 / math.sqrt(max(0.001, k_r))
        k_ramales_pa_equiv = 1 / (sum_inv_sqrt_k**2)
    
    # K Total en Pa / (m3/s)^2
    k_sistema_pa = k_ppal_pa + k_obs_pa + k_ramales_pa_equiv
    # Convertir a inH2O / (m3/h)^2
    k_final_inH2O = (k_sistema_pa / (3600**2)) / 249.08
    
    # Balance de Caudal: Q = sqrt( SP_disp / K )
    sp_disponible = sp_ventilador - dp_filtro
    if sp_disponible <= 0:
        q_real_m3h = 100 # Flujo casi nulo
    else:
        q_calc = math.sqrt(sp_disponible / k_final_inH2O)
        q_real_m3h = min(cfm_nominal * 1.699, q_calc)
        
    p_total_in = k_final_inH2O * (q_real_m3h**2) + dp_filtro
    return q_real_m3h, p_total_in, area_real_ppal

q_real_m3h, p_real_in, a_real_ppal = calcular_sistema_detallado(pct_obstruccion)
hp_req = (q_real_m3h / 1.699 * p_real_in) / (6356 * eficiencia_fan)
v_real_ppal = (q_real_m3h / 3600) / a_real_ppal
v_cap_ppal = (q_real_m3h / 3600) / area_c_ppal

# --- PESTAÑAS ---
tab1, tab2 = st.tabs(["📊 Diagnóstico y Gráficas", "💡 Recomendaciones Técnicas"])

with tab1:
    # Análisis Aire/Tela
    area_filtrado_u = math.pi * (diam_manga / 1000) * (largo_manga / 1000)
    area_total_filtrado = n_mangas_act * area_filtrado_u
    rel_aire_tela = (q_real_m3h / 60) / area_total_filtrado if area_total_filtrado > 0 else 0
    mangas_nec = math.ceil((q_real_m3h / 60) / (1.1 * area_filtrado_u))

    c1, c2, c3 = st.columns(3)
    c1.metric("Relación Aire/Tela", f"{rel_aire_tela:.2f} m/min")
    c2.metric("Caudal Real", f"{q_real_m3h:.0f} m³/h")
    c3.metric("Resistencia", f"{p_real_in:.2f} in H2O")

    st.subheader("📋 Resumen Real vs Ideal")
    st.table(pd.DataFrame({
        "Parámetro": ["V. Transporte Ppal", "Relación Aire/Tela", "Caudal Sistema", "V. Captación Ppal"],
        "Real": [f"{v_real_ppal:.2f} m/s", f"{rel_aire_tela:.2f} m/min", f"{q_real_m3h:.0f} m³/h", f"{v_cap_ppal:.2f} m/s"],
        "Ideal (Meta 1.1)": [f"{v_transp_target} m/s", "1.10 m/min", f"{cfm_nominal*1.699:.0f} m³/h", "12.00 m/s"]
    }))

    if n_ramales > 0:
        st.subheader("🌿 Detalle Individual por Ramal")
        resumen_r = []
        q_por_ramal = q_real_m3h / n_ramales
        for r in datos_ramales:
            v_cap_r = (q_por_ramal / 3600) / r["area_c"]
            v_tra_r = (q_por_ramal / 3600) / (math.pi * (r["diam"]/1000)**2 / 4)
            resumen_r.append({"Ramal": f"#{r['id']}", "V. Captación (m/s)": f"{v_cap_r:.2f}", "V. Transporte (m/s)": f"{v_tra_r:.2f}", "Estado": "✅ OK" if v_tra_r >= v_transp_target else "🚨 BAJA"})
        st.dataframe(pd.DataFrame(resumen_r), use_container_width=True)

    st.subheader("📈 Curva del Ventilador")
    q_plot = np.linspace(10, cfm_nominal * 1.5, 50)
    k_plot = p_real_in / (max(1, q_real_m3h/1.699))**2
    fig1, ax1 = plt.subplots(figsize=(10, 3.5))
    ax1.plot(q_plot, k_plot*(q_plot**2), color="#00FFAA", label="Curva Sistema")
    ax1.axhline(y=sp_ventilador, color='red', linestyle='--', label="SP Ventilador")
    ax1.scatter([q_real_m3h/1.699], [p_real_in], color='yellow', s=100, zorder=5)
    ax1.set_ylim(0, max(sp_ventilador, p_real_in) * 1.2)
    ax1.legend(); st.pyplot(fig1)

with tab2:
    st.subheader("🚀 Recomendaciones Técnicas")
    reserva_presion = sp_ventilador - p_real_in
    
    # Análisis Capacidad
    if reserva_presion < 0: st.error("❌ **Saturación:** Ventilador superado por la resistencia.")
    elif reserva_presion < 1.5: st.warning("⚠️ **Alerta:** Sin margen de seguridad.")
    else: st.success(f"✅ **Capacidad:** Reserva de {reserva_presion:.2f} inH2O.")

    # Protocolo Mantenimiento
    st.markdown("### ⚠️ Alertas Críticas")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        if reserva_presion < 2.0: st.error("🚫 **PROHIBIDO:** No añadir más ramales o codos.")
        if pct_obstruccion > 10: st.warning(f"🔍 **Obstrucción:** Limpiar ducto principal ({pct_obstruccion}%).")
    with col_m2:
        if dp_filtro > 6.0: st.error("🧵 **Mangas:** Limpieza urgente necesaria.")
        else: st.success("✅ **Mangas:** Limpieza OK.")

    # Dimensionamiento
    st.markdown("---")
    col_rec1, col_rec2 = st.columns(2)
    with col_rec1:
        st.markdown("### ⚙️ Motor y Ductos")
        if v_real_ppal >= v_transp_target: st.success("✅ **V. Ppal: OK**")
        else: st.error(f"❌ **V. Ppal: BAJA**. Reducir Ø a {math.sqrt(4*((q_real_m3h/3600)/v_transp_target)/math.pi)*1000:.0f}mm.")
        if hp_req > hp_motor_placa: st.error(f"❌ **Motor: SOBRECARGA ({hp_req:.1f} HP)**.")
        else: st.success(f"✅ **Motor: OK** ({ (hp_req/hp_motor_placa)*100 :.1f}%)")
    with col_rec2:
        st.markdown("### 🧵 Filtrado y Campanas")
        if rel_aire_tela > 1.1: st.error(f"❌ **Filtro:** Saturado. Instalar **{mangas_nec}** mangas.")
        else: st.success("✅ **Filtro: OK**")
        if v_cap_ppal < 12: st.error(f"❌ **Boca Ppal:** Reducir a {math.sqrt(4*((q_real_m3h/3600)/12)/math.pi)*1000:.0f}mm.")
