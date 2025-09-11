import os
from openai import OpenAI
import json
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
  api_key = os.getenv("OPENAI_API_KEY")
)

def clasificarcion_openai(texto_completo):
  """Función para clasificar documentos según parámetros SGDEA"""
  prompt = f"""
  Eres un assitente de clasificación documental para una entidad importante. Tu tarea consiste en analizar el siguiente texto de una solicitud ciudadana para identificar y clasificar la información clave.
  
  Texto a analizar: 
  {texto_completo}
  
  Extrae y clasifica la siguiente información según los parametros de un Sistema de Gestión y Archivo (SGDEA): 
  1. **Unidad administrativa:** Identifica e área o departamento responsable (por ejemplo, 'Secretaria de Hacienda', 'Departamento de Tránsito'). Si no se menciona, usa 'Sin especificar'.
  2. **Asunto:** Resume el tema principal de la solicitud en no más de 10 palabras.
  3. **Serie documental:** Basándote en el contenido, clasifica la solicitud en una de las siguientes categorías: 'Peticiones', 'Quejas', 'Reclamos', 'Sugerencias', 'Felicitaciones'. Si no aplica, usa 'Otros'.
  4. **Subserie documental:** Ofrece una subcategoría más específica para la serie (por ejemplo, para 'Peticiones', podría ser 'Trámites de Licencia'). Si no se puede determinar, usa 'General'.
  5. **Tipología documental:** Identifica el tipo de documento (ej. 'Solicitud de información', 'Oficio', 'Carta'). Si no se puede, usa 'Carta'.
  6. **Metadatos:** Extrae palabras clave o frases relevantes que describan la solicitud (por ejemplo, 'licencia de construcción', 'demora en proceso').
  
  Proporciona la respuesta únicamente en formato JSON. El JSON debe tener la siguiente estructura:
  {{
    'unidad_administrativa': '...',
    'asunto': '...',
    'serie_documental': '...',
    'subserie_documental': '...',
    'tipologia_documental': '...',
    'metadatos': [...]
  }}
  """
  
  try:
    response = client.chat.completions.create(
      model="gpt-5-nano",
      messages=[
        {"role": "system", "content": "Eres un asistente de ayuda"},
        {"role": "user", "content": prompt}
      ]
    )
    
    respuesta_str = response.choices[0].message.content
    return respuesta_str
  
  except Exception as e:
    return None

def clasificacion_por_paginas(texto_completo):
  """Función para clasificar documento completo según parámetros SGDEA
  
  Args:
    texto_completo (str): Texto completo del documento
  
  Returns:
    dict: Diccionario con clasificación del documento completo
  """
  clasificaciones = {}
  
  # Procesar todo el documento como una unidad
  texto_pagina = texto_completo
    
  # Crear prompt para el documento completo
  prompt = f"""
  Eres un asistente de clasificación documental para una entidad importante. Tu tarea consiste en analizar el siguiente texto completo de un documento para identificar y clasificar la información clave.
  
  Texto completo del documento a analizar: 
  {texto_pagina}
  
  Extrae y clasifica la siguiente información según los parámetros de un Sistema de Gestión y Archivo (SGDEA): 
  1. **Unidad administrativa:** Identifica el área o departamento responsable (por ejemplo, 'Secretaria de Hacienda', 'Departamento de Tránsito'). Si no se menciona, usa 'Sin especificar'.
  2. **Asunto:** Resume el tema principal del documento en no más de 10 palabras.
  3. **Serie documental:** Basándote en el contenido, clasifica la información en una de las siguientes categorías: 'Peticiones', 'Quejas', 'Reclamos', 'Sugerencias', 'Felicitaciones'. Si no aplica, usa 'Otros'.
  4. **Subserie documental:** Ofrece una subcategoría más específica para la serie (por ejemplo, para 'Peticiones', podría ser 'Trámites de Licencia'). Si no se puede determinar, usa 'General'.
  5. **Tipología documental:** Identifica el tipo de documento (ej. 'Solicitud de información', 'Oficio', 'Carta'). Si no se puede, usa 'Carta'.
  6. **Metadatos:** Extrae palabras clave o frases relevantes que describan el contenido del documento (por ejemplo, 'licencia de construcción', 'demora en proceso').
  7. **Contenido relevante:** Indica si el documento contiene información sustancial ('Sí') o es principalmente formato/encabezados ('No').
  
  Proporciona la respuesta únicamente en formato JSON. El JSON debe tener la siguiente estructura:
  {{
    "documento_completo": true,
    "unidad_administrativa": "...",
    "asunto": "...",
    "serie_documental": "...",
    "subserie_documental": "...",
    "tipologia_documental": "...",
    "metadatos": [...],
    "contenido_relevante": "..."
  }}
  """
    
  try:
    response = client.chat.completions.create(
      model="gpt-5-nano",
      messages=[
        {"role": "system", "content": "Eres un asistente especializado en clasificación documental."},
        {"role": "user", "content": prompt}
      ]
    )
    
    respuesta_str = response.choices[0].message.content
    
    try:
      clasificacion_json = json.loads(respuesta_str)
      clasificaciones["documento_completo"] = clasificacion_json
    except json.JSONDecodeError:
      clasificaciones["documento_completo"] = {"error": "JSON inválido", "respuesta_raw": respuesta_str}
  
  except Exception as e:
    clasificaciones["documento_completo"] = {"error": f"Error en clasificación: {str(e)}"}
  
  return clasificaciones