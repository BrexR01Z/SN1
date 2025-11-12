document.addEventListener("DOMContentLoaded", function(){
    const tipoUsuario = document.querySelectorAll('input[name="tipo_usuario"]');
    const rut = document.getElementById("rut");

    function mostrarRut(){
        const tipoElegido = document.querySelector('input[name="tipo_usuario"]:checked').value;

        if (tipoElegido === "dueno") {
            rut.style.display = "block";
            document.getElementById("id_rut").required = true;
        } else {
            rut.style.display = "none";
            document.getElementById("id_rut").required = false;
        }
    }  
    tipoUsuario.forEach(radio => {
        radio.addEventListener("change", mostrarRut);
    }) ;
    mostrarRut();
})