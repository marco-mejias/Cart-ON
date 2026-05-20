from connect.connect import connect
from algorithms.algorithms import *
import time

def main():
    clientID = connect(19999)
    if clientID == -1:
        return

    robot = Robot(clientID)
    robot.connect_hardware()

    mapa = Map()

    print("Iniciant prova de LIDAR + MAPA + FRONTIERS...\n")

    steps = [0]

    try:
        i = 0
        while i < 10:
            scan = robot.read_lidar()
            pose = robot.get_pose()

            if scan is None or pose is None:
                continue

            # x, y, theta = pose

            # # 1) Pose del robot
            # theta_deg = np.degrees(theta)
            # print(f"POSE -> x: {x:.3f}, y: {y:.3f}, theta: {theta_deg:.1f}°")

            # # 2) Índex del feix amb distància MÉS GRAN (candidat a frontal)
            # idx_max = int(np.argmax(scan))
            # dist_max = scan[idx_max]
            # print(f"LIDAR -> max dist: {dist_max:.3f} m  a index {idx_max}")

            # # 3) Índex del feix amb distància MÉS PETITA (obstacle més proper)
            # idx_min = int(np.argmin(scan))
            # dist_min = scan[idx_min]
            # print(f"LIDAR -> min dist: {dist_min:.3f} m  a index {idx_min}")

            # print("-" * 40)
            # time.sleep(0.2)
            i = i + 1

            mapa.update_map(pose, scan)
            mapa.mark_free_cells(pose, scan)
            
           # robot.up()
            time.sleep(1)



            # # 1) Fase inicial: AVANÇAR RECTE
            if initial_exploration(robot, scan, steps):
                 continue

            # # 2) Fase frontier
            navigate(robot, mapa, pose, scan)

            # time.sleep(0.05)
        # ix, iy = mapa.world_to_map(pose[0], pose[1])
        # window = mapa.grid[iy-10:iy+10, ix-10:ix+10]
        # print(window)
        # print("-" * 40)
        
    except KeyboardInterrupt:
        print("\nProva finalitzada.")

if __name__ == "__main__":
    main()
