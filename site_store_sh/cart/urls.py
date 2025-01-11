from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('view/', views.GetCartView.as_view(), name='view_cart'),
    path('add/<int:product_id>/', views.AddToCartView.as_view(), name='add_to_cart'),  # Додати товар
    path('update/<int:product_id>/', views.UpdateCartView.as_view(), name='update_cart'),  # Оновити кількість
    path('remove/<int:product_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),  # Видалити товар
]
