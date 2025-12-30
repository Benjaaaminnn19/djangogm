from django import forms
from .models import Participacion, Evidencia

class ParticipacionForm(forms.ModelForm):
    class Meta:
        model = Participacion
        fields = ['correo', 'telefono', 'descripcion']


class EvidenciaForm(forms.ModelForm):
    class Meta:
        model = Evidencia
        fields = ['archivo', 'comentario']
