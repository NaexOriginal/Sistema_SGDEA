import os
from openai import OpenAI
import json
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
  api_key = os.getenv("OPENAI_API_KEY")
)

def clasificarcion_openai(texto_completo):
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
    response = client.responses.create(
      model="gpt-5-nano",
      input=[
        {"role": "system", "content": "Eres un asistente de ayuda"},
        {"role": "user", "content": prompt}
      ]
    )
    
    respuesta_str = response.output_text
    return respuesta_str
  
  except Exception as e:
    print(f"Error al llamar a la API de OpenAI: {e}")
    return None
  

# print(clasificarcion_openai("""CURSO DE PROGRAMACION Y DESARROLLO DE PROGRAMAS FULL STACK :
# Estarás en la capacidad de aportar en la operación y emprender de los negocios de desarrollo de aplicaciones, web o sitios; diseño y creación de programas en la web y administración de bases de datos. Basándote en las buenas prácticas de Desarrollo de Software para cumplir con los estándares de alta calidad, las nuevas tendencias de desarrollo de software que implican implementar diseño, metodologías, modelos y arquitecturas; lenguajes de programación, para implementar aplicativos en: Python, JAVA, C# (sharp), PHP, HTML5 y CSS3, y sus versiones posteriores, diseño de sitios web, técnicas de diseño, herramientas para alojar y posicionar el sitio en un servidor: metodologías de desarrollo (SCRUM, RUP, XP) y el modelamiento, administración, diseño y análisis de la información usando administradores de bases de datos como: SQL, MySQL, mariadb, Oracle.

# CONTENIDO ACADEMICO:

# Programación: aprenderás todos los framework sobre:
# Estructuras de datos, Mi primer desarrollo en Windows, ,Mi primer desarrollo MAC, Mi primer desarrollo en Linux, Arquitectura cliente/servidor, Backend NodeJS y NPM, Lineas de Comando Servidor web, JSP,Fundamentos de Python, Estructura de datos con python,funciones Php con composer C# con .NET 3.1
# Programacion en Bash Shell ingenieria de software, Redes de internet Bases de datos, SQL básico y mucho más.

# ANALISIS DE DATOS:

# Uso básico de las hojas de cálculo.
# Hojas de cálculo como herramienta para la preparación de datos.
# Manejo de repositorios. 
# Fundamentos de programación en Python.
# Fundamentos de bases de datos.
# Fundamentos de estadística. 
# Introducción al análisis de datos. 
# Visualización con MatplotLib. 
# Dataframes con pandas. 
# Aprendizaje automático. 
# Procesamiento de lenguaje natural.
# Duración:
# 8 meses

# Frecuencia semanal:
# Son 3 encuentros de 2 horas que puedes programar en plataforma según tu horario, donde encontrarías la disponibilidad de un profesor que te asistirá en todo tiempo.
#  El contenido, los talleres y laboratorios son videos asistidos que quedan habilitados durante 12 meses.
# La carga horaria está compuesta por:
# * Prácticas individuales y de pares que serán guiadas fuera de clase por tu tutor asignado, adicional a esto contamos con la biblioteca Pearson educations.
# * El consumo del material adicional de estudio en la plataforma LULOPY, donde encontrarás el contenido de lectura, videos y exámenes.

# Modalidad:
# Online - virtual.

# Grupos reducidos:
# Promedio 25 personas.

# Hardware:
# Solo necesitarás una computadora con al menos 8GB de memoria RAM y un microprocesador Intel Core i3 en adelante.
# Recuerda también auriculares y cámara para que puedas comunicarte con el tutor y tus compañeros."""))