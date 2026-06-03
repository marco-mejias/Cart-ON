import threading
import requests
import time
import os
import base64
import tempfile
import speech_recognition as sr

# Silenciamos pygame antes de importarlo
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

from core.base_module import BaseModule
from core.event import Event
from core.constants import INDENT_OUTPUT

class HRI(BaseModule):
    def __init__(self, name, event_bus, sensor_data, api_key):
        super().__init__(name, event_bus)
        self.sensor_data = sensor_data
        self.api_key = api_key
        self.cloud_url = "https://cart-on-api-225606614592.europe-southwest1.run.app/api/v1/interaccion"
        
        # 🚥 SEMÁFORO: Controla cuándo podemos usar el teclado
        self.puedo_escuchar = threading.Event()
        self.puedo_escuchar.set() # Empezamos con luz verde
        
        # 🔊 Calentamos el motor de audio en el arranque
        try:
            pygame.mixer.init()
            print(f"{INDENT_OUTPUT}[{self.name}] 🔊 Motor de audio pre-cargado y listo.")
        except Exception as e:
            print(f"{INDENT_OUTPUT}[{self.name}] 🔴 Aviso: No se pudo iniciar el audio: {e}")
        
        # Arrancamos el hilo del micrófono real
        threading.Thread(target=self._escuchar_microfono, daemon=True).start()

    def handle_task(self, task):
        if task.type == "SEND_TO_CLOUD":
            # 🔴 Ponemos el semáforo en rojo para bloquear el teclado mientras piensa
            self.puedo_escuchar.clear() 
            
            texto_usuario = task.data
            foto_bytes = self.sensor_data.get("last_frame", b'\x00')
            
            print(f"{INDENT_OUTPUT}[{self.name}] ☁️ Conectando a la nube...")
            respuesta = self._hacer_peticion(texto_usuario, foto_bytes)
            
            self.publish_event(Event(origin=self.name, type="CLOUD_RESPONSE", data=respuesta))
            
        elif task.type == "SPEAK":
            # Extraemos el paquete que viene de la nube
            datos_nube = task.data
            texto = datos_nube.get("texto", "Error en la respuesta")
            audio_b64 = datos_nube.get("audio_b64", None)

            print(f"\n{INDENT_OUTPUT}🤖 [Cart-ON Dice]: {texto}\n")
            
            # Si la nube nos ha mandado un audio, lo reproducimos
            if audio_b64:
                try:
                    audio_bytes = base64.b64decode(audio_b64)
                    
                    # Guardamos el MP3 temporalmente
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                        fp.write(audio_bytes)
                        temp_path = fp.name
                        
                    # Reproducimos el archivo
                    pygame.mixer.music.load(temp_path)
                    pygame.mixer.music.play()
                    
                    # Pausamos el código de este hilo hasta que el robot termine de hablar
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                        
                    # Liberamos el archivo para que Windows nos deje borrarlo limpiamente
                    pygame.mixer.music.unload()
                    os.remove(temp_path)
                except Exception as e:
                    print(f"{INDENT_OUTPUT}🔴 Error al reproducir audio: {e}")

            # 🟢 Ponemos el semáforo en verde otra vez tras hablar
            self.puedo_escuchar.set()

    def _hacer_peticion(self, frase, foto_bytes):
        try:
            archivos = {'image_file': ('frame.jpg', foto_bytes, 'image/jpeg')}
            datos = {'frase_usuario': frase}
            res = requests.post(self.cloud_url, files=archivos, data=datos, timeout=15)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.RequestException as e:
            # Si falla, liberamos el semáforo para no quedarnos atascados
            self.puedo_escuchar.set()
            return {"status": "error", "texto": "Perdona, mis antenas no conectan con internet."}

    def _escuchar_microfono(self):
        # Inicializamos el reconocedor y el micrófono
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        print(f"{INDENT_OUTPUT}[{self.name}] 🎤 Calibrando micrófono (ruido ambiente)...")
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=2)
        print(f"{INDENT_OUTPUT}[{self.name}] ✅ Micrófono calibrado y listo.")

        time.sleep(1)
        while self.running:
            # Esperamos silenciosamente a que el semáforo esté en verde (que el robot no esté hablando)
            self.puedo_escuchar.wait() 

            try:
                with mic as source:
                    print(f"\n{INDENT_OUTPUT}🟢 Te escucho... (Habla ahora o di 'salir')")
                    # Escucha hasta que dejas de hablar
                    audio = recognizer.listen(source, timeout=None, phrase_time_limit=10)

                # 🔴 Ponemos el semáforo en rojo para que no nos escuche mientras procesa
                self.puedo_escuchar.clear()

                print(f"{INDENT_OUTPUT}⏳ Traduciendo tu voz a texto...")
                # Traducimos usando el motor gratuito de Google en español
                texto = recognizer.recognize_google(audio, language="es-ES")
                print(f"{INDENT_OUTPUT}🗣️ Has dicho: '{texto}'")

                if texto.lower() == 'salir':
                    self.publish_event(Event(origin=self.name, type="SHUTDOWN"))
                    break
                elif texto.strip():
                    # Disparamos el evento al orquestador
                    self.publish_event(Event(origin=self.name, type="VOICE_DETECTED", data=texto))

            except sr.UnknownValueError:
                print(f"{INDENT_OUTPUT}🤷 No te he entendido bien por el ruido. Volviendo a escuchar...")
                self.puedo_escuchar.set() # Volvemos a dar luz verde
            except sr.RequestError as e:
                print(f"{INDENT_OUTPUT}🔴 Error de conexión con el servicio de voz: {e}")
                self.puedo_escuchar.set()
            except Exception as e:
                if self.running:
                    print(f"{INDENT_OUTPUT}🔴 Error inesperado en el micro: {e}")
                    self.puedo_escuchar.set()