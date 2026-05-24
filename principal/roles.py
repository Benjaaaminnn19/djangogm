"""
Helpers para control de roles en el gimnasio.

Roles disponibles:
  - is_staff / is_superuser: Admin completo (dueño/encargado principal)
  - Recepcionista: puede ver y aprobar reservas, ver miembros
  - Instructor: puede ver las clases asignadas y sus reservas

Uso en views:
    from principal.roles import requiere_rol

    @requiere_rol('Recepcionista', 'Instructor')
    def mi_vista(request):
        ...

Uso en templates:
    {% if request.user|es_rol:'Recepcionista' %}
        ...
    {% endif %}
    — O con los métodos del usuario:
    {% if request.user.is_recepcionista %}
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def _tiene_rol(user, *roles):
    """Devuelve True si el usuario pertenece a alguno de los roles indicados o es staff."""
    if not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    return user.groups.filter(name__in=roles).exists()


def requiere_rol(*roles):
    """
    Decorador de vista. Permite el acceso solo a usuarios con alguno de los roles
    especificados (o a staff/superuser). Redirige al home con un mensaje de error si no.

    Ejemplo:
        @requiere_rol('Recepcionista')
        def aprobar_reservas(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not _tiene_rol(request.user, *roles):
                messages.error(request, "No tienes permiso para acceder a esta sección.")
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Métodos convenientes para agregar al modelo Miembro si se quiere
# (se usan como propiedades en templates via request.user.is_recepcionista)

def patch_miembro_roles():
    """
    Agrega propiedades de rol al modelo Miembro dinámicamente.
    Llamar desde AppConfig.ready() si se quiere usar en templates.
    """
    from principal.models import Miembro

    def is_recepcionista(self):
        return _tiene_rol(self, 'Recepcionista')

    def is_instructor(self):
        return _tiene_rol(self, 'Instructor')

    Miembro.is_recepcionista = property(is_recepcionista)
    Miembro.is_instructor = property(is_instructor)
