from core.base_module import BaseModule
from core.event import Event
from core.constants import INDENT_OUTPUT

class Navigation(BaseModule):
    def __init__(self, name, event_bus, shared_sensor_stream):
        super().__init__(name, event_bus)
        self.data_stream = shared_sensor_stream

    def handle_task(self, task):
        if task.type == "NAVIGATE_TO_TARGET":
            print(f"{INDENT_OUTPUT}[{self.name}] 🚀 Iniciando navegación al destino...")
            
        elif task.type == "START_MAPPING":
            print(f"{INDENT_OUTPUT}[{self.name}] 🗺️ Iniciando SLAM / Cartografía...")
            
        elif task.type == "STOP_MOTORS":
            print(f"{INDENT_OUTPUT}[{self.name}] 🛑 Frenando motores de emergencia.")