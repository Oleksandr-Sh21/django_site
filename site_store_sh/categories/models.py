from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назва категорії")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL-ідентифікатор")
    image = models.ImageField(upload_to='photos/category/%Y/%m/%d/', blank=True, null=True, default=None, verbose_name="Зображення")

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

    def __str__(self):
        return self.name
