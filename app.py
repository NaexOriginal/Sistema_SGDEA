from flask import Flask, render_template, jsonify, request
from get_information import conectar_servidor, obtener_contenido_correo
from openai_classifier import clasificarcion_openai
from get_documents import extraer_texto_archivo
from werkzeug.utils import secure_filename
import imaplib
import datetime
import os

app = Flask(__name__)

#* Directorio donde se guardan los archivos
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
  os.makedirs(UPLOAD_FOLDER)
  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#* Definimos una variable global para la conexión IMAP
mail = None

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/revisar_correo', methods=['POST'])
def revisar_correo():
  global mail
  
  try: 
    if not mail or not mail.state == 'SELECTED':
      mail = conectar_servidor()
      mail.select("INBOX")
      
    #* Realizamos la búsqueda
    resp, items = mail.search(None, 'ALL', 'SINCE 20-Aug-2025', 'X-GM-RAW "Category:Primary"')
    email_ids = items[0].split()
    
    
    if email_ids:
      latest_email_id = email_ids[-1]
      datos_correo = obtener_contenido_correo(mail, latest_email_id)
      mail.store(latest_email_id, '+FLAGS', r'\Seen')
      
      return jsonify({
        "status": "success",
        "message": "Nuevo correo detectado y procesado",
        "data": datos_correo
      })
      
    else:
      return jsonify({
        "status": "info",
        "message": "No se encontraron correos nuevos",
      })
      
  except imaplib.IMAP4.error as e:
    if "command CLOSE illegal in state LOGOUT" in str(e):
      return jsonify({
        "status": "error",
        "message": "Conexión cerrada. Por favor reinicie la aplicación"
      })
    
    else:
      return jsonify({
        "status": "error",
        "message": f"Error de conexión IMAP: {e}"
      })
      
  except Exception as e:
    return jsonify({
      "status": "error",
      "message": f"Ha ocurrido un error inesperado: {str(e)}"
    })
    
@app.route('/procesar_formulario', methods=['POST'])
def procesar_formulario():
  #* 1. Obtenemos la información del formulario
  asunto = request.form.get('asunto', '')
  cuerpo_mensaje = request.form.get('cuerpo_mensaje', '')
  
  #* 2. Manejar los archivos adjuntos
  adjuntos_texto = ""
  adjuntos_detectados = []
  
  if 'archivo' in request.files:
    archivos = request.files.getlist('archivo')
    for archivo in archivos:
      if archivo.filename != '':
        #* Usar secure_filename para evitar problemas de seguridad
        filename = secure_filename(archivo.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        archivo.save(filepath)
        
        #* Leer el archivo y procesarlo con la función
        with open(filepath, 'rb') as f:
          file_data = f.read()
          
        adjuntos_detectados.append(filename)
        adjuntos_texto += extraer_texto_archivo(filename, file_data)
        
        #* Opcional: Eliminar el archivo después de procesarlo
        os.remove(filepath)
        
  #* 3. Combinar todo el texto para el procesamiento NLP
  texto_total = cuerpo_mensaje + "\n\n" + adjuntos_texto
  
  #* Aquí puedes llamar a tu función de NLP para extraer la información
  from spacy_nlp import extraer_entidades
  info_clave = extraer_entidades(texto_total)
  
  #* Paso extra: Usar OpenAI para la clasificación de archivos (No funciona debido a la API)
  clasificacion_documental = clasificarcion_openai(texto_total)

  #* 4. Devolver una respuesta JSON con el resultado
  return jsonify({
    "status": "success",
    "cuerpo": cuerpo_mensaje,
    "adjuntos_detectados": adjuntos_detectados,
    "texto_extraido": texto_total,
    "informacion_clave": info_clave,
    "clasifiacion_documental_openai": clasificacion_documental
  })

if __name__ == '__main__':
  app.run(debug=True)