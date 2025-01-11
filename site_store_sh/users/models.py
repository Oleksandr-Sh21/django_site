from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

from products.models import Product


class User(AbstractUser):
    photo = models.ImageField(upload_to='photos/users/%Y/%m/%d/', default=None, blank=True, null=True,
                              verbose_name='Фотографія')
    date_birthday = models.DateTimeField(blank=True, null=True, verbose_name='Дата народження')
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Номер телефону')


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # Видаляємо вподобання, якщо користувача видалено
        related_name="favorites",  # Унікальне ім'я для зворотного зв'язку
        verbose_name='Користувач',
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,  # Видаляємо вподобання, якщо товар видалено
        verbose_name="Товар"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата створення"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата оновлення"
    )

    def __str__(self):
        return f"{self.user.username} вподобав {self.product.name}"

    class Meta:
        verbose_name = "Вподобане"
        verbose_name_plural = "Вподобані"
        unique_together = ("user", "product")