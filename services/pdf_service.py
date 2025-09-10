import io
import fitz  # PyMuPDF

def extraer_texto_pdf(file_data):
    """
    Extrae texto de un archivo PDF usando PyMuPDF.
    
    Args:
        file_data (bytes): Datos binarios del archivo PDF
        
    Returns:
        str: Texto extraído del PDF
    """
    texto_extraido = ""
    
    try:
        # Abrir el PDF desde los datos binarios
        doc = fitz.open(stream=file_data, filetype="pdf")
        
        # Extraer texto de cada página
        for page in doc:
            texto_extraido += page.get_text()
            
        # Cerrar el documento
        doc.close()
        
    except Exception as e:
        print(f"Error al leer el PDF: {e}")
        return ""
        
    return texto_extraido