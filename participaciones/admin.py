from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Participacion, Evidencia

@admin.register(Participacion)
class ParticipacionAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'correo', 'telefono', 'estado', 'fecha_creacion']
    search_fields = ['codigo', 'correo']
    list_filter = ['estado', 'fecha_creacion']

@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    list_display = ['participacion', 'archivo', 'fecha_subida']
    search_fields = ['participacion__codigo']
    list_filter = ['fecha_subida']