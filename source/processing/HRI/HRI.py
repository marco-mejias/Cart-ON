import requests
import base64
import os
import time
import pygame

add_commands = ["añadir", "añade", "añádeme", "mete", "apunta", "pon"]
delete_commands = ["borrar", "borra", "quita", "elimina", "saca"]
read_commands = ["qué hay", "lee", "dime", "cuál es", "revisa", "muestra", "enseña"]
clear_commands = ["vaciar", "vacía", "limpia", "borra toda"]

filler_words = ["por", "favor", "porfa", "a", "en", "la", "lista", "quiero", "necesito", "el", "los", "las", "un", "una"]
containers = ["bote", "botes", "pote", "potes", "litro", "litros", "paquete", "paquetes", "botella", "botellas", "de"]

number_mapping = {
    "un": 1, "una": 1, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, 
    "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10
}

def init_audio_system():
    # inicializa el sistema multimedia (display de audio)
    pygame.mixer.init()

def extract_quantity_and_product(spoken_text, command_list):
    # extrae entidades clave de la frase
    for command in command_list:
        spoken_text = spoken_text.replace(command, "")
        
    words = spoken_text.split()
    quantity = 1 
    product_words = []
    
    for word in words:
        if word.isdigit(): 
            quantity = int(word)
        elif word in number_mapping: 
            quantity = number_mapping[word]
        elif word not in filler_words and word not in containers:
            product_words.append(word)
            
    return quantity, " ".join(product_words).strip()

def speech_to_text(audio_data, api_key):
    # convierte audio en texto usando la api de google
    audio_wav = audio_data.get_wav_data()
    audio_b64 = base64.b64encode(audio_wav).decode("utf-8")

    endpoint_url = f"https://speech.googleapis.com/v1/speech:recognize?key={api_key}"
    payload = {
        "config": {"encoding": "LINEAR16", "sampleRateHertz": audio_data.sample_rate, "languageCode": "es-ES"},
        "audio": {"content": audio_b64}
    }

    try:
        response = requests.post(endpoint_url, json=payload)
        response_json = response.json()
        if "results" in response_json:
            return response_json["results"][0]["alternatives"][0]["transcript"].lower().strip()
    except Exception as e:
        print(f"error en la conexion sst: {e}")
    return None

def text_to_speech(text_to_say, api_key):
    # genera respuesta de voz (display)
    print(f"robot: {text_to_say}")
    endpoint_url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"
    
    payload = {
        "input": {"text": text_to_say},
        "voice": {"languageCode": "es-ES", "name": "es-ES-Neural2-F"},
        "audioConfig": {"audioEncoding": "MP3"}
    }
    
    try:
        response = requests.post(endpoint_url, json=payload)
        response_json = response.json()
        
        if "audioContent" in response_json:
            audio_bytes = base64.b64decode(response_json["audioContent"])
            temp_filename = "respuesta_temp.mp3"
            
            with open(temp_filename, "wb") as audio_file:
                audio_file.write(audio_bytes)
                
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
            pygame.mixer.music.unload()
            os.remove(temp_filename)
    except Exception as e:
        print(f"error reproduciendo audio tts: {e}")

def parse_intent(raw_text):
    # modulo cognitivo para clasificar la accion requerida
    if any(command in raw_text for command in add_commands):
        quantity, item = extract_quantity_and_product(raw_text, add_commands)
        return "add", item, quantity
    elif any(command in raw_text for command in delete_commands):
        quantity, item = extract_quantity_and_product(raw_text, delete_commands)
        return "delete", item, quantity
    elif any(command in raw_text for command in read_commands):
        return "read", None, None
    elif any(command in raw_text for command in clear_commands):
        return "clear", None, None
        
    return "unknown", None, None