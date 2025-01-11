from django import template

register = template.Library()


@register.filter
def mul(value, arg):
    """Множить значення на аргумент."""
    try:
        return float(value) * int(arg)
    except (ValueError, TypeError):
        return 0