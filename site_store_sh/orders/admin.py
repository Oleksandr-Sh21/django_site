from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'get_total_price')

    def price(self, obj):
        return obj.price
    price.short_description = "Ціна товару"

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = "Сума за товар"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number_link', 'customer_name', 'status', 'total_price', 'created_at', 'delivery_method')
    list_filter = ('status', 'delivery_method', 'payment_method', 'created_at')
    search_fields = ('order_number', 'customer_name', 'customer_email', 'customer_phone', 'user__username')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'total_price', 'shipping_address')
    inlines = [OrderItemInline]

    fieldsets = (
        ("Основна інформація", {
            'fields': ('order_number', 'status', 'payment_status', 'total_price', 'created_at', 'updated_at')
        }),
        ("Інформація про клієнта", {
            'fields': ('user', 'customer_name', 'customer_email', 'customer_phone')
        }),
        ("Доставка", {
            'fields': ('delivery_method', 'shipping_address')
        }),
        ("Оплата", {
            'fields': ('payment_method',)
        }),
    )

    def order_number_link(self, obj):
        """Додає посилання на замовлення за його номером."""
        return format_html('<a href="{}">{}</a>', f"/admin/orders/order/{obj.id}/change/", obj.order_number)

    order_number_link.short_description = "Номер замовлення"

    def has_add_permission(self, request):
        return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'get_total_price')
    list_filter = ('order', 'product')
    search_fields = ('order__order_number', 'product__name')
    readonly_fields = ('order', 'product', 'quantity', 'price', 'get_total_price')

    def price(self, obj):
        return obj.price
    price.short_description = "Ціна"

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = "Загальна сума"
