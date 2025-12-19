from django import template

register = template.Library()

@register.filter
def clp(value):
    """
    Formatea un número como precio chileno
    Ejemplo: 27900 -> $27.900
    """
    try:
        value = int(value)
        return f"${value:,}".replace(',', '.')
    except (ValueError, TypeError):
        return value