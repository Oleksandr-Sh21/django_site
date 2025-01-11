from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils.translation import get_language
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.list import MultipleObjectMixin

from categories.models import Category
from products.models import Product
from reviews.models import Review


class ListProduct(ListView):
    model = Product
    template_name = 'products/index.html'
    context_object_name = 'products'  # Змінюємо назву object_list на products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Додаємо всі категорії в контекст
        context['title'] = 'sh_shop'
        return context


class DetailProduct(DetailView, MultipleObjectMixin):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'product_slug'
    paginate_by = 3  # Кількість відгуків на сторінку

    def get_context_data(self, **kwargs):
        # Отримуємо всі відгуки, пов'язані з продуктом
        all_reviews = Review.objects.filter(product=self.object).order_by('-created_at')
        quality = all_reviews.count
        avg_rating = self.object.reviews.aggregate(avg=Avg('rating'))['avg']

        # Отримуємо перші 3 відгуки для початкового виведення
        initial_reviews = all_reviews[:3]

        # Для пагінації, якщо знадобиться повний список
        context = super().get_context_data(object_list=all_reviews, **kwargs)

        # Додаємо необхідні змінні в контекст
        context['initial_reviews'] = initial_reviews
        context['has_more_reviews'] = all_reviews.count() > 3  # Прапорець для кнопки "Показати ще"
        context['title'] = self.object.name  # Заголовок продукту
        context['request'] = self.request  # Щоб мати доступ до запитів
        context['avg_rating'] = avg_rating
        context['quality'] = quality
        return context


def product_search(request):
    query = request.GET.get('q', '').strip()  # Отримуємо текст запиту
    products = Product.objects.none()  # Ініціалізуємо порожній queryset

    # Якщо є пошуковий запит, виконуємо пошук
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

        # Сортування результатів
        filter_option = request.GET.get('filter')
        if filter_option == 'price':
            products = products.order_by('price')  # Сортувати за ціною (зростання)
        elif filter_option == 'price_desc':
            products = products.order_by('-price')  # Сортувати за ціною (спадання)
        elif filter_option == 'new':
            products = products.order_by('-created_at')  # Сортувати за новизною

    return render(request, 'products/product_search.html', {
        'products': products,
        'query': query
    })


def product_autocomplete(request):
    # Отримання запиту "q" із запиту GET
    query = request.GET.get('q', '').strip()  # Очищення пробілів
    if not query:  # Якщо запит пустий
        return JsonResponse([], safe=False)  # Повернути порожній список

    # Отримання мови, якщо ваш сайт підтримує мультимовність
    language = get_language()

    # Пошук продуктів за назвою чи описом
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    )

    # Якщо є поле `language` у моделі, додайте фільтрацію за мовою
    if hasattr(Product, 'language'):
        products = products.filter(language=language)

    # Форматування відповіді: повертаємо лише id і name, лімітуючи до 10 результатів
    products = products.values('id', 'name')[:10]

    # Повернення результатів у форматі JSON
    return JsonResponse(list(products), safe=False)

