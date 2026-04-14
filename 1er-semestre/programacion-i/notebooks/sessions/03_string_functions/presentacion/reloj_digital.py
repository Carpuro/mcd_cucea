import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from matplotlib.animation import FuncAnimation

# VARIABLES
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_aspect('equal')
ax.axis('off')

# FONDO
try:
    img = plt.imread("images\MCD.jpg")
    ax.imshow(img, extent=[-1.2, 1.2, -1.2, 1.2], alpha=0.25) 
except FileNotFoundError:
    print("⚠️ No hay imagen.")

# TITULO
plt.title("Te amooo\n"
          "Programación 1 - Reloj Digital",
          fontsize=14, fontweight="bold", pad=20, color="black")

# MARCO
outer_circle = plt.Circle((0, 0), 1, fill=False, linewidth=4, color="black")
ax.add_artist(outer_circle)

# MARCAS
for i in range(60):
    angle = np.deg2rad(i * 6)
    x1, y1 = np.cos(angle), np.sin(angle)
    if i % 5 == 0:
        ax.plot([0.85*x1, x1], [0.85*y1, y1], color="black", linewidth=2)
    else:
        ax.plot([0.9*x1, x1], [0.9*y1, y1], color="gray", linewidth=1)

# HORAS
for i in range(1, 13):
    angle = np.deg2rad(90 - i*30)
    x, y = 0.75 * np.cos(angle), 0.75 * np.sin(angle)
    ax.text(x, y, str(i), ha='center', va='center', fontsize=16, fontweight="bold")

# AGUJAS
line_hour, = ax.plot([], [], linewidth=6, color="black", label="Horas")
line_min,  = ax.plot([], [], linewidth=4, color="blue", label="Minutos")
line_sec,  = ax.plot([], [], linewidth=2, color="red", label="Segundos")

# LEYENDA
ax.legend(loc="upper right", fontsize=8, frameon=True)

# UPDATE
def update(frame):
    now = datetime.now()
    h, m, s = now.hour % 12, now.minute, now.second
    

    angle_h = np.deg2rad(90 - (h*30 + m*0.5))  # HORA
    angle_m = np.deg2rad(90 - (m*6))           # MINUTOS
    angle_s = np.deg2rad(90 - (s*6))           # SEGUNDOS
    

    line_hour.set_data([0, 0.5*np.cos(angle_h)], [0, 0.5*np.sin(angle_h)])
    line_min.set_data([0, 0.7*np.cos(angle_m)], [0, 0.7*np.sin(angle_m)])
    line_sec.set_data([0, 0.9*np.cos(angle_s)], [0, 0.9*np.sin(angle_s)])
    
    return line_hour, line_min, line_sec

# CALL ANIMACION
ani = FuncAnimation(fig, update, interval=1000)
plt.show()

