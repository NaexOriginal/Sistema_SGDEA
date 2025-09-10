// Importar y gestionar los módulos

// Variable global para el chat handler
window.chatHandler = null;

// Cargar emailHandler.js
function loadEmailHandler() {
    const script = document.createElement('script');
    script.src = '/static/js/emailHandler.js';
    script.onload = function() {
        console.log('Email handler cargado');
    };
    document.head.appendChild(script);
}

// Cargar formHandler.js
function loadFormHandler() {
    const script = document.createElement('script');
    script.src = '/static/js/formHandler.js';
    script.onload = function() {
        console.log('Form handler cargado');
    };
    document.head.appendChild(script);
}

// Cargar chatHandler.js
function loadChatHandler() {
    const script = document.createElement('script');
    script.src = '/static/js/chatHandler.js';
    script.onload = function() {
        console.log('Chat handler cargado');
        // Inicializar el chat handler
        if (window.ChatHandler) {
            window.chatHandler = new window.ChatHandler();
            window.chatHandler.init();
        }
    };
    document.head.appendChild(script);
}

// Inicializar la aplicación
function inicializar() {
    loadEmailHandler();
    loadFormHandler();
    loadChatHandler();
    console.log('Aplicación inicializada');
}

// Ejecutar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', inicializar);