from django.contrib import admin
from .models import Lead
from .models import Clase, Reserva
from django.core.mail import send_mail
from django.conf import settings

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'fecha_registro', 'activo']
    list_filter = ['activo', 'fecha_registro']
    search_fields = ['nombre', 'email']
    readonly_fields = ['fecha_registro']
    list_editable = ['activo']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-fecha_registro')

@admin.register(Clase)
class ClaseAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha', 'cupos', 'cupos_disponibles')
    list_filter = ('fecha',)
    search_fields = ('nombre',)
    date_hierarchy = 'fecha'
    
    def cupos_disponibles(self, obj):
        reservas = Reserva.objects.filter(clase=obj).count()
        disponibles = obj.cupos - reservas
        if disponibles <= 0:
            return f"0 (Agotado)"
        return f"{disponibles} de {obj.cupos}"
    cupos_disponibles.short_description = 'Cupos Disponibles'

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'clase', 'correo', 'aprobado', 'fecha_reserva')
    list_filter = ('aprobado', 'fecha_reserva', 'clase')
    search_fields = ('nombre', 'correo', 'clase__nombre')
    readonly_fields = ('fecha_reserva',)
    date_hierarchy = 'fecha_reserva'

    def save_model(self, request, obj, form, change):
        # Verificar si cambió el estado de aprobado
        if change:
            old_obj = Reserva.objects.get(pk=obj.pk)
            # Solo enviar correo si se aprueba y antes no estaba aprobado
            if obj.aprobado and not old_obj.aprobado:
                send_mail(
                    subject=f'¡Tu reserva fue aprobada! - {obj.clase.nombre}',
                    message=f'''Hola {obj.nombre},

¡Excelente noticia! Tu reserva para la clase "{obj.clase.nombre}" programada para el {obj.clase.fecha.strftime('%d/%m/%Y a las %H:%M')} ha sido aprobada.

Detalles de tu reserva confirmada:
- Clase: {obj.clase.nombre}
- Fecha y hora: {obj.clase.fecha.strftime('%d/%m/%Y a las %H:%M')}

¡Nos vemos pronto en Leblon Gym! 💪

Saludos,
Equipo Leblon Gym''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[obj.correo],
                    fail_silently=False,
                )
        # Guardar el modelo (tanto para cambios como para nuevos)
        super().save_model(request, obj, form, change)
