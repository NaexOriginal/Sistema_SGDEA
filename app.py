from flask import Flask, render_template, jsonify, request
from mysql_conection import conectar_db, buscar_expediente, insertar_documento
from get_information import conectar_servidor, obtener_contenido_correo
from openai_classifier import clasificarcion_openai
from get_documents import extraer_texto_archivo
from werkzeug.utils import secure_filename
from spacy_nlp import extraer_entidades
import imaplib
import json
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
  
  if 'adjuntos' in request.files:
    archivos = request.files.getlist('adjuntos')
    for archivo in archivos:
      if archivo.filename != '':
        filename = secure_filename(archivo.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        archivo.save(filepath)
        
        with open(filepath, 'rb') as f:
          file_data = f.read()
          
        adjuntos_detectados.append(filename)
        adjuntos_texto += extraer_texto_archivo(filename, file_data)
        
        os.remove(filepath)
        
  #* 3. Combinar todo el texto para el procesamiento NLP
  texto_total = cuerpo_mensaje + "\n\n" + adjuntos_texto  
  info_clave_spacy = extraer_entidades(texto_total)
  
  #* Obtener el JSON como texto (string)
  clasificacion_documental_json = clasificarcion_openai(texto_total)

  #* 4. Lógica de búsqueda y almacenamiento en la base de datos
  expediente_encontrado = None
  resultado_asignacion = {}
  
  conn = conectar_db()
  
  #* Se define una variable para el diccionario de clasificacion para evitar el NameError
  clasificacion_documental_dict = None

  if conn:
    try:
      if clasificacion_documental_json:
        #* Parseamos el JSON a un diccionario para poder acceder a los metadatos
        clasificacion_documental_dict = json.loads(clasificacion_documental_json)
        metadatos_documento = clasificacion_documental_dict.get('metadatos', [])
        
        expediente_encontrado = buscar_expediente(conn, metadatos_documento)
      
      #* 5. Preparar el resultado y guardar si es necesario
      if expediente_encontrado:
        resultado_asignacion['estado'] = "Expediente encontrado y asignado"
        resultado_asignacion['expediente_id'] = expediente_encontrado.get('id')
          
      else:
        resultado_asignacion['estado'] = "Documento enviado a bandeja de pendientes"
        #* Pasamos el JSON como texto (string) a la función de inserción
        insertar_documento(conn, asunto, cuerpo_mensaje, clasificacion_documental_json)
    
    except json.JSONDecodeError as e:
      print(f"Error al procesar el JSON de OpenAI: {e}")
      resultado_asignacion['estado'] = "Error de procesamiento"
      resultado_asignacion['detalles'] = str(e)
        
    finally:
      if conn:
        conn.close()
  else:
    resultado_asignacion['estado'] = "Error de conexión con la base de datos"
    
  return jsonify({
    "status": "success",
    "cuerpo_mensaje": cuerpo_mensaje,
    "adjuntos_detectados": adjuntos_detectados,
    "texto_extraido": texto_total,
    "informacion_clave_spacy": info_clave_spacy,
    "clasificacion_openai": clasificacion_documental_dict,
    "resultado_asignacion": resultado_asignacion
  })
  
if __name__ == '__main__':
  app.run(debug=True)