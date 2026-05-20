from classes.robot import Robot
from classes.map import Map
import numpy as np

LIDAR_FRONT = int((960 + 1021) / 2)   # = 990

# -------------------------
# Control d'orientació
# -------------------------

def angle_to_target(pose, target):
    x, y, theta = pose
    tx, ty = target

    desired = np.arctan2(ty - y, tx - x)
    error = desired - theta
    return (error + np.pi) % (2*np.pi) - np.pi


def compute_turn_speed(angle_error):
    Kp = 1.0
    return np.clip(Kp * angle_error, -0.6, 0.6)


def compute_forward_speed(angle_error):
    max_v = 0.5
    return max_v * max(0, 1 - abs(angle_error))


# -------------------------
# LIDAR / obstacles
# -------------------------

def obstacle_detected(scan, threshold=0.5):
    window = scan[LIDAR_FRONT-15 : LIDAR_FRONT+15]
    return min(window) < threshold


# -------------------------
# Fase inicial: avanç recte
# -------------------------

def initial_exploration(robot, scan, counter):
    window = scan[LIDAR_FRONT-15 : LIDAR_FRONT+15]
    min_front = min(window)

    if counter[0] < 50:   # ~2–3 segons
        if min_front < 0.5:
            robot.set_speed(0, 2)
            print("Girem!!")
        else:
            robot.set_speed(5, 0)
            print("Endavant!!")
        counter[0] += 1
        return True
    return False


# -------------------------
# Navegació per fronteres
# -------------------------

def navigate(robot, mapa, pose, scan):
    frontiers = mapa.detect_frontiers()
    if not frontiers:
        robot.set_speed(0, 0)
        return

    target = mapa.closest_frontier(pose, frontiers)
    if not target:
        robot.set_speed(0, 0)
        return

    angle_error = angle_to_target(pose, target)

    if obstacle_detected(scan):
        robot.set_speed(0.0, 0.5)
        return

    v = compute_forward_speed(angle_error)
    w = compute_turn_speed(angle_error)
    robot.set_speed(v, w)

    tx, ty = target
    if np.hypot(tx - pose[0], ty - pose[1]) < 0.4:
        robot.set_speed(0, 0)

