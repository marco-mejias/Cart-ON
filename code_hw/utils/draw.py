import matplotlib.pyplot as plt
from classes.map import *

def visualize_map(mapa):
    grid = mapa.grid

    # Convertir valors a colors
    # -1 → gris, 0 → blanc, 1 → negre
    display = np.zeros((MAP_SIZE, MAP_SIZE, 3), dtype=np.float32)

    display[grid == -1] = [0.5, 0.5, 0.5]   # gris
    display[grid == 0]  = [1.0, 1.0, 1.0]   # blanc
    display[grid == 1]  = [0.0, 0.0, 0.0]   # negre

    plt.clf()
    plt.imshow(display, origin='lower')
    plt.title("Mapa d'ocupació en temps real")
    plt.pause(0.001)


def print_grid_section(mapa, cx, cy, size=15):
    x1 = max(0, cx - size)
    x2 = min(MAP_SIZE, cx + size)
    y1 = max(0, cy - size)
    y2 = min(MAP_SIZE, cy + size)

    print("Girem!!")
    print(mapa.grid[y1:y2, x1:x2])

