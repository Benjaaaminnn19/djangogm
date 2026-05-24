from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
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
    fecha = models.DateTimeField(db_index=True)

    def __str__(self):
        return f"{self.nombre} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"

class Reserva(models.Model):
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(db_index=True)
    aprobado = models.BooleanField(default=False)  # visto bueno del admin
    fecha_reserva = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.clase.nombre}"

class SolicitudPlan(models.Model):
    PLAN_CHOICES = [
        ('Plan Trimestral', 'Plan Trimestral'),
        ('Plan Semestral', 'Plan Semestral'),
        ('Plan Anual', 'Plan Anual'),
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
    email = models.EmailField(db_index=True, verbose_name="Correo Electrónico")
    mensaje = models.TextField(blank=True, null=True, verbose_name="Mensaje o Comentarios")
    fecha_compra = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Compra")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente', verbose_name="Estado")
    activado = models.BooleanField(default=False, verbose_name="Activado")
    fecha_inicio_membresia = models.DateField(null=True, blank=True, verbose_name="Inicio de membresía")
    fecha_fin_membresia = models.DateField(null=True, blank=True, verbose_name="Vencimiento de membresía")

    class Meta:
        verbose_name = "Compra de Plan"
        verbose_name_plural = "Compras de Planes"
        ordering = ['-fecha_compra']

    def __str__(self):
        return f"{self.nombre} - {self.plan} - {self.fecha_compra.strftime('%d/%m/%Y')}"

    @property
    def esta_vigente(self):
        if not self.fecha_fin_membresia:
            return False
        return timezone.now().date() <= self.fecha_fin_membresia

    @property
    def dias_restantes(self):
        if not self.fecha_fin_membresia:
            return None
        delta = self.fecha_fin_membresia - timezone.now().date()
        return max(delta.days, 0)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, telefono, password=None, **extra_fields):
        if not email and not telefono:
            raise ValueError('Debe ingresar email o teléfono')
        if email:
            email = self.normalize_email(email)
        user = self.model(email=email, telefono=telefono, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, telefono, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, telefono, password, **extra_fields)

class PlanMembresia(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre del Plan")
    precio = models.PositiveIntegerField(verbose_name="Precio (CLP)")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Plan de Membresía"
        verbose_name_plural = "Planes de Membresía"
        ordering = ['precio']

    def __str__(self):
        return f"{self.nombre} — ${self.precio:,}".replace(',', '.')


class Miembro(AbstractUser):
    username = None  # No usamos username
    email = models.EmailField(unique=True, blank=True, null=True)
    telefono = models.CharField(max_length=20, unique=True, blank=True, null=True)
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField(default=timezone.now)
    activo = models.BooleanField(default=True)
    email_verificado = models.BooleanField(default=False, verbose_name="Email verificado")

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  # Django usa email por defecto
    REQUIRED_FIELDS = ['telefono']  # Obliga a poner teléfono al crear superuser

    def __str__(self):
        return self.nombre or self.email or self.telefono

class Asistencia(models.Model):
    miembro = models.ForeignKey(Miembro, on_delete=models.CASCADE)
    fecha_entrada = models.DateTimeField(default=timezone.now)
    fecha_salida = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.miembro} - {self.fecha_entrada.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        ordering = ['-fecha_entrada']