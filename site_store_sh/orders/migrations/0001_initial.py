# Generated by Django 5.1.2 on 2024-12-18 16:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0004_remove_product_image_productimage'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.ImageField(editable=False, max_length=55, unique=True, upload_to='', verbose_name='Номер замовлення')),
                ('customer_name', models.CharField(blank=True, max_length=255, null=True, verbose_name="Ім'я та Прізвище")),
                ('customer_email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email')),
                ('customer_phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='Телефон')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')),
                ('status', models.CharField(choices=[('PENDING', 'Очікує'), ('COMPLETED', 'Завершено'), ('CANCELLED', 'Скасовано')], default='PENDING', max_length=20, verbose_name='Статус')),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Загальна сума')),
                ('delivery_method', models.CharField(choices=[('self_delivery_of_mail', 'Самовивіз'), ('post_office', 'Відділення пошти'), ('courier', "Кур'єр")], default='post_office', max_length=30, verbose_name='Тип доставки')),
                ('shipping_address', models.TextField(verbose_name='Адреса доставки')),
                ('payment_method', models.CharField(choices=[('cash_on_delivery', 'Оплата при отриманні'), ('card', 'Оплата карткою')], default='cash_on_delivery', max_length=30, verbose_name='Спосіб оплати')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='Користувач')),
            ],
            options={
                'verbose_name': 'Замовлення',
                'verbose_name_plural': 'Замовлення',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Кількість')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.order', verbose_name='Замовлення')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='order_items', to='products.product', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Товар у замовленні',
                'verbose_name_plural': 'Товари у замовленні',
            },
        ),
    ]
