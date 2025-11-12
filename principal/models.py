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

class SolicitudPlan(models.Model):
    PLAN_CHOICES = [
        ('Plan Azul', 'Plan Azul'),
        ('Plan Amarillo', 'Plan Amarillo'),
        ('Plan Verde', 'Plan Verde'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de Pago'),
        ('pagado', 'Pagado'),
        ('activado', 'Activado'),
        ('cancelado', 'Cancelado'),
    ]
    
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, verbose_name="Plan")
    nombre = models.CharField(max_length=100, verbose_name="Nombre Completo")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Correo Electrónico")
    mensaje = models.TextField(blank=True, null=True, verbose_name="Mensaje o Comentarios")
    fecha_compra = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Compra")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pagado', verbose_name="Estado")
    activado = models.BooleanField(default=True, verbose_name="Activado")
    
    class Meta:
        verbose_name = "Compra de Plan"
        verbose_name_plural = "Compras de Planes"
        ordering = ['-fecha_compra']
    
    def __str__(self):
        return f"{self.nombre} - {self.plan} - {self.fecha_compra.strftime('%d/%m/%Y')}"
