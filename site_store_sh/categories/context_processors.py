# your_app/context_processors.py
from .models import Category


def categories_context(request):
    """
    Контекстний процесор, який додає всі категорії до контексту шаблону.
    """
    categories = Category.objects.all()
    return {
        'categories': categories
    }
