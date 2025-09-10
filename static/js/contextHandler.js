/**
 * Manejador de contextos guardados
 * Permite cargar y gestionar contextos desde archivos JSON
 */

class ContextHandler {
    constructor() {
        this.contextoActual = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Botón para mostrar/ocultar panel de contextos
        const toggleBtn = document.getElementById('toggle-context-panel');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggleContextPanel());
        }

        // Botón para cargar archivo JSON
        const loadBtn = document.getElementById('load-context-file');
        if (loadBtn) {
            loadBtn.addEventListener('click', () => this.loadContextFromFile());
        }

        // Botón para refrescar lista de contextos
        const refreshBtn = document.getElementById('refresh-contexts');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadContextList());
        }

        // Input de archivo JSON
        const fileInput = document.getElementById('context-file-input');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
        }
    }

    toggleContextPanel() {
        const panel = document.getElementById('context-panel');
        if (panel) {
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
            if (panel.style.display === 'block') {
                this.loadContextList();
            }
        }
    }

    async loadContextList() {
        try {
            const response = await fetch('/listar_contextos');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.displayContextList(data.contextos);
            } else {
                this.showMessage('Error al cargar lista de contextos: ' + data.mensaje, 'error');
            }
        } catch (error) {
            this.showMessage('Error de conexión al cargar contextos: ' + error.message, 'error');
        }
    }

    displayContextList(contextos) {
        const container = document.getElementById('context-list');
        if (!container) return;

        if (contextos.length === 0) {
            container.innerHTML = '<p class="no-contexts">No hay contextos guardados</p>';
            return;
        }

        const html = contextos.map(contexto => `
            <div class="context-item" data-filename="${contexto.nombre_archivo}">
                <div class="context-header">
                    <h4>${contexto.asunto}</h4>
                    <span class="context-date">${this.formatDate(contexto.timestamp)}</span>
                </div>
                <div class="context-details">
                    <span class="context-attachments">${contexto.adjuntos} adjunto(s)</span>
                    <span class="context-size">${contexto.tamaño_kb} KB</span>
                </div>
                <button class="load-context-btn" onclick="contextHandler.loadContextFromSaved('${contexto.nombre_archivo}')">
                    Cargar Contexto
                </button>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    formatDate(timestamp) {
        if (!timestamp || timestamp === 'Error al leer') return timestamp;
        try {
            const date = new Date(timestamp);
            return date.toLocaleString('es-ES');
        } catch {
            return timestamp;
        }
    }

    async loadContextFromSaved(filename) {
        try {
            const response = await fetch('/cargar_contexto', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ nombre_archivo: filename })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                this.contextoActual = data.contexto_info;
                this.showMessage('Contexto cargado exitosamente: ' + data.contexto_info.asunto, 'success');
                this.updateContextDisplay(data.contexto_info);
                this.toggleContextPanel(); // Cerrar panel después de cargar
            } else {
                this.showMessage('Error al cargar contexto: ' + data.mensaje, 'error');
            }
        } catch (error) {
            this.showMessage('Error de conexión: ' + error.message, 'error');
        }
    }

    loadContextFromFile() {
        const fileInput = document.getElementById('context-file-input');
        if (fileInput) {
            fileInput.click();
        }
    }

    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        if (!file.name.endsWith('.json')) {
            this.showMessage('Por favor selecciona un archivo JSON válido', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('archivo_json', file);

        try {
            const response = await fetch('/cargar_contexto', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                this.contextoActual = data.contexto_info;
                this.showMessage('Contexto cargado desde archivo: ' + data.contexto_info.asunto, 'success');
                this.updateContextDisplay(data.contexto_info);
                this.toggleContextPanel(); // Cerrar panel después de cargar
            } else {
                this.showMessage('Error al cargar archivo: ' + data.mensaje, 'error');
            }
        } catch (error) {
            this.showMessage('Error de conexión: ' + error.message, 'error');
        }

        // Limpiar input
        event.target.value = '';
    }

    updateContextDisplay(contextoInfo) {
        const display = document.getElementById('current-context-display');
        if (display) {
            display.innerHTML = `
                <div class="current-context">
                    <h4>Contexto Activo:</h4>
                    <p><strong>Asunto:</strong> ${contextoInfo.asunto}</p>
                    <p><strong>Fecha:</strong> ${this.formatDate(contextoInfo.timestamp)}</p>
                    <p><strong>Adjuntos:</strong> ${contextoInfo.adjuntos.length} archivo(s)</p>
                </div>
            `;
            display.style.display = 'block';
        }
        
        // Activar el chat automáticamente
        this.activateChat();
    }
    
    activateChat() {
        // Ocultar el mensaje de estado y habilitar el chat
        const chatStatus = document.getElementById('chat-status');
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendChatBtn');
        const chatMessages = document.getElementById('chatMessages');
        
        if (chatStatus) {
            chatStatus.style.display = 'none';
        }
        
        if (chatInput) {
            chatInput.disabled = false;
            chatInput.placeholder = 'Escribe tu pregunta sobre el documento...';
        }
        
        if (sendBtn) {
            sendBtn.disabled = false;
        }
        
        // Agregar mensaje de bienvenida al chat
        if (chatMessages && this.contextoActual) {
            const welcomeMessage = document.createElement('div');
            welcomeMessage.className = 'chat-message bot';
            welcomeMessage.innerHTML = `
                <p>✅ <strong>Contexto cargado exitosamente</strong></p>
                <p>Documento: <em>${this.contextoActual.asunto}</em></p>
                <p>Ahora puedes hacer preguntas sobre este documento.</p>
            `;
            chatMessages.appendChild(welcomeMessage);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    showMessage(message, type = 'info') {
        // Crear elemento de mensaje
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${type}`;
        messageDiv.textContent = message;
        
        // Agregar al contenedor de mensajes o al body
        const container = document.getElementById('messages-container') || document.body;
        container.appendChild(messageDiv);
        
        // Remover después de 5 segundos
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 5000);
    }

    clearCurrentContext() {
        this.contextoActual = null;
        const display = document.getElementById('current-context-display');
        if (display) {
            display.style.display = 'none';
        }
    }
}

// Inicializar el manejador de contextos
const contextHandler = new ContextHandler();