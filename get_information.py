import os
import time
import email
import pickle
import imaplib
import datetime
from dotenv import load_dotenv
from email.header import decode_header
from get_documents import extraer_texto_archivo
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

SCOPES = ['https://mail.google.com/']
EMAIL_ADDRESS = "rafaelpiedrahita414@gmail.com"


#* El token de autenticación se guarda en este archivo
TOKEN_FILE = 'token.pickle'
CREDENTIALS_FILE = 'credentials.json'

def get_gmail_credentials():
  creds = None
  
  if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, 'rb') as token:
      creds = pickle.load(token)
      
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_FILE, SCOPES
      )
      creds = flow.run_local_server(port=0)
      
    with open(TOKEN_FILE, 'wb') as token:
      pickle.dump(creds, token)
  
  return creds


def get_imap_token(email_address):
  creds = get_gmail_credentials()
  auth_string = f'user={ email_address }\x01auth=Bearer {creds.token}\x01\x01'
  return auth_string

#* 1. Generamos la conexión con el Servidor de Correo
def conectar_servidor():
  mail = imaplib.IMAP4_SSL("imap.gmail.com")
  
  #* Usa el token OAuth en lugar de la contraseña
  token = get_imap_token(EMAIL_ADDRESS)
  
  mail.authenticate('XOAUTH2', lambda x: token)
  return mail

#* 2. Extraemos y Decodigicamos el mensaje
def obtener_contenido_correo(mail, email_id):
  resp, data = mail.fetch(email_id, "(RFC822)")
  raw_email = data[0][1]
  msg = email.message_from_bytes(raw_email)

  #* Encabezados
  remitente, asunto, fecha = "N/A", "N/A", "N/A"
  
  if msg["From"]:
    remitente, _ = decode_header(msg["From"])[0]
    if isinstance(asunto, bytes):
      remitente = remitente.decode()
  
  if msg["Subject"]:
    asunto, encoding = decode_header(msg["Subject"])[0]
    if isinstance(asunto, bytes):
      asunto = asunto.decode(encoding if encoding else 'utf-8')
  
  if msg["Date"]:
    fecha = msg["Date"]
    
  print(f"--- Nuevo Correo de { remitente } ---")
  print(f"Asunto: { asunto }")
  print(f"Fecha: { fecha }")
  
  
  #* Cuerpo del mensaje
  cuerpo_plano = ""
  adjuntos_texto = ""
  adjuntos_detectados = []
  
  for part in msg.walk():
    content_type = part.get_content_type()
    content_disposition = str(part.get_content_disposition())
    
    #* Procesamos el cuerpo del correo
    if content_type == "text/plain" and "attachment" not in content_disposition:
      try:
        cuerpo_plano = part.get_payload(decode=True).decode()
      except:
        cuerpo_plano = part.get_payload(decode=True).decode('latin-1')
        
    #* Procesar archivos adjuntos
    if "attachment" in content_disposition:
      filename = part.get_filename()
      
      if filename:
        adjuntos_detectados.append(filename)
        file_data = part.get_payload(decode=True)
        
        #* Extrae,ps eñ textp del archivo adjunto y agregarlo al texto total
        adjuntos_texto += extraer_texto_archivo(filename, file_data)
        
      print("\nCuerpo del mensaje (Texto plano): \n", cuerpo_plano)
      

  texto_total = cuerpo_plano + "\n\n" + adjuntos_texto
  
  print("\nArchivos Adjuntos:")
  if adjuntos_detectados:
    for filename in adjuntos_detectados:
      print(f"- {filename}")
      
  else:
    print("No se encontraron adjuntos")
    
  print("\nTexto Extraído (cuerpo del correo + adjuntos)")
  print(texto_total)
  
  return {
    "remitente": remitente,
    "asunto": asunto,
    "cuerpo": texto_total,
    "fecha": fecha
  }  
  
#* Flujo principal del Script
if __name__ == "__main__":
  mail = None
  
  try:
    mail = conectar_servidor()
    mail.select("INBOX")
    print("Esperando nuvos correos... (Presiona Ctrl+C para salir)")
    
    while True:
      #* Establecemos el rango de fecha
      fecha_semana = (datetime.date.today() - datetime.timedelta(days=7)).strftime("%d-%b-%Y")
      
      resp, items = mail.search(None, 'UNSEEN', 'SINCE 20-Aug-2025', 'X-GM-RAW "Category:Primary"')
      email_ids = items[0].split()
        
      if email_ids:
        #* Procesar solo el último correo no leido
        latest_email_id = email_ids[-1]
        print("Nuevo correo detectado") 
        
        datos_correo = obtener_contenido_correo(mail, latest_email_id)    
        print("-" * 50)
        
        #* Opcional: Marcar el correo como leído para no procesarlo de nuevo
        mail.store(latest_email_id, '+FLAGS', r'\Seen')
          
      else:
        print("No se encontraron correos nuevos. Esperando...")
        
      #* Esperamos 30 segundos antes de volver a revisar
      time.sleep(30)
      
  except (imaplib.IMAP4.abort, imaplib.IMAP4.error) as e:
    print(f"Error de conexión IMAP: {e}. \n\nReconectando...")
    
    #* Lógica para reconectar si la conexión se íerde
    if mail:
      mail.close()
      mail.logout()
      
    time.sleep(30) 
    
  except KeyboardInterrupt:
    print("Proceso terminado por el usuario")  
  
  finally:
    if mail:
      mail.close()
      mail.logout()