/**
 * Manejo de campos condicionales en el formulario de registro
 */

function toggleConditionalFields() {
  const tipoUsuario = document.querySelector('input[name="tipo_usuario"]:checked');
  const rutField = document.getElementById('rut-field');

  
  if (tipoUsuario) {
    if (tipoUsuario.value === 'dueno') {
      rutField.classList.add('active');

    } else {
      rutField.classList.remove('active');

    }
  }
}

// Ejecutar al cargar la página
document.addEventListener('DOMContentLoaded', function() {
  toggleConditionalFields();
  
  // Agregar listener a los radio buttons
  const radioButtons = document.querySelectorAll('input[name="tipo_usuario"]');
  radioButtons.forEach(radio => {
    radio.addEventListener('change', toggleConditionalFields);
  });
});