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

def listar_clases(request):
    """Vista para listar todas las clases disponibles"""
    from django.utils import timezone
    # Obtener clases futuras o del día actual
    clases = Clase.objects.filter(fecha__gte=timezone.now()).order_by('fecha')
    
    # Calcular cupos disponibles para cada clase
    clases_con_cupos = []
    for clase in clases:
        reservas_existentes = Reserva.objects.filter(clase=clase).count()
        cupos_disponibles = clase.cupos - reservas_existentes
        clases_con_cupos.append({
            'clase': clase,
            'cupos_disponibles': cupos_disponibles,
            'tiene_cupos': cupos_disponibles > 0
        })
    
    return render(request, 'listar_clases.html', {
        'clases_con_cupos': clases_con_cupos
    })

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
    try:
        clase = Clase.objects.get(id=clase_id)
    except Clase.DoesNotExist:
        return render(request, 'error.html', {'mensaje': 'La clase no existe'})

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')

        if not nombre or not correo:
            return render(request, 'agendar.html', {
                'clase': clase,
                'error': 'Por favor completa todos los campos'
            })

        # Contar reservas aprobadas o en espera
        reservas_existentes = Reserva.objects.filter(clase=clase).count()
        cupos_disponibles = clase.cupos - reservas_existentes

        if reservas_existentes >= clase.cupos:
            # No hay cupos disponibles - solo mostrar página sin enviar correo
            return render(request, 'sin_cupos.html', {
                'clase': clase,
                'cupos_disponibles': 0
            })

        # Crear la reserva (por aprobar)
        reserva = Reserva.objects.create(clase=clase, nombre=nombre, correo=correo)
        
        # Enviar correo confirmando que la reserva está pendiente
        try:
            send_mail(
                subject=f'Reserva pendiente - {clase.nombre}',
                message=f'''Hola {nombre},

¡Gracias por agendar tu clase!

Tu reserva para la clase "{clase.nombre}" programada para el {clase.fecha.strftime('%d/%m/%Y a las %H:%M')} ha sido registrada y está pendiente de aprobación.

Detalles de tu reserva:
- Clase: {clase.nombre}
- Fecha y hora: {clase.fecha.strftime('%d/%m/%Y a las %H:%M')}
- Cupos disponibles: {cupos_disponibles - 1} de {clase.cupos}

Recibirás un correo de confirmación una vez que tu reserva sea aprobada por nuestro equipo.

¡Nos vemos pronto en Leblon Gym! 💪

Saludos,
Equipo Leblon Gym''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[correo],
                fail_silently=False,
            )
        except Exception as e:
            # Si falla el envío de correo, continuar con el flujo
            pass

        return render(request, 'reserva_pendiente.html', {
            'clase': clase,
            'reserva': reserva,
            'cupos_disponibles': cupos_disponibles - 1
        })

    # Contar cupos disponibles para mostrar en el formulario
    reservas_existentes = Reserva.objects.filter(clase=clase).count()
    cupos_disponibles = clase.cupos - reservas_existentes
    
    return render(request, 'agendar.html', {
        'clase': clase,
        'cupos_disponibles': cupos_disponibles
    })