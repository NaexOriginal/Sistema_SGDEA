// Importar y gestionar los módulos

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

// Inicializar la aplicación
function inicializar() {
    loadEmailHandler();
    loadFormHandler();
    console.log('Aplicación inicializada');
}

// Ejecutar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', inicializar);