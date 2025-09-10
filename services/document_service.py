import io
from docx import Document

def extraer_texto_docx(file_data):
    """
    Extrae texto de un documento Word (.docx) usando python-docx.
    
    Args:
        file_data (bytes): Datos binarios del archivo DOCX
        
    Returns:
        str: Texto extraído del documento
    """
    texto_extraido = ""
    
    try:
        # Abrir el documento desde los datos binarios
        doc = Document(io.BytesIO(file_data))
        
        # Extraer texto de cada párrafo
        for para in doc.paragraphs:
            texto_extraido += para.text + "\n"
            
    except Exception:
        return ""
        
    return texto_extraido

def es_formato_docx(extension):
    """
    Verifica si la extensión del archivo corresponde a un documento Word.
    
    Args:
        extension (str): Extensión del archivo (ej: '.docx')
        
    Returns:
        bool: True si el formato es DOCX, False en caso contrario
    """
    return extension.lower() == '.docx'