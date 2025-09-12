# Sistema SGDEA - Gestión de Documentos Electrónicos

## 📋 Descripción

El Sistema SGDEA (Sistema de Gestión de Documentos Electrónicos Automatizado) es una aplicación web desarrollada en Flask que permite la recepción, procesamiento y consulta inteligente de documentos PDF. El sistema utiliza inteligencia artificial para extraer, clasificar y analizar el contenido de los documentos, permitiendo realizar consultas conversacionales sobre la información contenida.

## 🚀 Características Principales

### 📄 Gestión de Documentos
- **Recepción de PDFs**: Endpoint API para recibir documentos desde dominios externos
- **Almacenamiento en Google Drive**: Integración automática con Google Drive para almacenamiento seguro
- **Procesamiento Inteligente**: Extracción de texto e imágenes usando OCR y análisis de contenido
- **Clasificación SGDEA**: Clasificación automática de documentos según estándares SGDEA
- **Validación de Seguridad**: Verificación de archivos PDF válidos y control de tamaño

### 🤖 Chat Inteligente
- **Consultas Conversacionales**: Sistema de chat para consultar información de los documentos
- **Análisis Contextual**: Respuestas basadas únicamente en el contenido de los documentos procesados
- **Búsqueda Específica**: Localización exacta de información con referencia a páginas específicas
- **Rate Limiting**: Control de frecuencia de consultas para optimizar recursos

### 🔒 Seguridad y Control
- **Validación de Archivos**: Verificación de formato PDF y contenido válido
- **Control de Tamaño**: Límite configurable de tamaño de archivos (50MB por defecto)
- **Registro de Actividad**: Tracking completo de documentos recibidos y procesados
- **Health Check**: Endpoint de monitoreo del estado del sistema

## 🏗️ Arquitectura del Sistema

### Estructura de Directorios
```
Sistema_SGDEA/
├── app.py                          # Aplicación principal Flask
├── requirements.txt                # Dependencias del proyecto
├── .env.example                   # Plantilla de variables de entorno
├── database.db                   # Base de datos SQLite
├── src/
│   ├── config/
│   │   └── settings.py           # Configuración centralizada
│   ├── routes/
│   │   ├── pdf_reception_routes.py  # Rutas para recepción de PDFs
│   │   └── chat_routes.py           # Rutas para funcionalidades de chat
│   ├── services/
│   │   ├── pdf_processor_service.py # Procesamiento de documentos
│   │   ├── chat_service.py          # Servicio de chat con IA
│   │   ├── google_drive_service.py  # Integración con Google Drive
│   │   └── document_classifier.py   # Clasificación de documentos
│   ├── database/
│   │   └── models.py                # Modelos de base de datos
│   └── utils/
│       ├── pdf_extractor.py         # Extracción de contenido PDF
│       └── security.py              # Utilidades de seguridad
├── templates/
│   └── index.html                   # Interfaz web principal
└── static/
    ├── css/                         # Estilos CSS
    └── js/                          # JavaScript del frontend
```

### Componentes Principales

#### 🔧 Backend (Flask)
- **app.py**: Aplicación principal con factory pattern
- **Blueprints**: Organización modular de rutas
- **Servicios**: Lógica de negocio separada por responsabilidades
- **Base de Datos**: SQLite con modelos para documentos recibidos y procesados

#### 🎨 Frontend
- **HTML5**: Interfaz responsive con secciones modulares
- **CSS3**: Estilos organizados por componentes
- **JavaScript**: Manejo de eventos y comunicación con API

#### 🤖 Inteligencia Artificial
- **OpenAI GPT**: Procesamiento de lenguaje natural para chat
- **OCR**: Extracción de texto de imágenes en PDFs
- **Clasificación**: Análisis automático de tipo de documento

## 📊 Base de Datos

### Tabla: documentos_recibidos
```sql
CREATE TABLE documentos_recibidos (
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
);
```

### Tabla: documentos_procesados
```sql
CREATE TABLE documentos_procesados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    documento_id INTEGER NOT NULL,
    contenido_json TEXT NOT NULL,
    fecha_procesamiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version_procesamiento TEXT DEFAULT '1.0',
    tiempo_procesamiento_segundos REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (documento_id) REFERENCES documentos_recibidos (id)
);
```

## 🔌 API Endpoints

### Documentos
- `POST /api/upload-pdf` - Recibir y procesar documentos PDF
- `GET /api/document-status/<id>` - Consultar estado de procesamiento
- `GET /api/documents` - Listar documentos con filtros
- `DELETE /api/documents/<id>` - Eliminar documento
- `GET /api/processing-stats` - Estadísticas de procesamiento

### Chat
- `POST /chat/message` - Enviar mensaje al chat inteligente
- `GET /chat/history` - Obtener historial de conversación
- `POST /chat/search` - Búsqueda específica en documentos

