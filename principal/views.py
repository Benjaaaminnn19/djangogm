from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging
from .models import Lead
from django.core.mail import send_mail
from django.conf import settings
from .models import Clase, Reserva

# Configurar logger
logger = logging.getLogger(__name__)

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
        logger.error(f"Intento de agendar clase inexistente con ID: {clase_id}")
        return render(request, 'agendar.html', {
            'error': 'La clase seleccionada no existe.'
        })
    except Exception as e:
        logger.error(f"Error al obtener clase {clase_id}: {str(e)}")
        return render(request, 'agendar.html', {
            'error': 'Hubo un error al cargar la información de la clase. Por favor intenta nuevamente.'
        })

    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre', '').strip()
            correo = request.POST.get('correo', '').strip()

            if not nombre or not correo:
                return render(request, 'agendar.html', {
                    'clase': clase,
                    'cupos_disponibles': clase.cupos - Reserva.objects.filter(clase=clase).count(),
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
            try:
                reserva = Reserva.objects.create(clase=clase, nombre=nombre, correo=correo)
            except Exception as e:
                logger.error(f"Error al crear reserva: {str(e)}", exc_info=True)
                return render(request, 'agendar.html', {
                    'clase': clase,
                    'cupos_disponibles': cupos_disponibles,
                    'error': f'Hubo un error al crear la reserva: {str(e)}'
                })
            
            # Enviar correo confirmando que la reserva está pendiente
            correo_enviado = False
            try:
                # Usar el email configurado o uno por defecto
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@gimnasioleblon.com')
                
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
                    from_email=from_email,
                    recipient_list=[correo],
                    fail_silently=True,  # No falla si hay error de correo
                )
                correo_enviado = True
                logger.info(f"Correo enviado exitosamente a {correo} para reserva {reserva.id}")
            except Exception as e:
                # Si falla el envío de correo, registrar el error pero continuar
                logger.error(f"Error al enviar correo a {correo}: {str(e)}", exc_info=True)
                correo_enviado = False

            return render(request, 'reserva_pendiente.html', {
                'clase': clase,
                'reserva': reserva,
                'cupos_disponibles': cupos_disponibles - 1,
                'correo_enviado': correo_enviado
            })
        except Exception as e:
            # Capturar cualquier error no previsto
            logger.error(f"Error inesperado en agendar_clase: {str(e)}", exc_info=True)
            return render(request, 'agendar.html', {
                'clase': clase,
                'cupos_disponibles': clase.cupos - Reserva.objects.filter(clase=clase).count(),
                'error': f'Hubo un error inesperado. Por favor intenta nuevamente. Error: {str(e)}'
            })

    # Contar cupos disponibles para mostrar en el formulario
    try:
        reservas_existentes = Reserva.objects.filter(clase=clase).count()
        cupos_disponibles = clase.cupos - reservas_existentes
    except Exception as e:
        logger.error(f"Error al contar cupos: {str(e)}")
        cupos_disponibles = clase.cupos
    
    return render(request, 'agendar.html', {
        'clase': clase,
        'cupos_disponibles': cupos_disponibles
    })