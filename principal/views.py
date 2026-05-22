from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.db.utils import NotSupportedError
import json
import logging
from .models import Lead
from django.core.mail import send_mail
from django.conf import settings
from .models import Clase, Reserva, SolicitudPlan
from .models import Miembro, Asistencia
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

# Configurar logger
logger = logging.getLogger(__name__)

def home(request):
    """Vista para mostrar la página principal del gimnasio"""
    return render(request, 'prueba.html')

def listar_clases(request):
    """Vista para listar todas las clases disponibles"""
    from django.utils import timezone
    # Mostrar clases de hoy en adelante (comparando por fecha, no por hora exacta)
    # Esto evita que una clase de hoy a las 9am desaparezca si ya son las 9:05am
    hoy = timezone.now().date()
    clases = Clase.objects.filter(fecha__date__gte=hoy).order_by('fecha')
    
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

            # Crear la reserva dentro de una transacción atómica para evitar
            # que dos personas tomen el último cupo al mismo tiempo (race condition).
            try:
                with transaction.atomic():
                    try:
                        # select_for_update bloquea las filas en PostgreSQL (producción).
                        reservas_existentes = (
                            Reserva.objects.select_for_update()
                            .filter(clase=clase)
                            .count()
                        )
                    except NotSupportedError:
                        # SQLite (desarrollo local) no soporta SELECT FOR UPDATE.
                        reservas_existentes = Reserva.objects.filter(clase=clase).count()

                    cupos_disponibles = clase.cupos - reservas_existentes

                    if reservas_existentes >= clase.cupos:
                        return render(request, 'sin_cupos.html', {
                            'clase': clase,
                            'cupos_disponibles': 0
                        })

                    reserva = Reserva.objects.create(clase=clase, nombre=nombre, correo=correo)
            except Exception as e:
                logger.error(f"Error al crear reserva: {str(e)}", exc_info=True)
                return render(request, 'agendar.html', {
                    'clase': clase,
                    'cupos_disponibles': clase.cupos - Reserva.objects.filter(clase=clase).count(),
                    'error': f'Hubo un error al crear la reserva: {str(e)}'
                })
            
            # Enviar correo avisando que la reserva quedó pendiente de aprobación
            correo_enviado = False
            try:
                from django.template.loader import render_to_string
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@gimnasiolebloncalama.cl')
                ctx = {
                    'nombre': nombre,
                    'clase_nombre': clase.nombre,
                    'clase_fecha': clase.fecha.strftime('%d/%m/%Y a las %H:%M'),
                }
                html_body = render_to_string('emails/reserva_recibida.html', ctx)
                plain_body = (
                    f"Hola {nombre},\n\n"
                    f"Tu reserva para {clase.nombre} el {ctx['clase_fecha']} "
                    f"fue recibida y está pendiente de confirmación.\n\n"
                    f"Recibirás otro correo cuando sea aprobada.\n\n"
                    f"Equipo Leblon Gym — Calama"
                )
                send_mail(
                    subject=f'Reserva recibida — {clase.nombre}',
                    message=plain_body,
                    from_email=from_email,
                    recipient_list=[correo],
                    html_message=html_body,
                    fail_silently=True,
                )
                correo_enviado = True
                logger.info(f"Correo de recepcion enviado a {correo} para reserva {reserva.id}")
            except Exception as e:
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

@login_required
def invitaciones_confirmadas(request):
    """Vista para que el personal del gimnasio vea las invitaciones confirmadas"""
    # Obtener todas las reservas confirmadas (aprobadas)
    reservas_confirmadas = Reserva.objects.filter(aprobado=True).select_related('clase').order_by('clase__fecha', 'fecha_reserva')
    
    # Agrupar por clase
    clases_con_invitados = {}
    for reserva in reservas_confirmadas:
        clase_id = reserva.clase.id
        if clase_id not in clases_con_invitados:
            clases_con_invitados[clase_id] = {
                'clase': reserva.clase,
                'invitados': []
            }
        clases_con_invitados[clase_id]['invitados'].append(reserva)
    
    # Convertir a lista ordenada por fecha de clase
    clases_lista = sorted(clases_con_invitados.values(), key=lambda x: x['clase'].fecha)
    
    # Estadísticas
    total_invitados = reservas_confirmadas.count()
    clases_hoy = [c for c in clases_lista if c['clase'].fecha.date() == timezone.now().date()]
    
    return render(request, 'invitaciones_confirmadas.html', {
        'clases_con_invitados': clases_lista,
        'total_invitados': total_invitados,
        'clases_hoy': clases_hoy,
        'total_clases': len(clases_lista)
    })

