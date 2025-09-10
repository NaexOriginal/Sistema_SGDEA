from flask import Blueprint, jsonify, request
import imaplib
from get_information import conectar_servidor, obtener_contenido_correo

email_bp = Blueprint('email', __name__)

# Variable global para almacenar la conexión IMAP
mail = None

@email_bp.route('/revisar_correo', methods=['POST'])
def revisar_correo():
    global mail
    
    try: 
        if not mail or not mail.state == 'SELECTED':
            mail = conectar_servidor()
            mail.select("INBOX")
            
        # Realizamos la búsqueda
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