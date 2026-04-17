import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.title("🎥 Simulador de Trayectoria de Bolas")
st.write("Visualiza el rastro de las bolas para optimizar el punto de impacto.")

# --- PARÁMETROS ---
rpm = st.slider("Velocidad (RPM)", 5, 35, 18)
r_molino = 2.0  # metros
g = 9.81

# --- CÁLCULO DE FÍSICA (PUNTO DE DESPRENDIMIENTO) ---
w = (rpm * 2 * np.pi) / 60
v_critica = np.sqrt(g / r_molino)
ratio = w / v_critica

# Lógica de la trayectoria parabólica
def calcular_trayectoria(t_array, angulo_inicio):
    # Punto de desprendimiento (simplificado para visualización)
    x0 = r_molino * np.cos(angulo_inicio)
    y0 = r_molino * np.sin(angulo_inicio)
    vx = -w * r_molino * np.sin(angulo_inicio)
    vy = w * r_molino * np.cos(angulo_inicio)
    
    x = x0 + vx * t_array
    y = y0 + vy * t_array - 0.5 * g * t_array**2
    return x, y

# --- GENERAR RASTROS ---
fig = go.Figure()

# 1. Dibujar Carcasa del Molino
t_circ = np.linspace(0, 2*np.pi, 100)
fig.add_trace(go.Scatter(x=r_molino*np.cos(t_circ), y=r_molino*np.sin(t_circ), 
                         mode='lines', line=dict(color='black', width=3), name="Carcasa"))

# 2. Dibujar Trayectorias (Rastros)
tiempos = np.linspace(0, 0.8, 20) # Duración del rastro
angulos_lanzamiento = [np.pi/4, np.pi/3, np.pi/6] # Diferentes capas de bolas

for i, ang in enumerate(angulos_lanzamiento):
    tx, ty = calcular_trayectoria(tiempos, ang)
    # Dibujar la línea del rastro (trayectoria)
    fig.add_trace(go.Scatter(x=tx, y=ty, mode='lines', 
                             line=dict(width=i+1, dash='dot'), 
                             name=f"Capa {i+1}"))
    # Dibujar la bola al final del rastro
    fig.add_trace(go.Scatter(x=[tx[-1]], y=[ty[-1]], mode='markers', 
                             marker=dict(size=12, symbol='circle'), 
                             showlegend=False))

fig.update_layout(width=600, height=600, template="plotly_white",
                  xaxis=dict(range=[-2.5, 2.5], showgrid=False),
                  yaxis=dict(range=[-2.5, 2.5], showgrid=False))

st.plotly_chart(fig)

# --- ANALISIS MECÁNICO ---
if ratio > 0.75:
    st.error("⚠️ IMPACTO DIRECTO AL BLINDAJE: El rastro muestra que las bolas caen muy alto.")
elif ratio < 0.60:
    st.warning("📉 EFECTO CASCADA: El rastro es muy corto, molienda por fricción.")
else:
    st.success("🎯 IMPACTO ÓPTIMO: Las bolas caen sobre el material en el pie de la carga.")
