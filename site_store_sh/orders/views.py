import requests
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from liqpay import LiqPay

from django.conf import settings
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView

from cart.models import Cart
from orders.forms import CheckoutForm
from orders.models import Order, OrderItem


class NovaPoshtaAPI:
    BASE_URL = "https://api.novaposhta.ua/v2.0/json/"

    def __init__(self):
        self.api_key = settings.NOVA_POSHTA_API_KEY

    def get_cities(self, query=None):
        """Отримати список міст із частковим пошуком."""
        payload = {
            "apiKey": self.api_key,
            "modelName": "Address",
            "calledMethod": "getCities",
            "methodProperties": {}
        }
        if query:  # Використовуємо FindByString для часткового пошуку
            payload["methodProperties"]["FindByString"] = query

        response = requests.post(self.BASE_URL, json=payload)
        full_data = response.json()

        # Перевірка відповіді API
        if not full_data.get('success'):
            return []

        # Фільтруємо тільки потрібні дані
        cities = full_data.get('data', [])
        filtered_cities = [
            {
                "name": city["Description"],
                "ref": city["Ref"],
                "area": city["AreaDescription"]
            }
            for city in cities
        ]
        return filtered_cities

    def get_warehouses(self, city_ref, delivery_method):
        """Отримати список відділень для вказаного міста."""
        payload = {
            "apiKey": self.api_key,
            "modelName": "Address",
            "calledMethod": "getWarehouses",
            "methodProperties": {
                "CityRef": city_ref,
            }
        }
        response = requests.post(self.BASE_URL, json=payload)
        full_data = response.json()

        # Перевірка відповіді API
        if not full_data.get('success'):
            return []

        # Фільтруємо тільки потрібні дані
        warehouses = full_data.get('data', [])

        ref_warehouse = []
        if delivery_method == "post_office":
            ref_warehouse = ['95dc212d-479c-4ffb-a8ab-8c1b9073d0bc', 'f9316480-5f2d-425d-bc2c-ac7cd29decf0']
        if delivery_method == "parcel_locker":
            ref_warehouse = ['6f8c7162-4b72-4b0a-88e5-906948c6a92f', '841339c7-591a-42e2-8233-7a0a00f0ed6f',
                             '9a68df70-0267-42a8-bb5c-37f427e36ee4']

        filtered_warehouses = [
            {
                "name": warehouse["Description"],
                "ref": warehouse["Ref"],
                "number": warehouse["Number"]
            }
            for warehouse in warehouses
            if warehouse['TypeOfWarehouse'] not in ref_warehouse
        ]
        return filtered_warehouses

    def get_streets(self, city_ref, query=None):
        """Отримати список вулиць із можливістю часткового пошуку."""
        payload = {
            "apiKey": self.api_key,
            "modelName": "AddressGeneral",
            "calledMethod": "getStreet",
            "methodProperties": {
                "CityRef": city_ref,
            }
        }
        if query:  # Використовуємо FindByString для часткового пошуку
            payload["methodProperties"]["FindByString"] = query

        response = requests.post(self.BASE_URL, json=payload)
        full_data = response.json()

        # Перевірка відповіді API
        if not full_data.get('success'):
            return []

        # Фільтруємо тільки потрібні дані
        streets = full_data.get('data', [])
        filtered_streets = [
            {
                "name": street["Description"],
                "ref": street["Ref"]
            }
            for street in streets
        ]
        return filtered_streets


class GetCitiesView(View):
    """Динамічне завантаження міст із пошуком."""

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()  # Отримуємо текст пошуку
        if len(query) < 3:  # Не виконуємо пошук, якщо введено менше 3 символів
            return JsonResponse({"results": []})

        np_api = NovaPoshtaAPI()
        all_cities = np_api.get_cities(query=query)  # Передаємо часткову назву міста

        # Форматуємо результати для використання на фронтенді
        filtered_cities = [
            {
                "id": city["ref"],
                "text": city['name']
            }
            for city in all_cities
        ]
        return JsonResponse({"results": filtered_cities})


class GetWarehousesView(View):
    """Динамічне завантаження складів для вибраного міста."""

    def get(self, request, *args, **kwargs):
        city_ref = request.GET.get("city_ref")
        delivery_method = request.GET.get("delivery_method")
        if not city_ref:
            return JsonResponse({"error": "CityRef is required"}, status=400)

        np_api = NovaPoshtaAPI()
        warehouses = np_api.get_warehouses(city_ref, delivery_method)

        return JsonResponse(warehouses, safe=False)


class GetStreetsView(View):
    """Динамічне завантаження вулиць для вибраного міста із пошуком."""

    def get(self, request, *args, **kwargs):
        city_ref = request.GET.get("city_ref")
        query = request.GET.get('q', '').strip()  # Отримуємо текст пошуку
        if not city_ref:
            return JsonResponse({"error": "CityRef is required"}, status=400)

        if len(query) < 3:  # Не виконуємо пошук, якщо введено менше 3 символів
            return JsonResponse({"results": []})

        np_api = NovaPoshtaAPI()
        streets = np_api.get_streets(city_ref, query=query)

        # Форматуємо результати для використання на фронтенді
        filtered_streets = [
            {
                "id": street["ref"],
                "text": street['name']
            }
            for street in streets
        ]
        return JsonResponse({"results": filtered_streets})


