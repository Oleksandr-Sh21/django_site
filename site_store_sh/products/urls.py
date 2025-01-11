from django.urls import path

from reviews.views import load_more_comments
from . import views

urlpatterns = [
    path('', views.ListProduct.as_view(), name='home'),
    path('product/<slug:product_slug>/', views.DetailProduct.as_view(), name='detail'),
    path('review/<int:review_id>/comments/load_more/', load_more_comments, name='load_more_comments'),
    path('search/', views.product_search, name='product_search'),
    path('autocomplete/', views.product_autocomplete, name='product_autocomplete'),
]
