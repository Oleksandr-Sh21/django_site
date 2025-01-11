from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from products.models import Product


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )  # Автор відгуку
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )  # Продукт
    rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )  # Оцінка (1-5)
    content = models.TextField()  # Текст відгуку
    created_at = models.DateTimeField(auto_now_add=True)  # Дата створення
    updated_at = models.DateTimeField(auto_now=True)  # Дата останнього оновлення
    advantages = models.TextField(blank=True, null=True)  # Переваги
    disadvantages = models.TextField(blank=True, null=True)  # Недоліки

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"

    def __str__(self):
        return f'{self.user.get_full_name()} - {self.product.name}'

    def like_count(self):
        """Повертає кількість лайків для відгуку"""
        return self.reactions.filter(reaction=Reaction.LIKE).count()

    def dislike_count(self):
        """Повертає кількість дизлайків для відгуку"""
        return self.reactions.filter(reaction=Reaction.DISLIKE).count()


class Reply(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='replies'
    )  # Відгук, до якого додається відповідь
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )  # Автор відповіді
    content = models.TextField()  # Текст відповіді
    created_at = models.DateTimeField(auto_now_add=True)  # Дата створення
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )  # Для вкладених відповідей

    class Meta:
        verbose_name = "Відповідь"
        verbose_name_plural = "Відповіді"

    def __str__(self):
        return f'Reply by {self.user.get_full_name()} to {self.review}'

    def like_count(self):
        """Повертає кількість лайків для відповіді"""
        return self.reactions.filter(reaction=Reaction.LIKE).count()

    def dislike_count(self):
        """Повертає кількість дизлайків для відповіді"""
        return self.reactions.filter(reaction=Reaction.DISLIKE).count()


class Reaction(models.Model):
    LIKE = 1
    DISLIKE = -1
    REACTION_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )  # Користувач, який залишив реакцію
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reactions'
    )  # Реакція на відгук
    reply = models.ForeignKey(
        Reply,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reactions'
    )  # Реакція на відповідь
    reaction = models.SmallIntegerField(choices=REACTION_CHOICES)  # Лайк або дизлайк
    created_at = models.DateTimeField(auto_now_add=True)  # Дата створення

    class Meta:
        unique_together = ('user', 'review', 'reply')  # Унікальна реакція для кожного користувача
        verbose_name = "Реакція"
        verbose_name_plural = "Реакції"

    def __str__(self):
        target = self.review or self.reply
        return f"{self.user.get_full_name()} reacted to {target}"
