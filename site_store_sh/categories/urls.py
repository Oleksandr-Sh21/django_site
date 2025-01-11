from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    path('category/<slug:category_slug>/', views.CategoryProduct.as_view(), name='product_by_category'),
]
