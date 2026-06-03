from queue import Queue
from dotenv import load_dotenv
import os
import sys

# Tus módulos locales (ahora en versión Thin Edge)
from modules.decision_making.planner import Planner
from modules.processing.navigation.navigation import Navigation
from modules.sensor.sensor import SensoryModule
from modules.processing.HRI.HRI import HRI

def main():
    print("==================================================")
    print(" ☁️ INICIANDO CART-ON (EVENT-DRIVEN THIN EDGE) ☁️")
    print("==================================================")

    event_bus = Queue()
    sensor_data = {}
    shared_data = {} # Para almacenar cosas temporales como el estado de la batería o la IP

    # Cargar variables de entorno
    load_dotenv()

    # ⚠️ ATENCIÓN: Solo cargamos la clave de voz. La de Gemini ya está en la nube.
    api_key = os.getenv("API_KEY")             

    if not api_key:
        print("Error crítico: falta la API_KEY (Voz STT/TTS) en el archivo .env")
        sys.exit(1)

    # 1. Instanciamos los módulos (pasándoles el bus para que hablen entre ellos)
    planner = Planner("Planner", event_bus)
    navigation = Navigation("Navigation", event_bus, sensor_data)
    sensory = SensoryModule("Sensory", event_bus, sensor_data)
    
    # El HRI ya no recibe la clave de Gemini, solo la de Google Cloud Voz
    human_interaction = HRI("HRI", event_bus, sensor_data, api_key)

    # 2. Conectamos los módulos al cerebro
    planner.append_modules([navigation, sensory, human_interaction])

    # 3. Arrancamos los hilos (Multithreading)
    planner.start()
    navigation.start()
    sensory.start()
    human_interaction.start()

    try:
        # Bucle de vigilancia del hilo principal
        while True:
            import time
            time.sleep(1) 
    except KeyboardInterrupt:
        print("\n[Main] 🛑 Cierre manual detectado (Ctrl+C). Apagando robot...")
        # Gritamos al bus para que todos los hilos se enteren de que hay que cerrar
        event_bus.put({"type": "SHUTDOWN"})
        
        # Esperamos a que los módulos terminen sus tareas pendientes antes de matar el programa
        planner.join(timeout=3)
        human_interaction.join(timeout=3)
        navigation.join(timeout=3)
        sensory.join(timeout=3)
        print("[Main] ✅ Sistema cerrado limpiamente.")

if __name__ == "__main__":
    main()