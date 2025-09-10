import io
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

# Configurar el PATH de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extraer_texto_pdf(file_data):
    """
    Extrae texto de un archivo PDF. Detecta automáticamente si el PDF contiene
    texto extraíble o si son imágenes que requieren OCR.
    
    Args:
        file_data (bytes): Datos binarios del archivo PDF
        
    Returns:
        str: Texto extraído del PDF
    """
    texto_extraido = ""
    
    try:
        # Abrir el PDF desde los datos binarios
        doc = fitz.open(stream=file_data, filetype="pdf")
        
        # Intentar extraer texto de cada página
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            texto_pagina = page.get_text().strip()
            
            # Si la página tiene texto extraíble, usarlo
            if texto_pagina:
                texto_extraido += f"\n=== PÁGINA {page_num + 1} ===\n"
                texto_extraido += f"--- Página {page_num + 1} (Texto Extraído) ---\n"
                texto_extraido += texto_pagina.strip() + "\n"
                texto_extraido += f"--- Fin Página {page_num + 1} ---\n\n"
            else:
                # Si no hay texto, la página probablemente contiene solo imágenes
                texto_ocr = extraer_texto_con_ocr_desde_pagina(page, page_num + 1)
                if texto_ocr.strip():
                    texto_extraido += f"\n=== PÁGINA {page_num + 1} ===\n"
                    texto_extraido += f"--- Página {page_num + 1} (OCR) ---\n"
                    texto_ocr = texto_ocr.strip()
                    texto_extraido += texto_ocr + "\n"
                    texto_extraido += f"--- Fin Página {page_num + 1} ---\n\n"
                else:
                    texto_extraido += f"\n=== PÁGINA {page_num + 1} ===\n"
                    texto_extraido += f"--- Página {page_num + 1} (Sin texto detectado) ---\n"
                    texto_extraido += "[Esta página no contiene texto legible]\n"
                    texto_extraido += f"--- Fin Página {page_num + 1} ---\n\n"
            
        # Cerrar el documento
        doc.close()
        
    except Exception as e:
        return ""
        
    return texto_extraido

def extraer_texto_con_ocr_desde_pagina(page, page_num):
    """
    Extrae texto de una página PDF usando OCR.
    
    Args:
        page: Objeto página de PyMuPDF
        page_num (int): Número de página para logging
        
    Returns:
        str: Texto extraído mediante OCR
    """
    try:
        # Convertir la página a imagen
        mat = fitz.Matrix(2.0, 2.0)  # Escalar 2x para mejor calidad OCR
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        
        # Convertir a PIL Image
        image = Image.open(io.BytesIO(img_data))
        
        # Configuración OCR optimizada para documentos
        custom_config = r'--oem 3 --psm 6 -l spa+eng'  # Español e inglés
        
        # Extraer texto usando OCR
        texto_ocr = pytesseract.image_to_string(image, config=custom_config)
        
        # Si no se extrae texto con la configuración inicial, probar otra
        if not texto_ocr.strip():
            custom_config = r'--oem 3 --psm 3 -l spa+eng'
            texto_ocr = pytesseract.image_to_string(image, config=custom_config)
            
        return texto_ocr
        
    except Exception:
        return ""

def detectar_tipo_pdf(file_data):
    """
    Detecta si un PDF contiene principalmente texto extraíble o imágenes.
    
    Args:
        file_data (bytes): Datos binarios del archivo PDF
        
    Returns:
        dict: Información sobre el tipo de contenido del PDF
    """
    try:
        doc = fitz.open(stream=file_data, filetype="pdf")
        
        total_paginas = len(doc)
        paginas_con_texto = 0
        paginas_con_imagenes = 0
        
        for page_num in range(total_paginas):
            page = doc.load_page(page_num)
            texto = page.get_text().strip()
            imagenes = page.get_images()
            
            if texto:
                paginas_con_texto += 1
            if imagenes:
                paginas_con_imagenes += 1
                
        doc.close()
        
        return {
            "total_paginas": total_paginas,
            "paginas_con_texto": paginas_con_texto,
            "paginas_con_imagenes": paginas_con_imagenes,
            "tipo_predominante": "texto" if paginas_con_texto > paginas_con_imagenes else "imagenes"
        }
        
    except Exception as e:
        return {"error": str(e)}