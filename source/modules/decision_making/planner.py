from threading import Thread
from queue import Empty
from core.task import Task

class Planner(Thread):
    def __init__(self, name, event_bus):
        super().__init__(name=name, daemon=True)
        self.event_bus = event_bus
        self.running = True
        
        # Guardaremos los módulos en un diccionario para mandarles tareas por nombre
        self.modules = {}
        
        self.fase_actual = "fase_2_interaccion"
        self.frase_pendiente = None 

    def append_modules(self, modules_list):
        for module in modules_list:
            self.modules[module.name] = module

    def stop(self):
        self.running = False

    def run(self):
        print(f"[{self.name}] ⚙️ Iniciando Orquestador (Actor Model)...")
        while self.running:
            try:
                event = self.event_bus.get(timeout=1.0)
                
                # PARCHE: Si por algún motivo llega un diccionario en lugar de un Event, lo adaptamos
                if isinstance(event, dict):
                    tipo = event.get("type")
                    data = event.get("data")
                    origen = event.get("origin", "Sistema")
                else:
                    tipo = event.type
                    data = event.data
                    origen = event.origin
                
                # Creamos un objeto falso al vuelo para no cambiar tu código de procesar_evento
                from collections import namedtuple
                EventoFalso = namedtuple('EventoFalso', ['type', 'data', 'origin'])
                self.procesar_evento(EventoFalso(tipo, data, origen))
                
                self.event_bus.task_done()
            except Empty:
                pass
            except Exception as e:
                print(f"[{self.name}] 🔴 Error crítico: {e}")

    def procesar_evento(self, event):
        tipo = event.type
        data = event.data
        origen = event.origin

        # ==========================================
        # 🗣️ 1. HUMANO HABLA
        # ==========================================
        if tipo == "VOICE_DETECTED":
            print(f"[{self.name}] 📥 Evento de {origen}: Humano dijo '{data}'")
            
            if self.fase_actual == "fase_1_escaneo":
                # Si estamos mapeando el súper, guardamos la frase y pedimos foto
                self.frase_pendiente = data
                print(f"[{self.name}] 📤 Enviando Task a Sensory: TAKE_PHOTO")
                self.modules["Sensory"].add_task(Task(type="TAKE_PHOTO"))
            else:
                # Si estamos en charla normal (fase 2 o 3), directo a la nube SIN foto
                print(f"[{self.name}] 📤 Enviando Task a HRI: SEND_TO_CLOUD (solo voz)")
                self.modules["HRI"].add_task(Task(type="SEND_TO_CLOUD", data=data))

        # 👁️ 2. FOTO LISTA
        elif tipo == "PHOTO_READY":
            print(f"[{self.name}] 📥 Evento de {origen}: Foto lista.")
            if self.frase_pendiente:
                print(f"[{self.name}] 📤 Enviando Task a HRI: SEND_TO_CLOUD")
                self.modules["HRI"].add_task(Task(type="SEND_TO_CLOUD", data=self.frase_pendiente))
                self.frase_pendiente = None

        # ==========================================
        # ☁️ 3. RESPUESTA DE LA NUBE
        # ==========================================
        elif tipo == "CLOUD_RESPONSE":
            print(f"[{self.name}] 📥 Evento de {origen}: Datos de la nube recibidos.")
            
            # Actualizamos fase
            nuevo_estado = data.get("estado_actual")
            if nuevo_estado and nuevo_estado != self.fase_actual:
                print(f"[{self.name}] 🔄 Transición: {self.fase_actual} -> {nuevo_estado}")
                self.fase_actual = nuevo_estado

            # 🎙️ Hablamos: Le pasamos ÚNICAMENTE el diccionario completo
            self.modules["HRI"].add_task(Task(type="SPEAK", data=data))

            # Nos movemos
            comando = data.get("comando_robot")
            if comando == "START_SLAM":
                self.modules["Navigation"].add_task(Task(type="START_MAPPING"))
            elif comando == "START_NAVIGATION":
                self.modules["Navigation"].add_task(Task(type="NAVIGATE_TO_TARGET"))
            elif comando == "STOP_MOTORS":
                self.modules["Navigation"].add_task(Task(type="STOP_MOTORS"))

        # 🛑 4. APAGADO GENERAL
        elif tipo == "SHUTDOWN":
            print(f"[{self.name}] 🛑 Apagando orquestador...")
            self.stop()