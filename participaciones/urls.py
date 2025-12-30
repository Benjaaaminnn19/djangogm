from django.urls import path
from .views import participar, subir_evidencia

urlpatterns = [
    path('participar/', participar, name='participar'),
    path('subir-evidencia/', subir_evidencia, name='subir_evidencia'),
    
    
]
