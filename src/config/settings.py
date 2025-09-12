import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración centralizada del sistema"""
    
    # Base de datos
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database.db')
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = 'gpt-5-nano'
    
    # Google Drive
    GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    GOOGLE_DRIVE_CREDENTIALS_FILE = os.getenv('GOOGLE_DRIVE_CREDENTIALS_FILE', 'gestion-de-archivos-471817-09c572451328.json')
    # Eliminado GOOGLE_DRIVE_TOKEN_FILE: tokens se guardan temporalmente por el servicio
    
    # Seguridad
    ALLOWED_DOMAINS = os.getenv('ALLOWED_DOMAINS', '').split(',') if os.getenv('ALLOWED_DOMAINS') else []
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50 * 1024 * 1024))  # 50MB por defecto
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    @classmethod
    def validate_config(cls):
        """Valida que las configuraciones críticas estén presentes"""
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY no está configurada")
            
        if not cls.GOOGLE_DRIVE_CREDENTIALS_FILE or not os.path.exists(cls.GOOGLE_DRIVE_CREDENTIALS_FILE):
            errors.append("GOOGLE_DRIVE_CREDENTIALS_FILE no existe")
            
        if not cls.GOOGLE_DRIVE_FOLDER_ID:
            errors.append("GOOGLE_DRIVE_FOLDER_ID no está configurada")
            
        return errors
    
    @classmethod
    def create_directories(cls):
        """Crea los directorios necesarios si no existen"""
        os.makedirs(os.path.dirname(cls.DATABASE_PATH), exist_ok=True)