from flask import Flask, render_template, jsonify, request
import os
import sys
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar configuración
from src.config.settings import Config

# Importar blueprints
from src.routes.pdf_reception_routes import pdf_reception_bp
from src.routes.chat_routes import chat_bp

# Importar base de datos
from src.database.models import db_manager

def create_app():
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Configurar la aplicación
    app.config.update({
        'MAX_CONTENT_LENGTH': Config.MAX_FILE_SIZE,
        'SECRET_KEY': Config.SECRET_KEY or 'dev-secret-key-change-in-production',
        # 'UPLOAD_FOLDER' eliminado: no se guardan archivos en local
    })
    
    # Inicializar base de datos
    try:
        db_manager.init_database()
        print("Base de datos inicializada correctamente")
    except Exception as e:
        print(f"Error inicializando base de datos: {e}")
    
    # Crear directorios necesarios
    Config.create_directories()
    
    # Registrar blueprints
    app.register_blueprint(pdf_reception_bp)
    app.register_blueprint(chat_bp)
    # app.register_blueprint(auth_bp)  # eliminado: no se usan rutas OAuth
    
    # Rutas principales
    @app.route('/')
    def index():
        """Página principal"""
        return render_template('index.html')
    
    @app.route('/health')
    def health_check():
        """Endpoint de health check"""
        try:
            # Verificar conexión a base de datos
            db_status = db_manager.test_connection()
            
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'database': 'connected' if db_status else 'disconnected',
                'version': '2.0.0'
            })
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    @app.route('/api/info')
    def api_info():
        """Información de la API"""
        return jsonify({
            'name': 'Sistema de Procesamiento de PDFs',
            'version': '2.0.0',
            'description': 'API para recepción y procesamiento de documentos PDF',
            'endpoints': {
                'pdf_upload': '/pdf/upload',
                'pdf_status': '/pdf/status/<document_id>',
                'pdf_list': '/pdf/list',
                'pdf_stats': '/pdf/stats',
                'chat_message': '/chat/message',
                'chat_history': '/chat/history',
                'chat_search': '/chat/search',
                'health': '/health'
            },
            'max_file_size': Config.MAX_FILE_SIZE
        })
    
    # Manejadores de errores
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Endpoint no encontrado',
            'code': 'NOT_FOUND',
            'timestamp': datetime.now().isoformat()
        }), 404
    
    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({
            'error': f'Archivo demasiado grande. Máximo permitido: {Config.MAX_FILE_SIZE // (1024*1024)}MB',
            'code': 'FILE_TOO_LARGE',
            'timestamp': datetime.now().isoformat()
        }), 413
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Error interno del servidor',
            'code': 'INTERNAL_ERROR',
            'timestamp': datetime.now().isoformat()
        }), 500
    
    # Middleware para logging
    @app.before_request
    def log_request_info():
        """Log información de requests"""
        if not request.path.startswith('/static'):
            print(f"[{datetime.now()}] {request.method} {request.path} - {request.remote_addr}")

    # CORS básico: permitir cualquier origen para métodos comunes
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin')
        response.headers['Access-Control-Allow-Origin'] = origin or '*'
        response.headers['Vary'] = 'Origin'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,DELETE,OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    # Soporte a preflight en endpoints /api
    @app.route('/api/<path:any_path>', methods=['OPTIONS'])
    def cors_preflight(any_path):
        return ('', 204)
    
    return app

# Crear instancia de la aplicación
app = create_app()

if __name__ == '__main__':
    # Configuración para desarrollo
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"Iniciando servidor en puerto {port}...")
    print(f"Modo debug: {debug}")
    print(f"Directorio de trabajo: {os.getcwd()}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )