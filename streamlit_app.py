st.header("💸 Cálculo de Pérdida de Energía y Costo")

col1, col2 = st.columns(2)

with col1:
    area_paredes = st.number_input("Área total de paredes del horno (m²)", value=5.0)
    horas_operacion = st.number_input("Horas de operación al mes", value=160)
    precio_gas = st.number_input("Precio del m³ de Gas ($)", value=0.50)

with col2:
    # El flujo de calor (Q) se calcula con la Ley de Fourier: Q = (k * A * ΔT) / L
    diferencia_temp = 1500 - t_chapa_estimada # t_chapa_estimada viene del bloque anterior
    perdida_watts = (k_refractario * area_paredes * diferencia_temp) / espesor
    
    st.metric("Pérdida de Calor Total", f"{perdida_watts/1000:.2f} kW")

# --- Cálculos Económicos ---
energia_total_mes = (perdida_watts / 1000) * horas_operacion # kWh al mes
# 1 m3 de gas natural produce aprox 10.5 kWh
gas_perdido = energia_total_mes / 10.5
costo_perdida = gas_perdido * precio_gas

st.subheader(f"Gasto mensual por pérdida térmica: ${costo_perdida:.2f}")

st.info(f"""
💡 **Análisis de eficiencia:** 
Para mantener esta pared a 1500°C, estás 'tirando' el equivalente a **{gas_perdido:.1f} m³** 
de gas al mes a través del refractario. 
Aumentar el espesor en **5cm** podría reducir este costo significativamente.
""")
