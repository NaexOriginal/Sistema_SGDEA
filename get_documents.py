import os
import io
import fitz
import pytesseract
from PIL import Image
from docx import Document

def extraer_texto_archivo(filename, file_data):
  texto_extraido = ""
  #* Extrae texto de un archivo PDF, DOCX o imagen
  extension = os.path.splitext(filename)[1].lower()
  
  if extension == ".pdf":
    try:
      doc = fitz.open(stream = file_data, filetype="pdf")
      for page in doc:
        texto_extraido += page.get_text()
      doc.close()
      
    except Exception as e:
      print(f"Error al leer el PDF: {e}")
      
  elif extension == ".docx":
    try:
      doc = Document(io.BytesIO(file_data))
      for para in doc.paragraphs:
        texto_extraido += para.text + "\n"
    
    except Exception as e:
      print(f"Error al leer el DOCX: {e}")
      
  elif extension in [".png", ".jpg", "jpeg"]:
    try:
      image = Image.open(io.BytesIO(file_data))
      texto_extraido = pytesseract.image_to_string(image)
      
    except Exception as e:
      print(f"El error al leer la imagen: {e}")
      
  return texto_extraido