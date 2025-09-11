import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def responder_con_contexto_ia(pregunta, contexto_completo):
    """Responde usando todo el contexto disponible"""
    prompt = f"""Contexto completo del documento:
{contexto_completo}

Pregunta: {pregunta}

Responde basándote en toda la información disponible."""

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

def responder_chat(pregunta, contexto):
    """Función principal: Responde usando todo el contexto"""
    try:
        # Responder con todo el contexto
        respuesta = responder_con_contexto_ia(pregunta, contexto)
        return respuesta

    except Exception as e:
        return f"Error: {str(e)}"
