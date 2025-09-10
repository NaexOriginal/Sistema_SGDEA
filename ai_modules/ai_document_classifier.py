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

def clasificacion_por_paginas(paginas_texto):
  """Función para clasificar documentos página por página según parámetros SGDEA
  
  Args:
    paginas_texto (dict): Diccionario con número de página como clave y texto como valor
                         Ejemplo: {1: "texto página 1", 2: "texto página 2"}
  
  Returns:
    dict: Diccionario con clasificaciones por página
          Ejemplo: {1: {clasificación_página_1}, 2: {clasificación_página_2}}
  """
  clasificaciones = {}
  
  for num_pagina, texto_pagina in paginas_texto.items():
    
    # Crear prompt específico para cada página
    prompt = f"""
    Eres un asistente de clasificación documental para una entidad importante. Tu tarea consiste en analizar el siguiente texto de la página {num_pagina} de un documento para identificar y clasificar la información clave.
    
    Texto de la página {num_pagina} a analizar: 
    {texto_pagina}
    
    Extrae y clasifica la siguiente información según los parámetros de un Sistema de Gestión y Archivo (SGDEA): 
    1. **Unidad administrativa:** Identifica el área o departamento responsable (por ejemplo, 'Secretaria de Hacienda', 'Departamento de Tránsito'). Si no se menciona, usa 'Sin especificar'.
    2. **Asunto:** Resume el tema principal de esta página en no más de 10 palabras.
    3. **Serie documental:** Basándote en el contenido, clasifica la información en una de las siguientes categorías: 'Peticiones', 'Quejas', 'Reclamos', 'Sugerencias', 'Felicitaciones'. Si no aplica, usa 'Otros'.
    4. **Subserie documental:** Ofrece una subcategoría más específica para la serie (por ejemplo, para 'Peticiones', podría ser 'Trámites de Licencia'). Si no se puede determinar, usa 'General'.
    5. **Tipología documental:** Identifica el tipo de documento (ej. 'Solicitud de información', 'Oficio', 'Carta'). Si no se puede, usa 'Carta'.
    6. **Metadatos:** Extrae palabras clave o frases relevantes que describan el contenido de esta página (por ejemplo, 'licencia de construcción', 'demora en proceso').
    7. **Número de página:** {num_pagina}
    8. **Contenido relevante:** Indica si esta página contiene información sustancial ('Sí') o es principalmente formato/encabezados ('No').
    
    Proporciona la respuesta únicamente en formato JSON. El JSON debe tener la siguiente estructura:
    {{
      "pagina": {num_pagina},
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
        clasificaciones[num_pagina] = clasificacion_json
      except json.JSONDecodeError:
        clasificaciones[num_pagina] = {"error": "JSON inválido", "respuesta_raw": respuesta_str}
    
    except Exception as e:
      clasificaciones[num_pagina] = {"error": f"Error en clasificación: {str(e)}"}
  
  return clasificaciones