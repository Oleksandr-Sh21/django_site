from django.shortcuts import render
from django.views.generic import ListView
from categories.models import Category
from products.models import Product, Attribute, ProductAttribute


class CategoryProduct(ListView):
    model = Product
    template_name = 'categories/products_by_category.html'
    context_object_name = 'products'

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        queryset = Product.objects.filter(category__slug=category_slug)

        # Отримання параметра сортування
        filter_option = self.request.GET.get('filter')
        if filter_option == 'price':
            queryset = queryset.order_by('price')  # Сортувати за ціною (зростання)
        elif filter_option == 'price_desc':
            queryset = queryset.order_by('-price')  # Сортувати за ціною (спадання)
        elif filter_option == 'new':
            queryset = queryset.order_by('-created_at')  # Сортувати за датою створення (новинки)

        # Отримання параметрів для фільтрації по характеристиках
        attribute_values = self.request.GET.getlist('attributes')  # Наприклад, ['1', '2']
        if attribute_values:
            queryset = queryset.filter(attributes__attribute_value__id__in=attribute_values).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.get(slug=self.kwargs.get('category_slug'))

        context['category'] = category
        context['title'] = category.name
        context['filter'] = self.request.GET.get('filter', '')  # Додати поточний фільтр

        # Отримати всі продукти в обраній категорії
        products_in_category = Product.objects.filter(category=category)

        # Отримати всі ProductAttribute для цих продуктів
        product_attributes = ProductAttribute.objects.filter(product__in=products_in_category)

        # Отримати унікальні атрибути через AttributeValue
        attribute_ids = product_attributes.values_list('attribute_value__attribute', flat=True).distinct()

        # Отримати унікальні атрибути
        attributes = Attribute.objects.filter(id__in=attribute_ids)
        selected_attributes = self.request.GET.getlist('attributes')

        context['attributes'] = attributes  # Унікальні характеристики для відображення
        context['selected_attributes'] = selected_attributes
        return context
