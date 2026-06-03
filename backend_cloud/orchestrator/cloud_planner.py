import unicodedata
from db.sql_manager import SQLManager
from ai_services.nlp_qwen import NLPQwen
from ai_services.vision_qwen import VisionQwen

# Función para quitar tildes y estandarizar nombres
def limpiar_nombre(texto):
    if not texto: return "producto desconocido"
    texto_sin_tildes = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto_sin_tildes.lower().strip()

class PlannerCloud:
    def __init__(self):
        print("[PlannerCloud] ⚙️ Orquestador en la Nube iniciado.")
        self.sql = SQLManager()
        self.nlp = NLPQwen()
        self.vision = VisionQwen()
        self.estado_actual = "fase_2_interaccion"
        self.lista_compra = {}

    def procesar_peticion_hri(self, texto_usuario: str, imagen_bytes: bytes, mime_type: str = "image/jpeg"):
        intent, item_crudo, quantity, reply = self.nlp.parse_intent(texto_usuario)
        
        # 🧹 Limpiamos el producto para que "Macarrón", "macarron" y "macarrones" sean lo mismo
        item = limpiar_nombre(item_crudo)
        
        if intent == "start_mapping":
            self.estado_actual = "fase_1_escaneo"
            return {"status": "success", "comando_robot": "START_SLAM", "texto": "Iniciando mapeo de los pasillos."}
        elif intent == "start_assistance":
            self.estado_actual = "fase_3_asistencia"
            return {"status": "success", "comando_robot": "START_NAVIGATION", "texto": "Modo guía activado, sígueme."}
        elif intent == "stop_mapping":
            self.estado_actual = "fase_2_interaccion"
            return {"status": "success", "comando_robot": "STOP_MOTORS", "texto": "Motores detenidos."}

        contexto_interno = ""

        if intent == "chat":
            if imagen_bytes and len(imagen_bytes) > 5000:
                return {"status": "success", "texto": self.vision.visual_chat(imagen_bytes, texto_usuario, mime_type)}
            # Le damos una pista a la IA para que tenga contexto si el usuario solo dice "sí" o "no"
            contexto_interno = "El usuario está charlando o asintiendo. Responde con naturalidad a su comentario."

        # 🛒 LISTA DE LA COMPRA (Independiente del stock)
        elif intent == "add":
            self.lista_compra[item] = self.lista_compra.get(item, 0) + quantity
            contexto_interno = f"Has agrupado y añadido exitosamente {quantity} de '{item}' a la lista de la compra del usuario."
            
        elif intent == "delete":
            if item in self.lista_compra:
                del self.lista_compra[item]
                contexto_interno = f"Has quitado '{item}' de su lista."
            else:
                contexto_interno = f"Dile que no tenía '{item}' en su lista."
                
        elif intent == "read_list":
            if not self.lista_compra:
                contexto_interno = "Dile que su lista de la compra está completamente vacía."
            else:
                items = ", ".join([f"{v} unidades de {k}" for k, v in self.lista_compra.items()])
                contexto_interno = f"Dile al usuario que en su lista de la compra tiene apuntado exactamente esto: {items}."
                
        elif intent == "clear":
            self.lista_compra.clear()
            contexto_interno = "Confírmale que has vaciado y borrado toda su lista de la compra."

        # 🏪 CONSULTAS A LA TIENDA Y STOCK (Fíjate que check_availability ahora está aquí)
        elif intent in ["read", "read_stock", "check_availability"]:
            if item == "esto" or item == "producto desconocido":
                if imagen_bytes and len(imagen_bytes) > 5000:
                    item = self.vision.identify_product(imagen_bytes, mime_type)
                else:
                    contexto_interno = "Pregunta por stock, pero no sabes qué producto es. Pídele que especifique el nombre."
            else:
                info = self.sql.get_product_info(item)
                if info:
                    contexto_interno = f"Información técnica de la base de datos: Sí vendemos el producto {info['nombre_pantalla']}. Cuesta {info['precio']} euros y hay {info['stock_actual']} en el almacén de la tienda."
                else:
                    contexto_interno = f"Has buscado '{item}' en la base de datos de nuestro supermercado y no lo vendemos. Asegúrate de decirle que NO lo tenemos en la tienda."
        else:
            contexto_interno = "No has entendido qué quiere hacer el usuario. Pídele amablemente que lo repita."

        # Generación de voz natural
        respuesta_natural = self.nlp.generate_response(texto_usuario, contexto_interno)

        return {"status": "success", "texto": respuesta_natural, "estado_actual": self.estado_actual}