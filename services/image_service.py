import io
import pytesseract
from PIL import Image

# Configurar el PATH de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extraer_texto_imagen(file_data):
    """
    Extrae texto de una imagen usando OCR (pytesseract).
    Soporta formatos: PNG, JPG, JPEG
    
    Args:
        file_data (bytes): Datos binarios del archivo de imagen
        
    Returns:
        str: Texto extraído de la imagen
    """
    texto_extraido = ""
    
    try:
        # Abrir la imagen desde los datos binarios
        image = Image.open(io.BytesIO(file_data))
        
        # Configuración personalizada para mejorar el OCR
        # --psm 6: Asume un bloque uniforme de texto
        # -l eng: Idioma inglés (viene por defecto con Tesseract)
        custom_config = r'--oem 3 --psm 6 -l eng'
        
        # Extraer texto usando OCR con configuración personalizada
        texto_extraido = pytesseract.image_to_string(image, config=custom_config)
        
        # Si no se extrae texto, intentar con configuración automática
        if not texto_extraido.strip():
            custom_config = r'--oem 3 --psm 3'
            texto_extraido = pytesseract.image_to_string(image, config=custom_config)
            
    except Exception:
        return ""
        
    return texto_extraido

def es_formato_imagen_soportado(extension):
    """
    Verifica si la extensión del archivo corresponde a un formato de imagen soportado.
    
    Args:
        extension (str): Extensión del archivo (ej: '.png', '.jpg')
        
    Returns:
        bool: True si el formato es soportado, False en caso contrario
    """
    formatos_soportados = ['.png', '.jpg', '.jpeg']
    return extension.lower() in formatos_soportados