@method_decorator(csrf_exempt, name='dispatch')
class ComprarPlanView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            plan = data.get('plan')
            nombre = data.get('nombre')
            telefono = data.get('telefono')
            email = data.get('email')
            mensaje = data.get('mensaje', '')
            
            # Obtener el email del usuario logueado si existe
            if request.user.is_authenticated:
                email = request.user.email
                nombre = nombre or request.user.nombre
                telefono = telefono or request.user.telefono
            
            if not plan or not nombre or not telefono or not email:
                return JsonResponse({
                    'success': False, 
                    'message': 'Por favor completa todos los campos requeridos'
                })
            
            # Determinar precios según el plan
            precios = {
                'Plan Trimestral': {'mensualidad': 91000, 'matricula': 0},
                'Plan Anual': {'mensualidad': 298000, 'matricula': 0},
                'Plan Semestral': {'mensualidad': 171000, 'matricula': 0},
            }
            
            precio_plan = precios.get(plan, {'mensualidad': 0, 'matricula': 0})
            total = precio_plan['mensualidad'] + precio_plan['matricula']
            
            # Crear compra de plan
            compra = SolicitudPlan.objects.create(
                plan=plan,
                nombre=nombre,
                telefono=telefono,
                email=email,
                mensaje=mensaje if mensaje else None,
                estado='pendiente',
                activado=False
            )
            
            # Enviar correo de confirmación de solicitud
            try:
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@gimnasioleblon.com')
                
                send_mail(
                    subject=f'Solicitud de {plan} - Gimnasio Leblon',
                    message=f'''╔═══════════════════════════════════════════════════════╗
║         🏋️ GIMNASIO LEBLON - SOLICITUD RECIBIDA 🏋️        ║
╚═══════════════════════════════════════════════════════╝

¡Hola {nombre}!

✅ Tu solicitud ha sido recibida exitosamente.

📋 DETALLES DE TU SOLICITUD:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🎯 Plan: {plan}
   💰 Precio: ${precio_plan['mensualidad']:,}
   📧 Email: {email}
   📱 Teléfono: {telefono}
   📅 Fecha de Solicitud: {compra.fecha_compra.strftime('%d/%m/%Y %H:%M')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 PRÓXIMOS PASOS:
   1. Nuestro equipo revisará tu solicitud
   2. Te contactaremos para coordinar el pago
   3. Una vez confirmado el pago, activaremos tu membresía

💪 INFORMACIÓN DEL GIMNASIO:
   • Dirección: Av. Granaderos 3037, Calama, Antofagasta
   • Teléfono: +56 9 7527 4804
   • WhatsApp: https://wa.me/56975274804
   • Horario: Lun-Vie 9:00-23:00, Sáb 9:00-22:00, Dom 9:00-13:00

¡Gracias por elegir Leblon Fitness!

Saludos,
Equipo Leblon Fitness

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Este es un correo automático de confirmación.''',
                    from_email=from_email,
                    recipient_list=[email],
                    fail_silently=True,
                )
            except Exception as e:
                logger.error(f"Error al enviar correo de confirmación: {str(e)}")
            
            return JsonResponse({
                'success': True,
                'message': f'¡Solicitud enviada! Te contactaremos pronto para confirmar tu {plan}. Revisa tu correo ({email}).'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 
                'message': 'Error en los datos enviados'
            })
        except Exception as e:
            logger.error(f"Error al procesar compra de plan: {str(e)}")
            return JsonResponse({
                'success': False, 
                'message': 'Error interno del servidor. Por favor intenta nuevamente.'
            })


