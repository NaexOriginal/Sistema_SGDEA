# Módulo compartido para el contexto del documento

# Variable global para almacenar el contexto del documento
documento_contexto = {
    "texto": "",
    "analisis": [],
    "paginas": {},  # Nueva estructura para páginas separadas
    "total_paginas": 0,
    "disponible": False
}

def get_documento_contexto():
    """Obtener el contexto del documento"""
    global documento_contexto
    return documento_contexto

def set_documento_contexto(nuevo_contexto):
    """Actualizar el contexto del documento"""
    global documento_contexto
    documento_contexto.update(nuevo_contexto)