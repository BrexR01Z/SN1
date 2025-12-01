from django.db import models

from cuentas.models import Dueno


# Create your models here.


"""
"""
class Deporte(models.Model):
    DEPORTES = [
        ("FUTBOL", "Futbol"),
        ("BASQUETBALL","Basquetball"),
        ("VOLEYBALL","Voleyball"),
        ("TENIS","Tenis"),
        ("RUGBY","Rugby"),
        ("HANDBALL","Handball"),
        ("BOWLING","Bowling"),
        ("SQUASH","Squash"),
        ("PADEL","Padel"),
        ("OTRO","Otro"),
        ("---","---"),        
    ]
    nombre = models.CharField(max_length=20,unique=True, choices=DEPORTES, default="---")
    # nombre = models.CharField(max_length=20)

    def __str__(self):
        return f"Nombre deporte = {self.nombre}"


    
class Establecimiento (models.Model):
    dueno = models.ForeignKey(Dueno, on_delete=models.CASCADE, related_name="establecimientos")
    nombre = models.CharField(max_length=50, unique=True,blank=False, null=False)
    direccion = models.CharField(max_length=100,blank=False, null=False)
    telefono_contacto = models.CharField(max_length=20,blank=False, null=False)
    correo_contacto = models.EmailField(blank=False, null=False)
    estacionamiento_disponible = models.BooleanField(default=False)
    camarines_disponible = models.BooleanField(default=False)
    # editar a futuro para integrar mapa
    def __str__(self):
        return f"Nombre establecimietno = {self.nombre} , Dueno = {self.dueno}"


class HorarioEstablecimiento(models.Model):
    DIAS_SEMANA = [
        ("Lunes","Lunes"),
        ("Martes","Martes"),
        ("Miercoles","Miercoles"),
        ("Jueves","Jueves"),
        ("Viernes","Viernes"),
        ("Sabado","Sabado"),
        ("Domingo","Domingo")
    ]
    
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name="horarios")
    dia = models.CharField(max_length=20, choices=DIAS_SEMANA)
    # hacer validacion para q hora_apertura<hora_cierre
    hora_apertura = models.TimeField()
    hora_cierre = models.TimeField()

    def __str__(self):
        return f"Horario {self.establecimiento}, dia {self.dia}, desde {self.hora_apertura} hasta {self.hora_cierre}"
    
class Cancha (models.Model):
    TIPOS_SUPERFICIES = [
        ("Pasto_Natural", "Pasto Natural"),
        ("Pasto_Sintético","Pasto Sintético"),
        ("Cemento","Cemento"),
        ("Arcilla","Arcilla"),
        ("Madera","Madera"),
        ("Caucho","Caucho"),
        ("Vinilo","Vinilo"),
        ]
    
    TIPOS_ILUMINACION = {
        ("LED","LED"),
        ("Natural", "Natural"),
        ("Mixta","Mixta"),
        ("Halogena","Halogena"),
        ("Fluorecente","Fluorecente"),

    }
    
    DEPORTES = [
        ("Futbol", "Futbol"),
        ("Basquetball","Basquetball"),
        ("Voleyball","Voleyball"),
        ("Tenis","Tenis"),
        ("Rugby","Rugby"),
        ("Handball","Handball"),
        ("Bowling","Bowling"),
        ("Squash","Squash"),
        ("Padel","Padel"),
        ("Otro","Otro"),
        ("---","---"),        
    ]
    
    
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name="canchas")
    deporte = models.CharField(max_length=20, choices=DEPORTES, default="---",blank=False, null=False)    
    #deporte = models.ManyToManyField(Deporte,choices=DEPORTES, default="---")
    nombre = models.CharField(max_length=25,blank=False, null=False)
    superficie = models.CharField(max_length=25, choices=TIPOS_SUPERFICIES,blank=False, null=False)
    iluminacion = models.CharField(max_length=20, choices=TIPOS_ILUMINACION,blank=False, null=False)
    # true = interior , false = exterior
    interior = models.BooleanField(default=False)
    # validar q sea un valor entero, positivo, 
    valor_por_bloque = models.DecimalField(max_digits=10, decimal_places=0,blank=False, null=False)

    def __str__(self):
        return f"Cancha = {self.nombre}, Deporte = {self.deporte}, Establecimiento {self.establecimiento} "

    


# integrar imagenes para canchas y establecimientos
