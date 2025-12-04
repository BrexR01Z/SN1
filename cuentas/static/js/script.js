/**
 * Manejo de campos condicionales en el formulario de registro
 */
console.log("js cargado");


function toggleConditionalFields() {
  const tipoUsuario = document.querySelector('input[name="tipo_usuario"]:checked');
  const rutField = document.getElementById('rut-field');
     console.log("1");
  
  if (tipoUsuario) {
    if (tipoUsuario.value === 'dueno') {
      rutField.classList.add('active');
      console.log("2");
     

    } else {
      rutField.classList.remove('active');
      console.log("3");

    }
  }
}

// Ejecutar al cargar la página
document.addEventListener('DOMContentLoaded', function() {
  toggleConditionalFields();
  console.log("cambio");
  // Agregar listener a los radio buttons
  const radioButtons = document.querySelectorAll('input[name="tipo_usuario"]');
  radioButtons.forEach(radio => {
    radio.addEventListener('change', toggleConditionalFields);
  });
});
