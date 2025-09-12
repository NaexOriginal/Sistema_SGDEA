import os, io, json, tempfile, threading, time
from typing import Optional, Tuple
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request as GoogleRequest
from ..config.settings import Config

SCOPES = [
    "https://www.googleapis.com/auth/drive.file"
]

class GoogleDriveService:
    def __init__(self):
        self._service = None
        self._creds = None
        self._token_path = os.path.join(tempfile.gettempdir(), "gdrive_oauth_token.json")
        self._upload_lock = threading.Lock()  # Lock para evitar problemas de concurrencia
        # is_configured es calculado dinámicamente

    def _load_oauth_user_creds(self) -> Optional[UserCredentials]:
        try:
            if os.path.exists(self._token_path):
                creds = UserCredentials.from_authorized_user_file(self._token_path, SCOPES)
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(GoogleRequest())
                return creds
        except Exception:
            pass
        return None

    def _save_oauth_user_creds(self, creds: UserCredentials) -> None:
        try:
            with open(self._token_path, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        except Exception:
            pass

    @property
    def is_configured(self) -> bool:
        """Config dinámica solo OAuth: requiere carpeta, CLIENT_ID/SECRET y token presente."""
        require_folder = bool(Config.GOOGLE_DRIVE_FOLDER_ID)
        has_oauth_env = bool(os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET"))
        has_oauth_token = os.path.exists(self._token_path)
        return require_folder and has_oauth_env and has_oauth_token

    def _get_credentials(self):
        # Solo OAuth de usuario: no ejecutar flujo interactivo en servidor
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        if client_id and client_secret:
            creds = self._load_oauth_user_creds()
            if not creds or not creds.valid:
                return None
            return creds
        return None

    def _get_service(self):
        if self._service is None:
            self._creds = self._get_credentials()
            if not self._creds:
                return None
            self._service = build("drive", "v3", credentials=self._creds, cache_discovery=False)
        return self._service

    def upload_pdf(self, file_content: bytes, filename: str) -> Tuple[Optional[str], Optional[str]]:
        # Usar lock para evitar problemas de concurrencia
        with self._upload_lock:
            try:
                print(f"Obteniendo servicio de Google Drive para {filename}")
                svc = self._get_service()
                if not svc:
                    print("Error: No se pudo obtener el servicio de Google Drive")
                    return None, None
                
                metadata = {"name": filename}
                if Config.GOOGLE_DRIVE_FOLDER_ID:
                    metadata["parents"] = [Config.GOOGLE_DRIVE_FOLDER_ID]
                
                media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype="application/pdf", resumable=True)
                
                # Reintentar la subida hasta 3 veces en caso de error
                for attempt in range(3):
                    try:
                        print(f"Intento {attempt + 1} de subida para {filename}")
                        res = svc.files().create(body=metadata, media_body=media, fields="id, webViewLink", supportsAllDrives=True).execute()
                        file_id = res.get("id")
                        drive_url = res.get("webViewLink") or (f"https://drive.google.com/file/d/{file_id}/view" if file_id else None)
                        print(f"Subida exitosa: {filename} -> {file_id}")
                        return file_id, drive_url
                    except Exception as e:
                        print(f"Intento {attempt + 1} de subida falló para {filename}: {str(e)}")
                        if attempt == 2:  # Último intento
                            raise e
                        # Esperar un poco antes del siguiente intento
                        time.sleep(1)
                        # Reinicializar el servicio para el siguiente intento
                        self._service = None
                        self._creds = None
                        svc = self._get_service()
                        if not svc:
                            return None, None
                
                return None, None
            except Exception as e:
                print(f"Error en upload_pdf para {filename}: {str(e)}")
                return None, None

# Instancia única para usar en las rutas
google_drive_service = GoogleDriveService()