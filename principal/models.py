from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

class Lead(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre Completo")
    email = models.EmailField(verbose_name="Correo Electrónico")
    fecha_registro = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Registro")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Lead"
        verbose_name_plural = "Leads"
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return f"{self.nombre} - {self.email}"




class Clase(models.Model):
    nombre = models.CharField(max_length=100)
    cupos = models.PositiveIntegerField(default=10)
    fecha = models.DateTimeField()

    def __str__(self):
        return f"{self.nombre} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"

class Reserva(models.Model):
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    aprobado = models.BooleanField(default=False)  # visto bueno del admin
    fecha_reserva = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.clase.nombre}"
