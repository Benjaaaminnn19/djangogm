from django.contrib import admin
from .models import Lead
from .models import Clase, Reserva
from django.core.mail import send_mail

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'fecha_registro', 'activo']
    list_filter = ['activo', 'fecha_registro']
    search_fields = ['nombre', 'email']
    readonly_fields = ['fecha_registro']
    list_editable = ['activo']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-fecha_registro')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'clase', 'aprobado')
    list_filter = ('aprobado',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Si se aprueba la reserva, enviar correo
        if obj.aprobado:
            send_mail(
                subject='¡Tu reserva fue aprobada!',
                message=f'Hola {obj.nombre}, tu reserva para la clase "{obj.clase.nombre}" fue confirmada. ¡Nos vemos pronto en Leblon Gym! 💪',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[obj.correo],
            )