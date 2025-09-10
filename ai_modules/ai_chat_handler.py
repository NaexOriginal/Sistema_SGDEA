import os
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extraer_paginas_del_contexto(contexto):
    """Extrae información separada por páginas del contexto"""
    paginas = {}

    # Buscar patrones de separación de páginas
    patron_pagina = r'=== PÁGINA (\d+) ===\n--- Página \d+ \(.*?\) ---\n(.*?)--- Fin Página \d+ ---'
    matches = re.findall(patron_pagina, contexto, re.DOTALL)

    if not matches:
        patron_pagina_old = r'--- Página (\d+).*?---\n(.*?)(?=--- Página|$)'
        matches = re.findall(patron_pagina_old, contexto, re.DOTALL)

    for numero_pagina, contenido in matches:
        paginas[int(numero_pagina)] = contenido.strip()

    if not paginas:
        paginas[1] = contexto

    return paginas

def detectar_pagina_ia(mensaje, paginas_disponibles):
    """IA 1: Detecta el número de página mencionado"""
    lista_paginas = ", ".join([f"página {num}" for num in paginas_disponibles.keys()])

    prompt = f"""Páginas disponibles: {lista_paginas}
Mensaje: "{mensaje}"

Responde SOLO con el número de la página mencionada. Si no se menciona página específica, responde "1"."""

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        numero = int(response.choices[0].message.content.strip())
        return numero if numero in paginas_disponibles else 1
    except:
        return 1

def responder_con_contexto_ia(pregunta, contexto_pagina, numero_pagina):
    """IA 2: Responde usando el contexto de la página específica"""
    prompt = f"""Contexto de la página {numero_pagina}:
{contexto_pagina}

Pregunta: {pregunta}

Responde basándote únicamente en esta información."""

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

def responder_chat(pregunta, contexto):
    """Función principal: 2 IAs especializadas"""
    try:
        # Extraer páginas
        paginas = extraer_paginas_del_contexto(contexto)

        # IA 1: Detectar página
        pagina_numero = detectar_pagina_ia(pregunta, paginas)

        # Obtener contexto de la página
        contexto_pagina = paginas.get(pagina_numero, paginas.get(1, contexto))

        # IA 2: Responder con contexto
        respuesta = responder_con_contexto_ia(pregunta, contexto_pagina, pagina_numero)

        return f"{respuesta} *Información de la página {pagina_numero}*"

    except Exception as e:
        return f"Error: {str(e)}"

def listar_paginas_disponibles(contexto):
    """Lista las páginas disponibles en el contexto"""
    paginas = extraer_paginas_del_contexto(contexto)
    return list(paginas.keys())
