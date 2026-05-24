"""
Verifica membresías vencidas y las marca como canceladas.
Envía email de aviso a los que vencen en los próximos 7 días.

Uso:
    python manage.py verificar_membresias
    python manage.py verificar_membresias --dry-run   # solo muestra, no modifica

Programar en Railway con Cron Job:
    Comando: python manage.py verificar_membresias
    Frecuencia: 0 8 * * *  (todos los días a las 8 AM)
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from principal.models import SolicitudPlan


class Command(BaseCommand):
    help = 'Verifica membresías vencidas y avisa a las que vencen pronto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra los cambios sin aplicarlos',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        hoy = timezone.now().date()
        limite_aviso = hoy + timedelta(days=7)
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@gimnasiolebloncalama.cl')

        # 1. Vencer membresías que ya expiraron
        vencidas = SolicitudPlan.objects.filter(
            estado='activado',
            fecha_fin_membresia__lt=hoy,
        )

        if dry_run:
            self.stdout.write(f'[DRY RUN] Membresías a vencer: {vencidas.count()}')
        else:
            for s in vencidas:
                s.estado = 'cancelado'
                s.activado = False
                s.save(update_fields=['estado', 'activado'])

                # Notificar al miembro
                try:
                    send_mail(
                        subject='Tu membresía en Gimnasio Leblon ha vencido',
                        message=(
                            f"Hola {s.nombre},\n\n"
                            f"Tu {s.plan} venció el {s.fecha_fin_membresia.strftime('%d/%m/%Y')}.\n"
                            "Para renovar, visita gimnasiolebloncalama.cl o contáctanos al +56 9 7527 4804.\n\n"
                            "Equipo Leblon Fitness"
                        ),
                        from_email=from_email,
                        recipient_list=[s.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass

            self.stdout.write(self.style.WARNING(
                f'{vencidas.count()} membresías marcadas como canceladas.'
            ))

        # 2. Avisar a membresías que vencen en los próximos 7 días
        por_vencer = SolicitudPlan.objects.filter(
            estado='activado',
            fecha_fin_membresia__gte=hoy,
            fecha_fin_membresia__lte=limite_aviso,
        )

        if dry_run:
            self.stdout.write(f'[DRY RUN] Membresías por vencer (7 días): {por_vencer.count()}')
        else:
            for s in por_vencer:
                dias = (s.fecha_fin_membresia - hoy).days
                try:
                    send_mail(
                        subject=f'Tu membresía vence en {dias} día{"s" if dias != 1 else ""} — Gimnasio Leblon',
                        message=(
                            f"Hola {s.nombre},\n\n"
                            f"Tu {s.plan} vence el {s.fecha_fin_membresia.strftime('%d/%m/%Y')} "
                            f"({dias} día{'s' if dias != 1 else ''}).\n"
                            "Renueva antes de que expire para no perder el acceso.\n\n"
                            "Contáctanos: +56 9 7527 4804 | gimnasiolebloncalama.cl\n\n"
                            "Equipo Leblon Fitness"
                        ),
                        from_email=from_email,
                        recipient_list=[s.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass

            self.stdout.write(self.style.SUCCESS(
                f'{por_vencer.count()} avisos de vencimiento enviados.'
            ))

        self.stdout.write(self.style.SUCCESS('Verificación completada.'))
