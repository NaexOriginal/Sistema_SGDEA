import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from ..config.settings import Config

class DatabaseManager:
    """Gestor de base de datos SQLite"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_database()
    
    def get_connection(self):
        """Obtiene una conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
        return conn
    
    def init_database(self):
        """Inicializa las tablas de la base de datos"""
        with self.get_connection() as conn:
            # Tabla de documentos recibidos
            conn.execute('''
                CREATE TABLE IF NOT EXISTS documentos_recibidos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_pdf TEXT NOT NULL,
                    url_google_drive TEXT NOT NULL,
                    fecha_hora_recepcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    dominio_origen TEXT NOT NULL,
                    estado_procesamiento TEXT DEFAULT 'pendiente',
                    tamano_archivo INTEGER,
                    hash_archivo TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de documentos procesados
            conn.execute('''
                CREATE TABLE IF NOT EXISTS documentos_procesados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    documento_id INTEGER NOT NULL,
                    contenido_json TEXT NOT NULL,
                    fecha_procesamiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    version_procesamiento TEXT DEFAULT '1.0',
                    tiempo_procesamiento_segundos REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (documento_id) REFERENCES documentos_recibidos (id)
                )
            ''')
            
            # Índices para mejorar rendimiento
            conn.execute('CREATE INDEX IF NOT EXISTS idx_documentos_recibidos_fecha ON documentos_recibidos(fecha_hora_recepcion)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_documentos_recibidos_dominio ON documentos_recibidos(dominio_origen)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_documentos_recibidos_estado ON documentos_recibidos(estado_procesamiento)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_documentos_procesados_documento_id ON documentos_procesados(documento_id)')
            
            conn.commit()

class DocumentoRecibido:
    """Modelo para documentos recibidos"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def crear(self, nombre_pdf: str, url_google_drive: str, dominio_origen: str, 
              tamano_archivo: int = None, hash_archivo: str = None) -> int:
        """Crea un nuevo registro de documento recibido"""
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO documentos_recibidos 
                (nombre_pdf, url_google_drive, dominio_origen, tamano_archivo, hash_archivo)
                VALUES (?, ?, ?, ?, ?)
            ''', (nombre_pdf, url_google_drive, dominio_origen, tamano_archivo, hash_archivo))
            return cursor.lastrowid
    
    def obtener_por_id(self, documento_id: int) -> Optional[Dict]:
        """Obtiene un documento por su ID"""
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM documentos_recibidos WHERE id = ?', 
                (documento_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def actualizar_estado(self, documento_id: int, estado: str) -> bool:
        """Actualiza el estado de procesamiento de un documento"""
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                UPDATE documentos_recibidos 
                SET estado_procesamiento = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (estado, documento_id))
            return cursor.rowcount > 0
    
    def listar_pendientes(self) -> List[Dict]:
        """Lista todos los documentos pendientes de procesamiento"""
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM documentos_recibidos WHERE estado_procesamiento = 'pendiente' ORDER BY fecha_hora_recepcion"
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def listar_por_dominio(self, dominio: str) -> List[Dict]:
        """Lista documentos por dominio de origen"""
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM documentos_recibidos WHERE dominio_origen = ? ORDER BY fecha_hora_recepcion DESC',
                (dominio,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def listar_todos(self, limite: int = 50, offset: int = 0) -> List[Dict]:
        """Lista todos los documentos con paginación"""
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM documentos_recibidos ORDER BY fecha_hora_recepcion DESC LIMIT ? OFFSET ?',
                (limite, offset)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def listar_por_estado(self, estado: str) -> List[Dict]:
        """Lista documentos por estado de procesamiento"""
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM documentos_recibidos WHERE estado_procesamiento = ? ORDER BY fecha_hora_recepcion DESC',
                (estado,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def eliminar(self, documento_id: int) -> bool:
        """Elimina un documento y sus datos procesados asociados"""
        with self.db.get_connection() as conn:
            # Primero eliminar los datos procesados asociados
            conn.execute(
                'DELETE FROM documentos_procesados WHERE documento_id = ?',
                (documento_id,)
            )
            
            # Luego eliminar el documento principal
            cursor = conn.execute(
                'DELETE FROM documentos_recibidos WHERE id = ?',
                (documento_id,)
            )
            
            return cursor.rowcount > 0

class DocumentoProcesado:
    """Modelo para documentos procesados"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def crear(self, documento_id: int, contenido_json: Dict[str, Any], 
              tiempo_procesamiento: float = None, version: str = '1.0') -> int:
        """Crea un nuevo registro de documento procesado"""
        contenido_str = json.dumps(contenido_json, ensure_ascii=False, indent=2)
        
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO documentos_procesados 
                (documento_id, contenido_json, version_procesamiento, tiempo_procesamiento_segundos)
                VALUES (?, ?, ?, ?)
            ''', (documento_id, contenido_str, version, tiempo_procesamiento))
            return cursor.lastrowid
    
    def obtener_por_documento_id(self, documento_id: int) -> Optional[Dict]:
        """Obtiene el procesamiento más reciente de un documento"""
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT dp.*, dr.nombre_pdf, dr.dominio_origen, dr.fecha_hora_recepcion
                FROM documentos_procesados dp
                JOIN documentos_recibidos dr ON dp.documento_id = dr.id
                WHERE dp.documento_id = ? 
                ORDER BY dp.fecha_procesamiento DESC 
                LIMIT 1
            ''', (documento_id,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['contenido_json'] = json.loads(result['contenido_json'])
                return result
            return None
    
    def buscar_en_contenido(self, termino_busqueda: str) -> List[Dict]:
        """Busca documentos que contengan un término específico en su contenido JSON"""
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT dp.*, dr.nombre_pdf, dr.dominio_origen, dr.fecha_hora_recepcion
                FROM documentos_procesados dp
                JOIN documentos_recibidos dr ON dp.documento_id = dr.id
                WHERE dp.contenido_json LIKE ?
                ORDER BY dp.fecha_procesamiento DESC
            ''', (f'%{termino_busqueda}%',))
            
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                result['contenido_json'] = json.loads(result['contenido_json'])
                results.append(result)
            return results
    
    def obtener_todos_procesados(self) -> List[Dict]:
        """Obtiene todos los documentos procesados con información básica"""
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT dp.documento_id, dp.fecha_procesamiento, dp.version_procesamiento,
                       dr.nombre_pdf, dr.dominio_origen, dr.fecha_hora_recepcion
                FROM documentos_procesados dp
                JOIN documentos_recibidos dr ON dp.documento_id = dr.id
                ORDER BY dp.fecha_procesamiento DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]

# Instancia global del gestor de base de datos
db_manager = DatabaseManager()
documento_recibido = DocumentoRecibido(db_manager)
documento_procesado = DocumentoProcesado(db_manager)