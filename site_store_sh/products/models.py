from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.template.defaultfilters import slugify

from categories.models import Category


def translit_to_eng(s: str) -> str:
    d = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd',
        'е': 'e', 'є': 'ye', 'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'yi', 'й': 'y',
        'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
        'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh',
        'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ь': '', 'ю': 'yu', 'я': 'ya',
    }
    return ''.join(map(lambda x: d[x] if d.get(x, False) else x, s.lower()))


class Product(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубліковано'

    name = models.CharField(max_length=255, unique=True, verbose_name="Назва продукту")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL-ідентифікатор")
    description = models.TextField(verbose_name="Опис", blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                         verbose_name="Ціна зі знижкою")
    tags = models.ManyToManyField('Tag', blank=True, related_name="products", verbose_name="Теги")
    stock = models.PositiveIntegerField(verbose_name="Кількість на складі")
    available = models.BooleanField(default=True, verbose_name="Доступність")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products", verbose_name="Категорія")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")
    status = models.BooleanField(choices=Status.choices, default=Status.PUBLISHED)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(translit_to_eng(self.name))
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукти"
        ordering = ['-created_at']


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Продукт"
    )
    image = models.ImageField(
        upload_to='photos/products/%Y/%m/%d/',
        verbose_name="Зображення"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата завантаження")

    def __str__(self):
        return f"Зображення для {self.product.name}"


class Tag(models.Model):
    tag = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)


class Attribute(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назва характеристики")

    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="values", verbose_name="Характеристика")
    value = models.CharField(max_length=255, verbose_name="Значення")

    class Meta:
        verbose_name = "Значення характеристики"
        verbose_name_plural = "Значення характеристик"

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="attributes", verbose_name="Продукт")
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE, verbose_name="Значення характеристики")

    class Meta:
        verbose_name = "Характеристика продукту"
        verbose_name_plural = "Характеристики продукту"

    def __str__(self):
        return f"{self.product.name} - {self.attribute_value}"

