// chatHandler.js - Maneja la funcionalidad del chat con el documento

class ChatHandler {
    constructor() {
        this.chatInput = null;
        this.sendButton = null;
        this.chatMessages = null;
        this.chatSection = null;
        this.isInitialized = false;
    }

    init() {
        console.log('Inicializando ChatHandler...');
        
        // Obtener elementos del DOM
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendChatBtn');
        this.chatMessages = document.getElementById('chatMessages');
        this.chatContainer = document.getElementById('chatContainer');

        if (!this.chatInput || !this.sendButton || !this.chatMessages || !this.chatContainer) {
            console.error('No se pudieron encontrar todos los elementos del chat');
            console.log('Elementos encontrados:', {
                chatInput: !!this.chatInput,
                sendButton: !!this.sendButton,
                chatMessages: !!this.chatMessages,
                chatContainer: !!this.chatContainer
            });
            return;
        }

        this.setupEventListeners();
        this.isInitialized = true;
        console.log('ChatHandler inicializado correctamente');
    }

    setupEventListeners() {
        // Evento para el botón de enviar
        this.sendButton.addEventListener('click', () => {
            this.enviarPregunta();
        });

        // Evento para presionar Enter en el input
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.enviarPregunta();
            }
        });
    }

    mostrarChat() {
        if (this.chatContainer) {
            this.chatContainer.style.display = 'block';
        }
        // Ocultar el mensaje de estado
        const chatStatus = document.getElementById('chat-status');
        if (chatStatus) {
            chatStatus.style.display = 'none';
        }
    }

    ocultarChat() {
        if (this.chatContainer) {
            this.chatContainer.style.display = 'none';
        }
        // Mostrar el mensaje de estado
        const chatStatus = document.getElementById('chat-status');
        if (chatStatus) {
            chatStatus.style.display = 'block';
        }
    }

    async enviarPregunta() {
        const pregunta = this.chatInput.value.trim();
        
        if (!pregunta) {
            alert('Por favor, escribe una pregunta.');
            return;
        }

        // Mostrar la pregunta del usuario
        this.agregarMensajeUsuario(pregunta);
        
        // Limpiar el input y deshabilitar el botón
        this.chatInput.value = '';
        this.sendButton.disabled = true;
        this.sendButton.textContent = 'Enviando...';

        try {
            // Enviar la pregunta al servidor
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ pregunta: pregunta })
            });

            const data = await response.json();

            if (data.status === 'success') {
                this.agregarMensajeBot(data.respuesta);
            } else {
                this.agregarMensajeError(data.message || 'Error al procesar la pregunta');
            }

        } catch (error) {
            console.error('Error al enviar pregunta:', error);
            this.agregarMensajeError('Error de conexión. Por favor, intenta de nuevo.');
        } finally {
            // Restaurar el botón
            this.sendButton.disabled = false;
            this.sendButton.textContent = 'Enviar';
            this.chatInput.focus();
        }
    }

    agregarMensajeUsuario(mensaje) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message user-message';
        messageDiv.innerHTML = `
            <div class="message-content">
                <strong>Tú:</strong> ${this.escapeHtml(mensaje)}
            </div>
            <div class="message-time">${this.obtenerHoraActual()}</div>
        `;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    agregarMensajeBot(mensaje) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message bot-message';
        messageDiv.innerHTML = `
            <div class="message-content">
                <strong>Asistente:</strong> ${this.escapeHtml(mensaje)}
            </div>
            <div class="message-time">${this.obtenerHoraActual()}</div>
        `;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    agregarMensajeSistema(mensaje) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message system-message';
        messageDiv.innerHTML = `
            <div class="message-content">
                <em>${this.escapeHtml(mensaje)}</em>
            </div>
            <div class="message-time">${this.obtenerHoraActual()}</div>
        `;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    agregarMensajeError(mensaje) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message error-message';
        messageDiv.innerHTML = `
            <div class="message-content">
                <strong>Error:</strong> ${this.escapeHtml(mensaje)}
            </div>
            <div class="message-time">${this.obtenerHoraActual()}</div>
        `;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    limpiarChat() {
        if (this.chatMessages) {
            this.chatMessages.innerHTML = '';
        }
    }

    scrollToBottom() {
        if (this.chatMessages) {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }
    }

    obtenerHoraActual() {
        const now = new Date();
        return now.toLocaleTimeString('es-ES', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Exportar la clase para uso en otros módulos
window.ChatHandler = ChatHandler;