def login_view(request):
    """Vista de inicio de sesión"""
    # Si ya está autenticado, redirigir al home
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        identificador = request.POST.get('identificador', '').strip()
        password = request.POST.get('password', '')

        if not identificador or not password:
            messages.error(request, "Por favor ingresa tu email/teléfono y contraseña.")
            return render(request, 'login.html')

        # Intentar autenticar
        user = authenticate(request, username=identificador, password=password)

        if user is not None:
            if not user.activo:
                messages.error(request, "Tu cuenta está inactiva. Contacta al gimnasio.")
            else:
                login(request, user)
                messages.success(request, f"¡Bienvenido de vuelta, {user.nombre or user.email}!")
                
                # Redirigir a la página que intentaba acceder o al home
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        else:
            messages.error(request, "Email/teléfono o contraseña incorrectos.")
    
    return render(request, 'login.html')


def registro_view(request):
    """Vista de registro de nuevos usuarios"""
    # Si ya está autenticado, redirigir al home
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        # Validaciones básicas
        if not nombre or not email or not telefono or not password1 or not password2:
            messages.error(request, "Todos los campos son obligatorios.")
        elif password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
        elif len(password1) < 8:
            messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
        elif Miembro.objects.filter(email=email).exists():
            messages.error(request, "Ya existe una cuenta con ese email.")
        elif Miembro.objects.filter(telefono=telefono).exists():
            messages.error(request, "Ya existe una cuenta con ese teléfono.")
        else:
            try:
                # Crear el miembro
                miembro = Miembro.objects.create_user(
                    email=email,
                    telefono=telefono,
                    password=password1,
                    nombre=nombre
                )
                
                # Enviar correo de bienvenida
                try:
                    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@gimnasioleblon.com')
                    
                    send_mail(
                        subject='¡Bienvenido a Leblon Fitness!',
                        message=f'''╔═══════════════════════════════════════════════════════╗
║         🏋️ ¡BIENVENIDO A LEBLON FITNESS! 🏋️          ║
╚═══════════════════════════════════════════════════════╝

¡Hola {nombre}!

🎉 Tu cuenta ha sido creada exitosamente.

📧 Email: {email}
📱 Teléfono: {telefono}

🚀 PRÓXIMOS PASOS:
   1. Inicia sesión en nuestra plataforma
   2. Explora nuestros planes de membresía
   3. Agenda tu primera clase
   4. ¡Comienza tu transformación!

💪 INFORMACIÓN DEL GIMNASIO:
   • Dirección: Av. Granaderos 3037, Calama, Antofagasta
   • Teléfono: +56 9 7527 4804
   • WhatsApp: https://wa.me/56975274804
   • Horario: Lun-Vie 9:00-23:00, Sáb 9:00-22:00, Dom 9:00-13:00

¡Estamos emocionados de ser parte de tu viaje fitness!

Saludos,
Equipo Leblon Fitness

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━''',
                        from_email=from_email,
                        recipient_list=[email],
                        fail_silently=True,
                    )
                except Exception as e:
                    logger.error(f"Error al enviar correo de bienvenida: {str(e)}")
                
                # Hacer login automático
                user = authenticate(request, username=email, password=password1)
                if user is not None:
                    login(request, user)
                    messages.success(request, f"¡Bienvenido a Leblon Fitness, {nombre}! Tu cuenta ha sido creada exitosamente.")
                    
                    # Redirigir al home
                    return redirect('home')
                
            except Exception as e:
                logger.error(f"Error al crear cuenta: {str(e)}")
                messages.error(request, f"Error al crear la cuenta: {str(e)}")
                return render(request, 'registro.html', {
                    'nombre': nombre,
                    'email': email,
                    'telefono': telefono,
                })

        # Si hay errores, vuelve al formulario con los datos
        return render(request, 'registro.html', {
            'nombre': nombre,
            'email': email,
            'telefono': telefono,
        })

    return render(request, 'registro.html')


def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect('home')


@login_required
def checkin_view(request):
    """Vista de check-in para usuarios autenticados"""
    if request.method == 'POST':
        # Registrar asistencia
        hoy = timezone.now().date()
        if not Asistencia.objects.filter(miembro=request.user, fecha_entrada__date=hoy).exists():
            Asistencia.objects.create(miembro=request.user)
            messages.success(request, "¡Entrada registrada exitosamente!")
        else:
            messages.info(request, "Ya registraste entrada hoy.")
        
        return render(request, 'checkin.html', {
            'mensaje_exito': True,
            'nombre_miembro': request.user.nombre or request.user.email or request.user.telefono,
            'hora_entrada': timezone.now(),
        })
    
    return render(request, 'checkin.html')