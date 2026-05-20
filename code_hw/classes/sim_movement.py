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
        
        self.speed = 3.0
        # self.sensors = {'us1': None, 'us2': None, 'us3': None, 'us4': None}
        # self.detection = {'us1': False, 'us2': False, 'us3': False, 'us4': False}
        # self.distances = {'us1': 999.0, 'us2': 999.0, 'us3': 999.0, 'us4': 999.0}

    def connect_hardware(self):
            # Connexió de Motors
            _, self.left_motor = sim.simxGetObjectHandle(self.clientID, 'DC_L', sim.simx_opmode_blocking)
            _, self.right_motor = sim.simxGetObjectHandle(self.clientID, 'DC_R', sim.simx_opmode_blocking)
            
            # Inicialitzar l'streaming de la posició dels joints (Els nostres Encoders)
            sim.simxGetJointPosition(self.clientID, self.left_motor, sim.simx_opmode_streaming)
            sim.simxGetJointPosition(self.clientID, self.right_motor, sim.simx_opmode_streaming)
            
            # Connexió d'Ultrasons
            # for name in self.sensors.keys():
            #     _, handle = sim.simxGetObjectHandle(self.clientID, name, sim.simx_opmode_blocking)
            #     self.sensors[name] = handle
            #     sim.simxReadProximitySensor(self.clientID, handle, sim.simx_opmode_streaming)
            
            # _, self.robot_base = sim.simxGetObjectHandle(self.clientID, 'Robot_Base', sim.simx_opmode_blocking)
            
            # # Inicialitzem l'streaming de posició i orientació respecte al món (-1)
            # sim.simxGetObjectPosition(self.clientID, self.robot_base, -1, sim.simx_opmode_streaming)
            # sim.simxGetObjectOrientation(self.clientID, self.robot_base, -1, sim.simx_opmode_streaming)
            # _, pos_l = sim.simxGetJointPosition(self.clientID, self.left_motor, sim.simx_opmode_blocking)
            # self.last_encoder_left = pos_l
            # self.total_left_radians = 0.0

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
        
    def print_real_time_pose(self):
        """Llegeix i mostra la posició X, Y, Z i els angles d'Euler de la base"""
        # El -1 indica que volem la posició respecte a l'origen del món de Coppelia
        res_pos, pos = sim.simxGetObjectPosition(self.clientID, self.robot_base, -1, sim.simx_opmode_buffer)
        res_ori, ori = sim.simxGetObjectOrientation(self.clientID, self.robot_base, -1, sim.simx_opmode_buffer)
        
        if res_pos == sim.simx_return_ok and res_ori == sim.simx_return_ok:
            x, y, z = pos[0], pos[1], pos[2]
            
            # Coppelia retorna els angles d'Euler en radiants (Alpha, Beta, Gamma)
            # Els convertim a graus per veure'ls de forma més humana (Roll, Pitch, Yaw)
            roll = math.degrees(ori[0])
            pitch = math.degrees(ori[1])
            yaw = math.degrees(ori[2]) # El 'Yaw' és el que varia quan el robot gira sobre el terra
            
            # Print elegant en una sola línia que es va actualitzant gràcies al retorn de carro (\r)
            print(f"📍 POS: [{x:6.2f}, {y:6.2f}, {z:6.2f}] | 🔄 EULER (deg): [R:{roll:6.1f}°, P:{pitch:6.1f}°, Y:{yaw:6.1f}°]", end='\r')
            
    # def update_sensor_distances(self):
    #     threshold = 1.0
        
    #     for name, handle in self.sensors.items():
    #         res, detectionState, detectedPoint, _, _ = sim.simxReadProximitySensor(
    #             self.clientID, handle, sim.simx_opmode_buffer)
        
    #         if res == sim.simx_return_ok and detectionState:
    #             # Calculem la distància real (norma del vector 3D)
    #             dist = (detectedPoint[0]**2 + detectedPoint[1]**2 + detectedPoint[2]**2)**0.5             
    #             self.distances[name] = dist
                
    #             if dist < threshold:
    #                 self.detection[name] = True
    #             else:
    #                 self.detection[name] = False
    #         else:    
    #             self.distances[name] = 999.0
    #             self.detection[name] = False

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