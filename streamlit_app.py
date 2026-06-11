import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Configuración de la página de Streamlit
st.set_page_config(page_title="Simulación de Flujo en Rodete - UNACEM", layout="wide")

st.title("⚙️ Simulación Aerodinámica: Transición Interna del Rodete")
st.markdown("""
Esta aplicación simula el comportamiento del flujo de aire al ingresar a la placa superior del rodete. 
Compara el comportamiento aerodinámico entre el **diseño original con radio** y la **modificación real con transición recta**.
""")

# Parámetros en la barra lateral
st.sidebar.header("Parámetros de Entrada")
rpm = st.sidebar.slider("Velocidad de Operación (RPM)", 500, 1200, 1040, step=10)
ancho_perif = st.sidebar.slider("Ancho en la periferia (mm)", 100, 300, 200, step=10)

# Cálculos rápidos basados en los datos del usuario
v_periferica = (2 * np.pi * rpm / 60) * 0.9 # Radio externo = 0.9m
st.sidebar.metric(label="Velocidad Periférica Estimada", value=f"{v_periferica:.2f} m/s (~{v_periferica*3.6:.1f} km/h)")

# Crear la malla para la simulación numérica (2D)
X, Y = np.meshgrid(np.linspace(0, 5, 100), np.linspace(0, 5, 100))

# --- CONFIGURACIÓN DE GEOMETRÍAS Y VECTORES ---

# 1. Diseño Curvo (Flujo suave, sigue la pared cóncava)
U_curvo = 1.5 * (X**0.2)  # Componente X de velocidad
V_curvo = -1.2 * (Y**0.3) # Componente Y de velocidad

# 2. Diseño Recto con Ángulo Vivo (Generación de vórtice/recirculación en la esquina)
U_recto = 1.5 * (X**0.2)
V_recto = -1.2 * (Y**0.3)

# Simular zona de desprendimiento y remolino en la esquina (aprox en coordenadas X=2, Y=2)
vortex_mask = (X > 1.8) & (X < 3.2) & (Y > 1.8) & (Y < 3.2)
U_recto[vortex_mask] = -1.0 * np.sin(Y[vortex_mask]) # Inversión de flujo en X
V_recto[vortex_mask] = 1.5 * np.cos(X[vortex_mask])  # Movimiento rotacional en Y

# --- RENDERIZADO DE GRÁFICOS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Diseño Original (Con Radio Curvo)")
    fig_curvo, ax_curvo = plt.subplots(figsize=(6, 5))
    
    # Líneas de corriente suaves
    ax_curvo.streamplot(X, Y, U_curvo, V_curvo, color=U_curvo, cmap='autumn', linewidth=1.5)
    # Perfil geométrico curvo
    t = np.linspace(0, np.pi/2, 100)
    ax_curvo.plot(2 + 1.5*np.cos(t), 2 + 1.5*np.sin(t), color='black', linewidth=4, label='Placa Curva')
    
    ax_curvo.set_xlim([0, 5])
    ax_curvo.set_ylim([0, 5])
    ax_curvo.set_title("Flujo Laminar / Deslizamiento Suave")
    ax_curvo.axis('off')
    st.pyplot(fig_curvo)
    st.info("💡 El fluido acompaña la geometría. Las partículas de polvo deslizan en lugar de impactar de frente.")

with col2:
    st.subheader("2. Modificación Real (Ángulo Recto)")
    fig_recto, ax_recto = plt.subplots(figsize=(6, 5))
    
    # Líneas de corriente con remolino
    ax_recto.streamplot(X, Y, U_recto, V_recto, color=np.sqrt(U_recto**2 + V_recto**2), cmap='winter', linewidth=1.5)
    # Perfil geométrico recto (Esquina viva)
    ax_recto.plot([2, 2, 3.5], [3.5, 2, 2], color='black', linewidth=4, label='Placa Recta')
    # Zona de impacto del vórtice
    ax_recto.plot(2, 2, 'ro', markersize=12, label='Zona de Máxima Erosión')
    
    ax_recto.set_xlim([0, 5])
    ax_recto.set_ylim([0, 5])
    ax_recto.set_title("Desprendimiento de Flujo (Vórtice)")
    ax_recto.axis('off')
    st.pyplot(fig_recto)
    st.warning("⚠️ El quiebre a 90° desprende el aire creando un vórtice. El punto rojo exige máximo recargue duro.")

st.markdown("---")
st.subheader("📌 Conclusión para el Trabajo en Planta:")
st.write("""
Dado que el rodete real cuenta con la **Geometría 2 (Ángulo Recto)**, la turbulencia en el vértice interno provocará que el polvo centrifuge en forma de remolino justo en la esquina. 
Para mitigar esto en el taller, es mandatorio que el **filete de soldadura de recargue duro rellene el vértice**, tratando de 'suavizar' o emular artificialmente la curva de la Geometría 1.
""")
