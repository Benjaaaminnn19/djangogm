from django.contrib import admin
from django.utils.html import format_html
from .models import Lead, PlanMembresia
from .models import Clase, Reserva, SolicitudPlan
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Miembro, Asistencia
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(PlanMembresia)
class PlanMembresiaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'activo']
    list_editable = ['precio', 'activo']
    search_fields = ['nombre']
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
    # Los correos de confirmación/cancelación se envían via signals (principal/signals.py),
    # lo que garantiza que funcionen sin importar desde dónde se cambie el estado.

class MiembroCreationForm(UserCreationForm):
    class Meta:
        model = Miembro
        fields = ('email', 'telefono', 'nombre')

class MiembroChangeForm(UserChangeForm):
    class Meta:
        model = Miembro
        fields = '__all__'

@admin.register(Miembro)
class MiembroAdmin(BaseUserAdmin):
    form = MiembroChangeForm
    add_form = MiembroCreationForm
    
    list_display = ('email', 'telefono', 'nombre', 'is_active', 'fecha_inicio', 'activo')
    list_filter = ('activo', 'is_staff', 'is_superuser', 'fecha_inicio')
    search_fields = ('email', 'telefono', 'nombre')
    ordering = ('nombre',)
    
    fieldsets = (
        (None, {'fields': ('email', 'telefono', 'password')}),
        ('Información Personal', {'fields': ('nombre', 'fecha_inicio', 'activo', 'email_verificado')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'telefono', 'nombre', 'password1', 'password2', 'activo'),
        }),
    )

@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ('miembro', 'fecha_entrada')
    list_filter = ('fecha_entrada',)
    search_fields = ('miembro__nombre', 'miembro__email', 'miembro__telefono')
    readonly_fields = ('miembro', 'fecha_entrada')
    ordering = ('-fecha_entrada',)


@admin.register(SolicitudPlan)
class SolicitudPlanAdmin(admin.ModelAdmin):
    list_display = (
        'nombre', 'plan', 'estado', 'fecha_compra',
        'fecha_inicio_membresia', 'fecha_fin_membresia',
        'vigente', 'whatsapp_link',
    )
    list_filter = ('estado', 'plan', 'activado')
    search_fields = ('nombre', 'email', 'telefono')
    list_editable = ('estado', 'fecha_inicio_membresia', 'fecha_fin_membresia')
    readonly_fields = ('fecha_compra',)
    fieldsets = (
        ('Datos del cliente', {'fields': ('nombre', 'email', 'telefono', 'mensaje')}),
        ('Plan', {'fields': ('plan', 'estado', 'activado')}),
        ('Membresía', {'fields': ('fecha_inicio_membresia', 'fecha_fin_membresia', 'fecha_compra')}),
    )

    def vigente(self, obj):
        if obj.esta_vigente:
            return format_html('<span style="color:green;font-weight:bold;">✔ Vigente ({} días)</span>', obj.dias_restantes)
        if obj.fecha_fin_membresia:
            return format_html('<span style="color:red;">✘ Vencida</span>')
        return format_html('<span style="color:gray;">— Sin fecha</span>')
    vigente.short_description = 'Estado membresía'

    def whatsapp_link(self, obj):
        if not obj.telefono:
            return '—'
        numero = obj.telefono.replace('+', '').replace(' ', '').replace('-', '')
        if not numero.startswith('56'):
            numero = f'56{numero}'
        mensaje = f'Hola {obj.nombre}, te contactamos desde Gimnasio Leblon respecto a tu {obj.plan}.'
        url = f'https://wa.me/{numero}?text={mensaje}'
        return format_html('<a href="{}" target="_blank" style="color:green;"><b>WhatsApp</b></a>', url)
    whatsapp_link.short_description = 'WhatsApp'