import os
import json
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

#* 1. Configuración de la Conexión BD
DB_CONFIG = {
  'host': os.getenv("HOST_DB"),
  'user': os.getenv("USER_DB"),
  'password': os.getenv("PASSWORD_DB"),
  'database': os.getenv("DATABASE")
}

def conectar_db():
  try:
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn
  except mysql.connector.Error as err:
    print(f"Error al conectar a MySQL: {err}")
    return None
  
  
def buscar_expediente(conn, metadatos_busqueda):
  if not conn:
    print("No se pudo conectar a la base de datos")
    return None
  
  elif not metadatos_busqueda:
    print("No hay metadatos para buscar")
    return None
  
  cursor = conn.cursor(dictionary=True)
  
  #* Buscamos expediente cuyos metadatos coincidan con la lista de búsqueda
  placeholders = ', '.join(['%s'] * len(metadatos_busqueda))
  query = f"""
    SELECT
      E.id, E.nombre_expediente, E.unidad_administrativa,
      E.serie_documental, E.subserie_documental
    FROM expedientes AS E
    JOIN metadatos_expedientes AS M ON E.id = M.expediente_id
    WHERE M.metadato IN ({ placeholders })
    LIMIT 1
  """
  
  try:
    cursor.execute(query, metadatos_busqueda)
    expediente = cursor.fetchone()
    return expediente  
  
  except mysql.connector.Error as err:
    print(f"Error en la consulta SQL: {err}")
    return None
    
  finally:
    cursor.close()
    
def insertar_documento(conn, asunto, cuerpo_mensaje, clasificacion_openai_json):
    #* Inserta un nuevo documento en la tabla de pendientes.
    if not conn:
        print("No se pudo conectar a la base de datos para insertar el documento.")
        return False
    
    cursor = conn.cursor()
    query = """
        INSERT INTO documentos_pendientes (asunto, cuerpo_mensaje, clasificacion_openai)
        VALUES (%s, %s, %s)
    """
    
    try:
        cursor.execute(query, (asunto, cuerpo_mensaje, clasificacion_openai_json))
        conn.commit()
        print(f"Documento insertado correctamente como pendiente con ID: {cursor.lastrowid}")
        return True
    except mysql.connector.Error as err:
        print(f"Error al insertar documento pendiente: {err}")
        return False
    finally:
        cursor.close()    


# if __name__ == '__main__':
#   #* 2. Simulación del JSON que devuelve OpenAI
#   json_openai = """
#   {
#     "unidad_administrativa": "Sin especificar",
#     "asunto": "Curso de programación y desarrollo de software full stack",
#     "serie_documental": "Otros",
#     "subserie_documental": "General",
#     "tipologia_documental": "Carta",
#     "metadatos": [
#       "bases de datos: SQL, MySQL, MariaDB, Oracle",
#       "Análisis de datos: hojas de cálculo, pandas, matplotlib, aprendizaje automático",
#       "Python, Java, C#, PHP, HTML5, CSS3",
#       "Requisitos de hardware: 8GB RAM, i3 o superior, micrófono y cámara"
#     ]
#   }
#   """

#   #* 3. INICIO DEL PROCESO DE PRUEBA
#   conexion = conectar_db()
  
#   if conexion:
#     print("\n--- INICIANDO PRUEBA DE BÚSQUEDA ---")

#     try:
#       #* Parsear el JSON para obtener la lista de metadatos
#       clasificacion_openai = json.loads(json_openai)
#       metadatos_del_documento = clasificacion_openai.get('metadatos', [])

#       print(f"\nMetadatos extraídos de la clasificación: {metadatos_del_documento}")
      
#       #* 4. Búsqueda en la base de datos
#       expediente_encontrado = buscar_expediente(conexion, metadatos_del_documento)
      
#       #* 5. Imprimir el resultado
#       if expediente_encontrado:
#         print("\n¡Expediente encontrado en la base de datos!")
#         print("---")
#         for key, value in expediente_encontrado.items():
#           print(f"  {key.replace('_', ' ').title()}: {value}")
#       else:
#         print("\nNo se encontró un expediente coincidente.")
#         print("El documento se enviaría a la bandeja de documentos pendientes.")

#     except json.JSONDecodeError as e:
#       print(f"Error al procesar el JSON simulado: {e}")
    
#     finally:
#         conexion.close()