### Sistema
- `GET /health` - Health check del sistema
- `GET /api/info` - Información de la API

## ⚙️ Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- Cuenta de Google Drive con API habilitada
- API Key de OpenAI
- Tesseract OCR instalado

### Instalación

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd Sistema_SGDEA
```

2. **Crear entorno virtual**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:
```env
# API Keys
OPENAI_API_KEY=tu_openai_api_key_aqui

# Google Drive
GOOGLE_DRIVE_FOLDER_ID=id_de_tu_carpeta_google_drive
GOOGLE_CLIENT_ID=tu_google_client_id_aqui
GOOGLE_CLIENT_SECRET=tu_google_client_secret_aqui

# Configuración
MAX_FILE_SIZE=52428800
DEBUG=False
FLASK_ENV=development
```

5. **Configurar Google Drive API**
- Crear proyecto en Google Cloud Console
- Habilitar Google Drive API
- Crear credenciales OAuth 2.0
- Descargar archivo de credenciales como `gestion-de-archivos-471817-09c572451328.json`

6. **Ejecutar la aplicación**
```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## 🔧 Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `OPENAI_API_KEY` | Clave API de OpenAI | Requerido |
| `GOOGLE_DRIVE_FOLDER_ID` | ID de carpeta en Google Drive | Requerido |
| `GOOGLE_CLIENT_ID` | Client ID de Google OAuth | Requerido |
| `GOOGLE_CLIENT_SECRET` | Client Secret de Google OAuth | Requerido |
| `MAX_FILE_SIZE` | Tamaño máximo de archivo en bytes | 52428800 (50MB) |
| `DEBUG` | Modo debug de Flask | False |
| `SECRET_KEY` | Clave secreta de Flask | dev-secret-key |

### Configuración de Producción

1. **Cambiar SECRET_KEY**
```env
SECRET_KEY=tu_clave_secreta_super_segura
```

2. **Configurar base de datos externa** (opcional)
```python
# En settings.py, cambiar DATABASE_PATH para usar PostgreSQL/MySQL
```

3. **Configurar servidor web**
```bash
# Usar Gunicorn para producción
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📝 Uso del Sistema

### Subir Documentos
1. Acceder a la interfaz web en `http://localhost:5000`
2. Hacer clic en "📄 Subir PDF"
3. Seleccionar archivo PDF (máximo 50MB)
4. El sistema procesará automáticamente el documento

### Consultar Documentos
1. Los documentos aparecerán en la tabla "📋 Documentos Disponibles"
2. Usar la barra de búsqueda para filtrar documentos
3. Ver estado de procesamiento en tiempo real

### Chat Inteligente
1. Usar la sección de chat para hacer preguntas
2. El sistema responderá basándose únicamente en los documentos procesados
3. Las respuestas incluirán referencias a páginas específicas

## 🔍 Monitoreo y Logs

### Health Check
```bash
curl http://localhost:5000/health
```

### Logs del Sistema
Los logs se muestran en la consola durante la ejecución:
- Recepción de documentos
- Progreso de procesamiento
- Errores y excepciones
- Estado de servicios externos

## 🛠️ Desarrollo

### Estructura de Desarrollo
- **Modular**: Cada funcionalidad en su propio módulo
- **Blueprints**: Rutas organizadas por funcionalidad
- **Servicios**: Lógica de negocio separada
- **Configuración centralizada**: Todas las configuraciones en `settings.py`

### Agregar Nuevas Funcionalidades
1. Crear nuevo servicio en `src/services/`
2. Agregar rutas en `src/routes/`
3. Registrar blueprint en `app.py`
4. Actualizar frontend si es necesario

## 🐛 Solución de Problemas

### Errores Comunes

**Error: "OPENAI_API_KEY no está configurada"**
- Verificar que el archivo `.env` existe
- Confirmar que la variable está correctamente definida

**Error: "Google Drive credentials not found"**
- Verificar que el archivo de credenciales existe
- Confirmar permisos de la aplicación en Google Cloud

**Error: "File too large"**
- Verificar tamaño del archivo (máximo 50MB por defecto)
- Ajustar `MAX_FILE_SIZE` en `.env` si es necesario

**Error de base de datos**
- Verificar permisos de escritura en el directorio
- Eliminar `database.db` para recrear la base de datos

## 📚 Dependencias Principales

- **Flask**: Framework web
- **OpenAI**: API de inteligencia artificial
- **Google API Client**: Integración con Google Drive
- **PyMuPDF**: Procesamiento de archivos PDF
- **Tesseract**: OCR para extracción de texto
- **SQLite**: Base de datos
- **python-dotenv**: Gestión de variables de entorno

---

**Versión**: 2.0.0  
**Última actualización**: Enero 2025  
**Desarrollado con**: Flask, OpenAI, Google Drive API
        