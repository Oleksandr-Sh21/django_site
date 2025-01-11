import uuid

from django.conf import settings
from django.db import models

from products.models import Product


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Очікує'
        COMPLETED = 'COMPLETED', 'Завершено'
        CANCELLED = 'CANCELLED', 'Скасовано'

    class PaymentStatus(models.TextChoices):
        PAID = "PAID", "Оплачено"
        NOT_PAID = "NOT_PAID", "Не оплачено"
        CASH_ON_DELIVERY = "CASH_ON_DELIVERY", "Оплата при отриманні"

    class DeliveryMethod(models.TextChoices):
        BRANCH = 'branch', 'Відділення'
        PARCEL_LOCKER = 'parcel_locker', 'Поштомат'
        COURIER = 'courier', 'Кур\'єр'

    class PaymentMethod(models.TextChoices):
        CASH_ON_DELIVERY = 'cash_on_delivery', 'Оплата при отриманні'
        CARD = 'card', 'Оплата карткою'

    order_number = models.ImageField(max_length=55, unique=True, editable=False, verbose_name="Номер замовлення")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Користувач',
        blank=True,
        null=True,
    )

    customer_name = models.CharField(max_length=255, verbose_name="Ім'я та Прізвище", blank=True, null=True)
    customer_email = models.EmailField(verbose_name="Email", blank=True, null=True)
    customer_phone = models.CharField(max_length=20, verbose_name="Телефон", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')

    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        verbose_name='Статус'
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Загальна сума'
    )

    delivery_method = models.CharField(
        max_length=30,
        choices=DeliveryMethod.choices,
        default=DeliveryMethod.PARCEL_LOCKER,
        verbose_name="Тип доставки"
    )
    shipping_address = models.TextField(verbose_name='Адреса доставки')

    payment_method = models.CharField(
        max_length=30,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH_ON_DELIVERY,
        verbose_name="Спосіб оплати"
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.NOT_PAID,
        verbose_name="Статус оплати"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'

    def __str__(self):
        return f"Замовлення #{self.order_number} від {self.user}"

    def save(self, *args, **kwargs):
        # Генеруємо унікальний номер замовлення, якщо його ще немає
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_order_number():
        """Генерація унікального номера замовлення."""
        return str(uuid.uuid4())[:8].upper()


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Замовлення'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='Кількість')

    @property
    def price(self):
        """Ціна товару (з врахуванням знижки, якщо є)."""
        return self.product.discount_price if self.product.discount_price else self.product.price

    def get_total_price(self):
        return self.quantity * self.price

    class Meta:
        verbose_name = 'Товар у замовленні'
        verbose_name_plural = 'Товари у замовленні'

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"