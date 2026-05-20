import numpy as np

MAP_RES = 0.5 #resolució (disminuir per a més precisió)
MAP_SIZE = 500

class Map:   
    def __init__(self):
        self.grid = np.full((MAP_SIZE, MAP_SIZE), -1, dtype=np.int8)
        
    def world_to_map(self, x, y):
        ix = int(x / MAP_RES + MAP_SIZE/2)
        iy = int(y / MAP_RES + MAP_SIZE/2)
        return ix, iy

    def map_to_world(self, ix, iy):
        x = (ix - MAP_SIZE/2) * MAP_RES
        y = (iy - MAP_SIZE/2) * MAP_RES
        return x, y
           
    def update_map(self, pos, scan):
        x, y, theta = pos
        
        for i, dist in enumerate(scan):
            if dist <= 0 or dist > 6:   # rang del LIDAR, 6, posu a tres per eficiencia
                continue
            
            angle = theta + (-30 + i * (240/len(scan))) * np.pi/180
            # angle = theta + (-30 + i * (240/len(scan))) * np.pi/180


            # Punt en coordenades del món
            wx = x + dist * np.cos(angle)
            wy = y + dist * np.sin(angle)

            ix, iy = self.world_to_map(wx, wy)

            # Marcar obstacle
            if 0 <= ix < MAP_SIZE and 0 <= iy < MAP_SIZE:
                self.grid[iy, ix] = 1
    
    def mark_free_cells(self, pos, scan):
        x, y, theta = pos

        MAX_LIDAR_RANGE = 3.0   # Hokuyo té fins a 30m, però 10 és suficient

        for i, dist in enumerate(scan):
            if dist <= 0:
                continue

            angle = theta + (-120 + i * (240/len(scan))) * np.pi/180

            # Si el LIDAR no veu obstacle, dist serà gran → marca fins al rang màxim
            max_dist = min(dist, MAX_LIDAR_RANGE)
            steps = int(max_dist / MAP_RES)

            for s in range(steps):
                wx = x + s * MAP_RES * np.cos(angle)
                wy = y + s * MAP_RES * np.sin(angle)

                ix, iy = self.world_to_map(wx, wy)
                if 0 <= ix < MAP_SIZE and 0 <= iy < MAP_SIZE:
                    if self.grid[iy, ix] == -1:
                        self.grid[iy, ix] = 0


    def detect_frontiers(self):
        frontiers = []

        for y in range(1, MAP_SIZE - 1):
            for x in range(1, MAP_SIZE - 1):

                # Cel·la lliure?
                if self.grid[y, x] == 0:

                    # Veïns 3x3
                    neighbors = self.grid[y-1:y+2, x-1:x+2]

                    # Toca alguna cel·la desconeguda?
                    if np.any(neighbors == -1):
                        frontiers.append((x, y))

        return frontiers

    def closest_frontier(self, pos, frontiers):
        x, y, _ = pos
        best = None
        best_dist = float('inf')

        for fx, fy in frontiers:
            wx, wy = self.map_to_world(fx, fy)
            d = np.hypot(wx - x, wy - y)
            if d < best_dist:
                best_dist = d
                best = (wx, wy)

        return best
