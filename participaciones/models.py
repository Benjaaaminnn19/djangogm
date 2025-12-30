from django.db import models
import uuid

class Participacion(models.Model):
    codigo = models.CharField(max_length=20, unique=True, editable=False)
    correo = models.EmailField()
    telefono = models.CharField(max_length=15)
    descripcion = models.TextField()
    estado = models.CharField(
        max_length=20,
        default='Registrado'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = f"PART-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.codigo


class Evidencia(models.Model):
    participacion = models.ForeignKey(
        Participacion,
        on_delete=models.CASCADE,
        related_name='evidencias'
    )
    archivo = models.FileField(upload_to='evidencias/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evidencia de {self.participacion.codigo}"
