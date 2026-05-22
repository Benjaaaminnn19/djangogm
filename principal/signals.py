import logging
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Reserva

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Reserva)
def reserva_pre_save(sender, instance, **kwargs):
    """Guarda el estado anterior de 'aprobado' para compararlo en post_save."""
    if instance.pk:
        try:
            instance._aprobado_anterior = Reserva.objects.get(pk=instance.pk).aprobado
        except Reserva.DoesNotExist:
            instance._aprobado_anterior = False
    else:
        instance._aprobado_anterior = False


@receiver(post_save, sender=Reserva)
def reserva_post_save(sender, instance, created, **kwargs):
    """
    Envía correos HTML cuando cambia el estado de aprobación.
    Funciona sin importar si el cambio viene del admin detail, list_editable, action, etc.
    """
    aprobado_anterior = getattr(instance, '_aprobado_anterior', False)
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@gimnasiolebloncalama.cl')
    fecha_str = instance.clase.fecha.strftime('%d/%m/%Y a las %H:%M')
    ctx = {
        'nombre': instance.nombre,
        'clase_nombre': instance.clase.nombre,
        'clase_fecha': fecha_str,
    }

    # --- Correo de CONFIRMACIÓN: pasó de no aprobado → aprobado ---
    if instance.aprobado and not aprobado_anterior and not created:
        try:
            html_body = render_to_string('emails/reserva_confirmada.html', ctx)
            plain_body = (
                f"Hola {instance.nombre},\n\n"
                f"¡Tu reserva para {instance.clase.nombre} el {fecha_str} ha sido confirmada!\n\n"
                f"Recuerda llegar 10 minutos antes y traer ropa cómoda y agua.\n\n"
                f"¡Te esperamos!\nEquipo Leblon Gym — Calama"
            )
            send_mail(
                subject=f'¡Reserva confirmada! — {instance.clase.nombre}',
                message=plain_body,
                from_email=from_email,
                recipient_list=[instance.correo],
                html_message=html_body,
                fail_silently=True,
            )
            logger.info(f"Correo de confirmacion enviado a {instance.correo} (reserva {instance.pk})")
        except Exception as e:
            logger.error(f"Error al enviar correo de confirmacion a {instance.correo}: {e}", exc_info=True)

    # --- Correo de CANCELACIÓN: pasó de aprobado → no aprobado ---
    elif not instance.aprobado and aprobado_anterior and not created:
        try:
            html_body = render_to_string('emails/reserva_cancelada.html', ctx)
            plain_body = (
                f"Hola {instance.nombre},\n\n"
                f"Te informamos que tu reserva para {instance.clase.nombre} el {fecha_str} "
                f"ha sido cancelada.\n\n"
                f"Si tienes dudas, contáctanos al +56 9 7527 4804.\n\n"
                f"Equipo Leblon Gym — Calama"
            )
            send_mail(
                subject=f'Reserva cancelada — {instance.clase.nombre}',
                message=plain_body,
                from_email=from_email,
                recipient_list=[instance.correo],
                html_message=html_body,
                fail_silently=True,
            )
            logger.info(f"Correo de cancelacion enviado a {instance.correo} (reserva {instance.pk})")
        except Exception as e:
            logger.error(f"Error al enviar correo de cancelacion a {instance.correo}: {e}", exc_info=True)
