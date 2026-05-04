import numpy as np
import matplotlib.pyplot as plt

def calcular_y_analizar(capacidad_tph, velocidad_ms, altura_m, peso_cadena_lb, peso_cangilones_lb, diametro_pin_mm, resistencia_mpa):
    # 1. Cálculo del Peso del Material (Wm) basado en la capacidad
    # tph a kg/s: (ton/h * 1000) / 3600
    flujo_kgs = (capacidad_tph * 1000) / 3600
    carga_lineal_kgm = flujo_kgs / velocidad_ms
    peso_material_kg = carga_lineal_kgm * altura_m
    peso_material_lb = peso_material_kg * 2.20462
    
    # 2. Cálculo de Fuerzas Totales
    lb_to_n = 4.44822
    peso_total_lb = peso_cadena_lb + peso_cangilones_lb + peso_material_lb
    fuerza_total_n = peso_total_lb * lb_to_n
    
    # 3. Análisis de Esfuerzos en el Pin (Doble Cortadura)
    area_simple_mm2 = np.pi * (diametro_pin_mm / 2)**2
    area_doble_mm2 = 2 * area_simple_mm2
    esfuerzo_corte_mpa = fuerza_total_n / area_doble_mm2
    
    # Resistencia al corte (Von Mises 57.7%)
    res_corte_material = resistencia_mpa * 0.577
    factor_seguridad = res_corte_material / esfuerzo_corte_mpa

    # --- VISUALIZACIÓN ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Gráfico 1: DCL del Sprocket y Cargas
    ax1.set_title(f"DCL Elevador: {capacidad_tph} TPH", fontweight='bold')
    # Dibujo sprocket
    sprocket = plt.Circle((0.5, 0.8), 0.15, color='darkgray', label='Sprocket Motriz')
    ax1.add_patch(sprocket)
    # Líneas de cadena
    ax1.plot([0.35, 0.35], [0.1, 0.8], 'k--', lw=2) # Rama bajando
    ax1.plot([0.65, 0.65], [0.1, 0.8], 'k-', lw=3, color='red') # Rama subiendo (Cargada)
    
    # Etiquetas de pesos
    info_pesos = (f"Peso Material: {peso_material_lb:.0f} lb\n"
                  f"Peso Cangilones: {peso_cangilones_lb} lb\n"
                  f"Peso Cadena: {peso_cadena_lb} lb\n"
                  f"TENSIÓN TOTAL: {peso_total_lb:.0f} lb")
    ax1.text(0.7, 0.4, info_pesos, bbox=dict(facecolor='wheat', alpha=0.5))
    ax1.axis('off')

    # Gráfico 2: Diagrama de Corte en el Pin
    ax2.set_title(f"Análisis de Corte Pin Ø{diametro_pin_mm}mm", fontweight='bold')
    ax2.add_patch(plt.Rectangle((0.2, 0.4), 0.6, 0.2, color='silver', ec='black'))
    # Vectores de fuerza
    ax2.annotate('', xy=(0.5, 0.4), xytext=(0.5, 0.1), arrowprops=dict(facecolor='red', shrink=0.05))
    ax2.text(0.52, 0.15, f"T_max: {fuerza_total_n/1000:.1f} kN", color='red')
    
    # Resultados finales
    res_final = (f"Esfuerzo Real: {esfuerzo_corte_mpa:.2f} MPa\n"
                 f"Resistencia Material: {res_corte_material:.2f} MPa\n"
                 f"FACTOR SEGURIDAD: {factor_seguridad:.2f}")
    color_fs = 'green' if factor_seguridad > 8 else 'orange' if factor_seguridad > 5 else 'red'
    ax2.text(0.5, 0.8, res_final, ha='center', fontsize=12, bbox=dict(facecolor=color_fs, alpha=0.3))
    ax2.axis('off')

    plt.tight_layout()
    plt.show()

# --- CAMBIA ESTOS VALORES PARA SIMULAR ---
calcular_y_analizar(
    capacidad_tph = 150,      # Toneladas por hora
    velocidad_ms = 1.2,       # Velocidad (m/s)
    altura_m = 33.5,          # Altura (m)
    peso_cadena_lb = 2400,    # Peso total cadena
    peso_cangilones_lb = 11820, # Peso total cangilones
    diametro_pin_mm = 34.74,  # Diámetro del pasador
    resistencia_mpa = 980     # Resistencia acero (35CrMo)
)
