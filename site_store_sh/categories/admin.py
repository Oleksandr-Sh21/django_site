from django.contrib import admin
from categories.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_display_links = ('id', 'name')

    prepopulated_fields = {'slug': ('name',)}