from django.contrib import admin

from products.models import Product, ProductImage

from django.contrib import admin
from .models import Product, Tag, Attribute, AttributeValue, ProductAttribute


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1  # Кількість додаткових порожніх рядків
    verbose_name = "Характеристика продукту"
    verbose_name_plural = "Характеристики продукту"


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Кількість додаткових порожніх рядків для додавання нових зображень
    verbose_name = "Зображення продукту"
    verbose_name_plural = "Зображення продукту"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'created_at', 'status', 'available', 'category')
    list_display_links = ('id', 'name')
    list_filter = ('status', 'available', 'category', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name', )}
    ordering = ['-created_at']
    list_editable = ('status', 'available')
    filter_horizontal = ('tags', )
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductImageInline, ProductAttributeInline]  # Включаємо інлайн для характеристик


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'slug')
    list_display_links = ('id', 'tag')
    prepopulated_fields = {'slug': ('tag', )}
    search_fields = ('tag',)


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'attribute', 'value')
    list_display_links = ('id', 'attribute')
    search_fields = ('attribute__name', 'value')


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'attribute_value')
    list_display_links = ('id', 'product')
    search_fields = ('product__name', 'attribute_value__value')

