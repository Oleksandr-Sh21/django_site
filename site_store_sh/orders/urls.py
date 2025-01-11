from django.urls import path
from .views import CheckoutView, GetWarehousesView, GetCitiesView, GetStreetsView, OrderSuccess, PayView, \
    PayCallbackView

app_name = 'orders'

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('api/cities/', GetCitiesView.as_view(), name='get_cities'),
    path('api/warehouses/', GetWarehousesView.as_view(), name='get_warehouses'),
    path('api/streets/', GetStreetsView.as_view(), name='get_streets'),
    path('order_success/<int:order_id>/', OrderSuccess.as_view(), name='order_success'),
    path('pay/<int:order_id>/', PayView.as_view(), name='pay_view'),
    path('pay-callback/', PayCallbackView.as_view(), name='pay_callback'),
]

