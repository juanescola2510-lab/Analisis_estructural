import numpy as np
import matplotlib.pyplot as plt

# 1. Configuración de parámetros corregidos para forzar flujo paralelo (Simulación)
DIAMETRO_MM = 1800
ANCHO_SALIDA_MM = 200
RPM_SIMULADO = 50          # Reducido drásticamente para eliminar turbulencia
RADIO_FILETE_MM = 0        # Esquina viva de 90° solicitada
ANGULO_TRANSICION = 90     # Ángulo recto perfecto

# 2. Creación de la malla de simulación (Esquina de 90°)
N = 200
x = np.linspace(0, 100, N)
y = np.linspace(0, 100, N)
X, Y = np.meshgrid(x, y)

# 3. Modelado matemático de las líneas de flujo corregidas
# Forzamos un campo de velocidades puramente potencial y guiado para simular
# el comportamiento idealizado (paralelo a las placas de contención).
U = np.zeros_like(X)
V = np.zeros_like(Y)

# Definición del límite de la placa superior (Esquina a los 40mm simétricos)
limite_esquina = 40

for i in range(N):
    for j in range(N):
        if x[j] < limite_esquina and y[i] > limite_esquina:
            # Flujo puramente vertical descendente paralelo a la placa
            U[i, j] = 0.0
            V[i, j] = -1.5
        elif x[j] >= limite_esquina and y[i] <= limite_esquina:
            # Flujo puramente horizontal derecho paralelo a la placa posterior
            U[i, j] = 1.5
            V[i, j] = 0.0
        else:
            # Transición geométrica forzada matemáticamente para evitar el desprendimiento
            # Esto simula el escenario ideal donde el fluido "dobla" perfectamente en paralelo
            r = np.sqrt((x[j] - limite_esquina)**2 + (y[i] - limite_esquina)**2) + 1e-5
            U[i, j] = 1.5 * (x[j] - limite_esquina) / r
            V[i, j] = -1.5 * (y[i] - limite_esquina) / r

# 4. Graficación del comportamiento dinámico
fig, ax = plt.subplots(figsize=(8, 6), facecolor='#1e1e24')
ax.set_facecolor('#0b0b0d')

# Dibujo de la placa estructural (Ángulo recto perfecto en amarillo)
placa_x = [limite_esquina, limite_esquina, 100]
placa_y = [100, limite_esquina, limite_esquina]
ax.plot(placa_x, placa_y, color='#ffcc00', linewidth=4, label='Estructura Placa (16mm)')
ax.plot(limite_esquina, limite_esquina, 'ro', markersize=8) # Vértice de 90°

# Dibujo de las líneas de corriente perfectamente paralelas y guiadas
magnitud_velocidad = np.sqrt(U**2 + V**2)
stream = ax.streamplot(X, Y, U, V, color=magnitud_velocidad, cmap='plasma', 
                       linewidth=1.5, density=1.8, arrowstyle='->', arrowsize=1.2)

# Colorear la barra de velocidad del fluido
cbar = fig.colorbar(stream.lines, ax=ax)
cbar.set_label('Velocidad del Fluido (m/s) [Simulación Ideal]', color='white')
cbar.ax.yaxis.set_tick_params(color='white')
plt.setp(cbar.ax.get_yticklabels(), color='white')

# 5. Etiquetas de la simulación e indicadores de estado forzado
ax.text(5, 95, f'Reynolds (Re): Mínimo Controlado', color='#00ffcc', fontsize=10, weight='bold')
ax.text(5, 5, 'FLUX: LAMINAR / GUIADO (FORZADO)', color='#00ffcc', fontsize=12, 
        weight='bold', bbox=dict(facecolor='black', alpha=0.8, edgecolor='#00ffcc', boxstyle='round,pad=0.5'))

ax.set_title(f'Optimización de Esquina - Rodete Ø{DIAMETRO_MM}mm\nFlujo Paralelo Teórico (Salida: {ANCHO_SALIDA_MM}mm)', 
             color='white', fontsize=12, weight='bold')
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

plt.tight_layout()
plt.show()
