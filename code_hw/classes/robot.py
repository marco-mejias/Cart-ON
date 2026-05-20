from connect import sim
import math

class Robot:
    def __init__(self, clientID):
        self.clientID = clientID
        
        self.left_motor = None
        self.right_motor = None
        
        self.W = 0.350   # Wheelbase: Distància entre el centre de les dues rodes (en metres)
        self.R = 0.05   # Radi de la roda (en metres)
        self.encoder_left = 0.0
        self.encoder_right = 0.0        
        self.speed = 5.0
        self.robot_base = None


    def connect_hardware(self):
            # Connexió de Motors
            _, self.left_motor = sim.simxGetObjectHandle(self.clientID, 'DC_L', sim.simx_opmode_blocking)
            _, self.right_motor = sim.simxGetObjectHandle(self.clientID, 'DC_R', sim.simx_opmode_blocking)
            
            # Inicialitzar Els nostres Encoders
            sim.simxGetJointPosition(self.clientID, self.left_motor, sim.simx_opmode_streaming)
            sim.simxGetJointPosition(self.clientID, self.right_motor, sim.simx_opmode_streaming)
            
            # Iniciar streaming del LIDAR
            sim.simxGetStringSignal(self.clientID, "lidar_data", sim.simx_opmode_streaming)
            
            # Iniciar el nostre robot
            _, self.robot_base = sim.simxGetObjectHandle(self.clientID, 'Cart_ON', sim.simx_opmode_blocking)
            sim.simxGetObjectPosition(self.clientID, self.robot_base, -1, sim.simx_opmode_streaming)
            sim.simxGetObjectOrientation(self.clientID, self.robot_base, -1, sim.simx_opmode_streaming)
            err, h = sim.simxGetObjectHandle(self.clientID, 'Cart_ON', sim.simx_opmode_blocking)
            print("Handle:", h, "Error:", err)

    def read_lidar(self):
        res, data = sim.simxGetStringSignal(self.clientID, "lidar_data", sim.simx_opmode_buffer)
        if res == sim.simx_return_ok and data:
            scan = sim.simxUnpackFloats(data)
            return scan
        return None

    def get_pose(self):
        res_pos, pos = sim.simxGetObjectPosition(
            self.clientID, self.robot_base, -1, sim.simx_opmode_buffer)

        # Orientació (Euler angles)
        res_ori, ori = sim.simxGetObjectOrientation(
            self.clientID, self.robot_base, -1, sim.simx_opmode_buffer)

        if res_pos == sim.simx_return_ok and res_ori == sim.simx_return_ok:
            x = pos[0]
            y = pos[1]
            theta = ori[2]   # yaw, rotation
            return x, y, theta
            
        return None

            
    def update_encoders(self):
        res_l, pos_l = sim.simxGetJointPosition(self.clientID, self.left_motor, sim.simx_opmode_buffer)
        
        if res_l == sim.simx_return_ok:
            # Calculem la diferència directa respecte a la lectura anterior
            diff = pos_l - self.last_encoder_left
            
            # CORRECCIÓ DEL SALT DE VOLTA DETECTAT (El truc de robòtica)
            if diff > math.pi:
                diff -= 2 * math.pi
            elif diff < -math.pi:
                diff += 2 * math.pi
                
            # Acumulem el desplaçament real (sempre creixent en absolut)
            self.total_left_radians += diff
            self.last_encoder_left = pos_l
        
    # MOVIMENTS
    def up(self):
        sim.simxSetJointTargetVelocity(self.clientID, self.right_motor, self.speed, sim.simx_opmode_oneshot)
        sim.simxSetJointTargetVelocity(self.clientID, self.left_motor, self.speed, sim.simx_opmode_oneshot)

    def left(self):
        sim.simxSetJointTargetVelocity(self.clientID, self.right_motor, self.speed, sim.simx_opmode_oneshot)
        sim.simxSetJointTargetVelocity(self.clientID, self.left_motor, -self.speed, sim.simx_opmode_oneshot)
    
    def right(self):
        sim.simxSetJointTargetVelocity(self.clientID, self.right_motor, -self.speed, sim.simx_opmode_oneshot)
        sim.simxSetJointTargetVelocity(self.clientID, self.left_motor, self.speed, sim.simx_opmode_oneshot)

    def stop(self):
        sim.simxSetJointTargetVelocity(self.clientID, self.right_motor, 0, sim.simx_opmode_oneshot)
        sim.simxSetJointTargetVelocity(self.clientID, self.left_motor, 0, sim.simx_opmode_oneshot)

    def set_speed(self, v, w):
        # v = velocitat lineal (m/s)
        # w = velocitat angular (rad/s)

        # Cinemàtica diferencial
        v_r = (2*v + w*self.W) / (2*self.R)
        v_l = (2*v - w*self.W) / (2*self.R)

        sim.simxSetJointTargetVelocity(self.clientID, self.right_motor, v_r, sim.simx_opmode_oneshot)
        sim.simxSetJointTargetVelocity(self.clientID, self.left_motor,  v_l, sim.simx_opmode_oneshot)

    def stop_speed(self):
        sim.simxSetJointTargetVelocity(self.clientID, self.right_motor, 0, sim.simx_opmode_oneshot)
        sim.simxSetJointTargetVelocity(self.clientID, self.left_motor,  0, sim.simx_opmode_oneshot)