import os
import sys
from dotenv import load_dotenv

# anadimos la raiz del proyecto al path para importar modulos correctamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from processing.data import data_manager
from processing.HRI import HRI
from sensor import sensor

# inicializar entorno y credenciales
load_dotenv()
api_key = os.getenv("api_key")

if not api_key:
    print("error critico: falta la api_key en el archivo .env")
    exit()

def main_loop():
    # capa 1: toma de decisiones. el planificador orquesta todo el sistema
    HRI.init_audio_system()
    print("sistema iniciado. el planificador esta orquestando las capas.")
    HRI.text_to_speech("sistema iniciado. dime qué necesitas.", api_key)
    
    while True:
        print("\nplanificador: esperando eventos sensoriales...")
        
        # 1. obtener datos de la capa de abstraccion de hardware
        audio_data = sensor.capture_audio()
        if not audio_data:
            continue

        # 2. enviar datos al modulo cognitivo para procesarlos
        raw_text = HRI.speech_to_text(audio_data, api_key)
        if not raw_text:
            continue
            
        print(f"hri reporta: '{raw_text}'")
        
        # 3. clasificar la intencion del usuario
        intent, item, quantity = HRI.parse_intent(raw_text)
        
        if intent == "unknown":
            print("planificador: orden desconocida. ignorando evento.")
            continue
            
        # 4. interactuar con el manejador de datos segun la intencion
        shopping_list = data_manager.load_list()
        
        if intent == "add":
            if item:
                shopping_list[item] = shopping_list.get(item, 0) + quantity
                data_manager.save_list(shopping_list)
                HRI.text_to_speech(f"he añadido {quantity} de {item}. ya tienes {shopping_list[item]} en total.", api_key)
            else:
                HRI.text_to_speech("no he entendido qué producto quieres añadir.", api_key)
                
        elif intent == "delete":
            if item in shopping_list:
                del shopping_list[item]
                data_manager.save_list(shopping_list)
                HRI.text_to_speech(f"he borrado el producto {item} completamente de la lista.", api_key)
            else:
                HRI.text_to_speech(f"no encontré {item} en la lista.", api_key)
                
        elif intent == "read":
            if shopping_list:
                formatted_list = ", ".join([f"{qty} {prod}" for prod, qty in shopping_list.items()])
                HRI.text_to_speech(f"en la lista tienes: {formatted_list}.", api_key)
            else:
                HRI.text_to_speech("la lista de la compra está vacía.", api_key)
                
        elif intent == "clear":
            data_manager.save_list({})
            HRI.text_to_speech("he vaciado la lista de la compra por completo.", api_key)

if __name__ == "__main__":
    main_loop()