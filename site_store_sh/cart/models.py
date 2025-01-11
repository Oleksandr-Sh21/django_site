from django.conf import settings
from django.db import models

from products.models import Product


class CartManager(models.Manager):
    def get_or_create_cart(self, request):
        """Отримати або створити кошик для поточного користувача чи сесії."""
        if request.user.is_authenticated:
            # Для авторизованих користувачів
            cart, created = self.get_or_create(user=request.user, session_key=None)
        else:
            # Для неавторизованих користувачів
            session_key = request.session.session_key
            if not session_key:
                request.session.create()  # Створити нову сесію, якщо її немає
                session_key = request.session.session_key
            cart, created = self.get_or_create(user=None, session_key=session_key)
        return cart  # Повертаємо лише об'єкт Cart


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carts",
        verbose_name="Користувач",
        null=True,
        blank=True
    )
    session_key = models.CharField(
        max_length=40,
        verbose_name="Ключ сесії",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    objects = CartManager()

    def __str__(self):
        return f"Кошик користувача: {self.user or self.session_key}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Кошик'
        verbose_name_plural = 'Кошик'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", verbose_name="Кошик")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Кількість")