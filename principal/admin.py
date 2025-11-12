from django.contrib import admin
from .models import Lead
from .models import Clase, Reserva, SolicitudPlan
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
    list_editable = ('cupos',)  # Permite editar cupos directamente desde la lista
    
    fieldsets = (
        ('Información de la Clase', {
            'fields': ('nombre',)
        }),
        ('Fecha y Cupos', {
            'fields': ('fecha', 'cupos'),
            'description': 'Selecciona una fecha y hora futura para que la clase aparezca en la lista disponible.'
        }),
    )
    
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
    list_editable = ('aprobado',)  # Permite aprobar directamente desde la lista

    def save_model(self, request, obj, form, change):
        # Verificar si cambió el estado de aprobado
        if change:
            try:
                old_obj = Reserva.objects.get(pk=obj.pk)
                # Solo enviar correo si se aprueba y antes no estaba aprobado
                if obj.aprobado and not old_obj.aprobado:
                    try:
                        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@gimnasioleblon.com')
                        send_mail(
                            subject=f'🎉 ¡Invitación Confirmada! - Clase: {obj.clase.nombre}',
                            message=f'''╔═══════════════════════════════════════════════════════╗
║         🏋️ GIMNASIO LEBLON - INVITACIÓN CONFIRMADA 🏋️        ║
╚═══════════════════════════════════════════════════════╝

Hola {obj.nombre},

¡Tenemos el placer de confirmarte tu invitación a nuestra clase!

📋 DETALLES DE TU INVITACIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🎯 Clase: {obj.clase.nombre}
   📅 Fecha: {obj.clase.fecha.strftime('%d de %B de %Y')}
   ⏰ Hora: {obj.clase.fecha.strftime('%H:%M')} hrs
   ✅ Estado: CONFIRMADA

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 IMPORTANTE:
   • Presenta esta invitación cuando llegues al gimnasio
   • Llega 10 minutos antes para el registro
   • Trae ropa cómoda y una botella de agua

¡Estamos emocionados de verte en Leblon Gym! 💪

Saludos,
Equipo Leblon Gym

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Este es un correo automático, por favor no responder.''',
                            from_email=from_email,
                            recipient_list=[obj.correo],
                            fail_silently=True,
                        )
                    except Exception as e:
                        # Si falla el correo, solo registrar el error pero continuar
                        pass
            except Reserva.DoesNotExist:
                # Si es una nueva reserva, no hacer nada
                pass
        # Guardar el modelo (tanto para cambios como para nuevos)
        super().save_model(request, obj, form, change)

@admin.register(SolicitudPlan)
class SolicitudPlanAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'plan', 'telefono', 'email', 'fecha_compra', 'estado', 'activado')
    list_filter = ('plan', 'estado', 'activado', 'fecha_compra')
    search_fields = ('nombre', 'email', 'telefono', 'plan')
    readonly_fields = ('fecha_compra',)
    date_hierarchy = 'fecha_compra'
    list_editable = ('estado', 'activado')
    
    fieldsets = (
        ('Información del Cliente', {
            'fields': ('nombre', 'telefono', 'email')
        }),
        ('Detalles del Plan', {
            'fields': ('plan', 'mensaje')
        }),
        ('Estado de la Compra', {
            'fields': ('estado', 'activado', 'fecha_compra')
        }),
    )
