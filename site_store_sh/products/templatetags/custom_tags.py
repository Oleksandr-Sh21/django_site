from django import template

register = template.Library()


@register.filter
def range_filter(value):
    """Генерує діапазон від 0 до value."""
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)


@register.filter
def subtract(value):
    """Віднімає одне значення від іншого."""
    try:
        return range(int(5) - int(value))
    except (ValueError, TypeError):
        return 0
