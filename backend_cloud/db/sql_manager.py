# db/sql_manager.py
# (Asegúrate de importar tu librería de conexión real: psycopg2, pymysql o sqlalchemy)

class SQLManager:
    def __init__(self):
        print("[SQLManager] 🗄️ Gestor de Base de Datos inicializado.")
        # Aquí inicializarías tu conexión real a Google Cloud SQL

    def get_product_info(self, item_name: str):
        """
        Búsqueda difusa (Fuzzy Search). 
        Encuentra 'Plátano de Canarias' aunque busques 'platano'.
        """
        if not item_name:
            return None
            
        # 1. Aseguramos que el término esté en minúsculas para comparar
        termino = item_name.lower()
        
        # ⚠️ AQUÍ VA TU LÓGICA SQL REAL. El concepto es usar LIKE con %:
        # QUERY: SELECT * FROM productos WHERE LOWER(nombre_pantalla) LIKE '%platano%' OR LOWER(nombre_yolo) LIKE '%platano%'
        
        # --- SIMULACIÓN BASADA EN TU CAPTURA DE PANTALLA ---
        simulacion_bd = [
            {"nombre_yolo": "apple", "nombre_pantalla": "Manzana Fuji Premium", "precio": 1.89, "stock_actual": 20},
            {"nombre_yolo": "banana", "nombre_pantalla": "Plátano de Canarias", "precio": 2.15, "stock_actual": 15},
            {"nombre_yolo": "bottle", "nombre_pantalla": "Botella de Agua Bezoya 1L", "precio": 0.85, "stock_actual": 30},
            {"nombre_yolo": "tomato", "nombre_pantalla": "Tomate Pera", "precio": 1.20, "stock_actual": 50}
        ]
        
        # Buscamos si la palabra raíz está dentro de nombre_yolo o nombre_pantalla
        for producto in simulacion_bd:
            # Quitamos tildes rápido para comparar de forma segura
            nombre_limpio = producto["nombre_pantalla"].lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
            
            if termino in nombre_limpio or termino in producto["nombre_yolo"].lower():
                return producto
                
        return None