class CheckoutView(View):
    """Сторінка оформлення замовлення."""
    template_name = 'orders/checkout.html'

    def get(self, request, *args, **kwargs):
        form = CheckoutForm(initial={'user': request.user if request.user.is_authenticated else None})
        cart = Cart.objects.get_or_create_cart(request)
        cart_items = cart.items.all()

        return render(request, self.template_name, {
            'form': form,
            'cart_items': cart_items,
            'total_price': sum(item.product.price * item.quantity for item in cart_items),
        })

    def post(self, request, *args, **kwargs):
        form = CheckoutForm(request.POST, initial={'user': request.user if request.user.is_authenticated else None})
        cart = Cart.objects.get_or_create_cart(request)
        cart_items = cart.items.all()

        if not form.is_valid():
            print("Form is not valid")
            print("Form errors:", form.errors)

        if not cart_items.exists():
            print("Cart is empty")
            print("Cart items:", list(cart_items))

        if form.is_valid() and cart_items.exists():
            with transaction.atomic():
                shipping_address = self.get_shipping_address(form.cleaned_data)
                payment_method = form.cleaned_data['payment_method']

                order = Order.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    customer_name=form.cleaned_data['customer_name'],
                    customer_email=form.cleaned_data['customer_email'],
                    customer_phone=form.cleaned_data['customer_phone'],
                    delivery_method=form.cleaned_data['delivery_method'],
                    payment_method=payment_method,
                    shipping_address=shipping_address,
                    total_price=0,
                )

                # Додаємо товари до замовлення
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity
                    )

                # Обчислюємо загальну суму замовлення
                order.total_price = sum(item.product.price * item.quantity for item in cart_items)

                # Встановлення статусу оплати
                if payment_method == 'cash_on_delivery':
                    order.payment_status = Order.PaymentStatus.CASH_ON_DELIVERY
                else:
                    order.payment_status = Order.PaymentStatus.NOT_PAID

                order.save()

                # Очищення кошика після успішного створення замовлення
                cart.items.all().delete()

                if payment_method == 'cash_on_delivery':
                    return redirect('orders:order_success', order_id=order.id)
                else:
                    return redirect('orders:pay_view', order_id=order.id)

        # У випадку помилок форми або порожнього кошика
        return render(request, self.template_name, {
            'form': form,  # Передаємо форму з помилками
            'cart_items': cart_items,
            'total_price': sum(item.product.price * item.quantity for item in cart_items),
        })

    def get_shipping_address(self, cleaned_data):
        """Формує повну адресу доставки на основі введених даних."""
        delivery_method = cleaned_data['delivery_method']
        if delivery_method == Order.DeliveryMethod.BRANCH:
            return f"Відділення: {cleaned_data.get('branch', '')}"
        elif delivery_method == Order.DeliveryMethod.PARCEL_LOCKER:
            return f"Поштомат: {cleaned_data.get('parcel_locker', '')}"
        elif delivery_method == Order.DeliveryMethod.COURIER:
            street = cleaned_data.get('street', '')
            house = cleaned_data.get('house_number', '')
            apartment = cleaned_data.get('apartment_number', '')
            return f"{street}, буд. {house}, кв. {apartment}" if apartment else f"{street}, буд. {house}"
        return "Адреса не вказана"


class PayView(TemplateView):
    template_name = 'orders/pay.html'

    def get(self, request, *args, **kwargs):
        order_id = kwargs['order_id']
        order = Order.objects.get(id=order_id)
        liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)

        server_url = request.build_absolute_uri(reverse('orders:pay_callback'))

        params = {
            'action': 'pay',
            'amount': f'{order.total_price}',
            'currency': 'UAH',
            'description': 'Payment for Item',
            'order_id': f'{order.order_number}',
            'version': '3',
            'sandbox': 1, # sandbox mode, set to 1 to enable it
            'server_url': server_url, # url to callback view
            'result_url': request.build_absolute_uri(reverse('order_success', kwargs={'order_id': order.id})),
        }
        signature = liqpay.cnb_signature(params)
        data = liqpay.cnb_data(params)
        return render(request, self.template_name, {'signature': signature, 'data': data})


@method_decorator(csrf_exempt, name='dispatch')
class PayCallbackView(View):
    def post(self, request, *args, **kwargs):
        liqpay = LiqPay("sandbox", "sandbox")
        data = request.POST.get('data')
        signature = request.POST.get('signature')

        if not data or not signature:
            return HttpResponse("Invalid callback data", status=400)

        sign = liqpay.str_to_sign("sandbox" + data + "sandbox")
        if sign == signature:
            response = liqpay.decode_data_from_str(data)
            print('callback data', response)

            if 'order_id' not in response:
                return HttpResponse("Missing order_id", status=400)

            try:
                order = Order.objects.get(order_number=response['order_id'])
                order.payment_status = Order.PaymentStatus.PAID
                order.save()
            except Order.DoesNotExist:
                return HttpResponse("Order not found", status=404)

            return HttpResponse("Callback processed successfully")
        else:
            return HttpResponse("Invalid signature", status=400)


class OrderSuccess(TemplateView):
    template_name = 'orders/order_success.html'
    model = Order

    def get_context_data(self, **kwargs):
        order = Order.objects.filter(id=self.kwargs['order_id']).first()
        context = super().get_context_data(**kwargs)
        context['order_id'] = self.kwargs['order_id'] # Передаємо order_id в контекст шаблону
        context['order_number'] = order.order_number
        return context
