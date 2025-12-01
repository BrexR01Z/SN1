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

// Mapa 


    // Inicializar el mapa
    var map = L.map('map').setView([-33.45, -70.66], 13); // Santiago

    // Capa base (OpenStreetMap)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
    }).addTo(map);

    // Marcador de ejemplo
    L.marker([-33.45, -70.66]).addTo(map)
        .bindPopup("Estás viendo Santiago")
        .openPopup();
