// Manejador de formularios PDF
document.getElementById('uploadForm').addEventListener('submit', (event) => {
    event.preventDefault();

    const responseContainer = document.getElementById('responseContainer');
    const responseJson = document.getElementById('responseJson');
    const submitButton = event.target.querySelector('button[type="submit"]');

    // Mostrar estado de carga
    submitButton.textContent = 'Procesando...';
    submitButton.disabled = true;
    responseContainer.classList.add('hidden');

    const form = document.getElementById('uploadForm');
    const formData = new FormData(form);

    fetch('/procesar_formulario', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        responseJson.textContent = JSON.stringify(data, null, 2);
        responseContainer.classList.remove('hidden');
    })
    .catch(error => {
        console.error('Error:', error);
        responseJson.textContent = `Error: ${error.message}`;
        responseContainer.classList.remove('hidden');
    })
    .finally(() => {
        // Restaurar estado del botón
        submitButton.textContent = 'Procesar Formulario';
        submitButton.disabled = false;
    });
});