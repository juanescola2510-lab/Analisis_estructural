
# COMPLETAR EN LA BARRA LATERAL (AGREGAR ESTO DEBAJO DE LA CONDICIÓN DE LA BOTA)
# ==============================================================================
st.sidebar.header("⏱️ Parámetros Operativos del Tiempo")
rpm_sprocket = st.sidebar.number_input("Velocidad del Sprocket (RPM)", value=45.0, min_value=1.0)


# ==============================================================================
# --- REEMPLAZAR EL BLOQUE 2 COMPLETO POR ESTA VERSIÓN CON VIDA ÚTIL ---
# ==============================================================================
st.markdown("---")
st.write(f"### Análisis de Fatiga y Estimación de Vida Útil (Factor $K_t$ = {kt})")
col_graf, col_tab = st.columns(2)

# Corrección analítica rigurosa del límite de fatiga a cortante
sse_corregido = su_mpa * 0.5 * 0.577  # ~0.288 * Su

# --- CÁLCULO DE VIDA ÚTIL Y CICLOS (TEORÍA S-N) ---
# Esfuerzo invertido equivalente usando el criterio de Goodman modificado
# S_eq es el esfuerzo puramente alternante que causaría el mismo daño que la combinación actual
if tau_m < ssu:
    tau_eq = tau_a / (1 - (tau_m / ssu))
else:
    tau_eq = tau_a + tau_m  # Condición extrema fuera de rango seguro

# Propiedades de la curva S-N para aceros en cortante
sf_103 = 0.9 * ssu  # Resistencia estimada a 10^3 ciclos
f_limite = sse_corregido

if tau_eq <= f_limite:
    ciclos_estimados = float('inf')
    vida_horas = float('inf')
    txt_vida = "♾️ Vida Infinita (Fatiga Controlada)"
    txt_horas = "Sin límite teórico bajo estas cargas"
elif tau_eq >= sf_103:
    ciclos_estimados = 1000.0
    vida_horas = ciclos_estimados / (rpm_sprocket * 60)
    txt_vida = "⚠️ Falla Próxima o Fatiga de Bajo Ciclaje"
    txt_horas = f"{vida_horas:.2f} horas de operación continua"
else:
    # Ecuaciones constituyentes de la curva S-N: log(S) = b*log(N) + log(a)
    b_param = (1/3) * np.log10(f_limite / sf_103)
    a_param = (sf_103**2) / f_limite
    
    # Despeje de ciclos de vida aproximados: N = (tau_eq / a)^(1/b)
    ciclos_estimados = (tau_eq / a_param)**(1 / b_param)
    vida_horas = ciclos_estimados / (rpm_sprocket * 60)
    txt_vida = f"{ciclos_estimados:,.0f} ciclos"
    txt_horas = f"{vida_horas:,.1f} horas operativas ({vida_horas/24:,.1f} días aprox.)"

# --- RENDERIZADO DEL GRÁFICO ---
with col_graf:
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    tm_range = np.linspace(0, ssu, 100)
    
    ax3.plot([0, ssy], [sse_corregido, 0], 'green', label='SODERBERG', lw=2)
    ax3.plot([0, ssu], [sse_corregido, 0], 'blue', ls='--', label='GOODMAN', lw=2)
    ax3.plot(tm_range, sse_corregido*(1-(tm_range/ssu)**2), 'orange', label='GERBER', lw=2)
    
    ax3.scatter(tau_nominal, tau_nominal * 0.25, color='gray', s=120, alpha=0.6, label='Punto Nominal (Ideal)')
    ax3.scatter(tau_m, tau_a, color='red', s=200, edgecolor='black', zorder=10, label='Punto Crítico Local (Con Kt)')
    
    ax3.set_xlabel("τ_medio (MPa)")
    ax3.set_ylabel("τ_alternante (MPa)")
    ax3.set_xlim(0, ssu * 1.05)
    ax3.set_ylim(0, sse_corregido * 1.2)
    ax3.legend(loc='upper right')
    ax3.grid(True, alpha=0.3)
    st.pyplot(fig3)

# --- RENDERIZADO DE MÉTRICAS Y TABLAS ---
with col_tab:
    fs_sod = 1 / ((tau_a / sse_corregido) + (tau_m / ssy))
    fs_goo = 1 / ((tau_a / sse_corregido) + (tau_m / ssu))
    fs_ger = 1 / ((tau_a / sse_corregido) + (tau_m / ssu)**2)
    
    st.write("**Métricas de Esfuerzo en el Pin:**")
    st.info(f"🔹 **τ Nominal:** {tau_nominal:.2f} MPa")
    st.error(f"🔺 **τ Local (Pico en Muesca):** {tau_m:.2f} MPa")
    
    fs_min = 1.2
    data_tabla = {
        "Criterio": ["Soderberg", "Goodman", "Gerber"],
        "Factor de Seguridad": [f"{fs_sod:.2f}", f"{fs_goo:.2f}", f"{fs_ger:.2f}"],
        "Condición Estructural": [
            "🟢 SEGURO" if fs_sod >= fs_min else "🔴 FALLA POR FATIGA",
            "🟢 SEGURO" if fs_goo >= fs_min else "🔴 FALLA POR FATIGA",
            "🟢 SEGURO" if fs_ger >= fs_min else "🔴 FALLA POR FATIGA"
        ]
    }
    st.table(data_tabla)
    
    # Nueva Sección de Diagnóstico de Vida Útil
    st.write("**⌛ Estimación de Durabilidad de la Pieza:**")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.metric(label="Ciclos hasta el inicio de falla", value=f"{ciclos_estimados:,.0f}" if ciclos_estimados != float('inf') else "Infinitos")
    with col_c2:
        st.metric(label="Tiempo estimado de servicio", value=f"{vida_horas:,.1f} h" if vida_horas != float('inf') else "Infinito")
        
    if ciclos_estimados != float('inf'):
        st.warning(f"📉 **Pronóstico:** Basado en la curva S-N, el pin acumulará daño por fatiga y alcanzará su vida útil en aproximadamente **{txt_horas}**.")
    else:
        st.success("✨ **Pronóstico:** Las cargas mecánicas se encuentran por debajo del límite de fatiga corregido. No se prevé inicio de grietas bajo condiciones normales.")
