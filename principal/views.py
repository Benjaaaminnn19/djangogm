from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import Lead
from django.core.mail import send_mail
from django.conf import settings
from .models import Clase, Reserva

# Create your views here.

def home(request):
    """Vista para mostrar la página principal del gimnasio"""
    return render(request, 'prueba.html')

@method_decorator(csrf_exempt, name='dispatch')
class RegistrarLeadView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            nombre = data.get('nombre')
            email = data.get('email')
            
            if not nombre or not email:
                return JsonResponse({'success': False, 'message': 'Nombre y email son requeridos'})
            
            # Verificar si el email ya existe
            if Lead.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': 'Este email ya está registrado'})
            
            # Crear nuevo lead
            lead = Lead.objects.create(nombre=nombre, email=email)
            
            return JsonResponse({
                'success': True, 
                'message': '¡Registro exitoso! Te contactaremos pronto.',
                'lead_id': lead.id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Error en los datos enviados'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error interno del servidor'})
        
def agendar_clase(request, clase_id):
    clase = Clase.objects.get(id=clase_id)

    if request.method == 'POST':
        nombre = request.POST['nombre']
        correo = request.POST['correo']

        # Contar reservas aprobadas o en espera
        reservas_existentes = Reserva.objects.filter(clase=clase).count()

        if reservas_existentes >= clase.cupos:
            return render(request, 'sin_cupos.html', {'clase': clase})

        # Crear la reserva (por aprobar)
        Reserva.objects.create(clase=clase, nombre=nombre, correo=correo)
        return render(request, 'reserva_pendiente.html', {'clase': clase})

    return render(request, 'agendar.html', {'clase': clase})