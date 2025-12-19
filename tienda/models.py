from django.db import models

# Create your models here.

class Producto(models.Model):
    CATEGORIAS = [
        ('ropa', 'Ropa Deportiva'),
        ('suplementos', 'Suplementos'),
        ('accesorios', 'Accesorios'),
    ]
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.IntegerField()

    imagen = models.ImageField(upload_to='productos/')
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    stock = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.nombre

class Orden(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('cancelado', 'Cancelado'),
        ('fallido', 'Fallido'),
    ]
    
    orden_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    total = models.IntegerField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    flow_token = models.CharField(max_length=255, blank=True, null=True)
    flow_order = models.CharField(max_length=255, blank=True, null=True)
    productos = models.JSONField(default=list)  # Lista de productos comprados
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Orden {self.orden_id} - {self.estado}"