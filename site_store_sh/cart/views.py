import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from cart.models import Cart, CartItem
from products.models import Product


class GetCartView(View):
    def get(self, request):
        """Отримати дані кошика у форматі JSON."""
        try:
            cart = Cart.objects.get_or_create_cart(request)  # Отримуємо лише Cart
            items = cart.items.select_related('product')
            total_price = sum(item.quantity * (item.product.discount_price or item.product.price) for item in items)

            data = {
                "items": [
                    {
                        "id": item.product.id,
                        "name": item.product.name,
                        "image_url": item.product.images.first().image.url if item.product.images.exists() else "https://via.placeholder.com/150",
                        "quantity": item.quantity,
                        "price": float(item.product.price),
                        "discount_price": float(item.product.discount_price) if item.product.discount_price else None,
                        "total_price": float(item.quantity * (item.product.discount_price or item.product.price)),
                    }
                    for item in items
                ],
                "total_price": float(total_price),
            }
            return JsonResponse(data, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AddToCartView(View):
    def post(self, request, product_id):
        """Додати товар у кошик."""
        try:
            cart = Cart.objects.get_or_create_cart(request)  # Отримуємо лише Cart
            product = get_object_or_404(Product, id=product_id)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

            if not created:
                cart_item.quantity += 1
                cart_item.save()

            return JsonResponse({
                "message": "Товар додано або оновлено в кошику",
                "product_name": product.name,
                "quantity": cart_item.quantity,
            }, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Продукт не знайдено"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class UpdateCartView(View):
    def post(self, request, product_id):
        """Оновити кількість товару в кошику."""
        try:
            data = json.loads(request.body)
            change = int(data.get('quantity', 0))  # Отримуємо зміну кількості
            if change == 0:
                return JsonResponse({"error": "Неприпустима зміна кількості"}, status=400)

            cart = Cart.objects.get_or_create_cart(request)
            product = get_object_or_404(Product, id=product_id)
            cart_item = CartItem.objects.get(cart=cart, product=product)

            # Змінюємо кількість
            cart_item.quantity += change
            if cart_item.quantity <= 0:
                cart_item.delete()  # Видаляємо, якщо кількість <= 0
            else:
                cart_item.save()

            return JsonResponse({
                "message": "Кількість товару оновлено",
                "product_id": product_id,
                "quantity": cart_item.quantity,
            }, status=200)
        except CartItem.DoesNotExist:
            return JsonResponse({"error": "Товар не знайдено в кошику"}, status=404)
        except Product.DoesNotExist:
            return JsonResponse({"error": "Продукт не знайдено"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class RemoveFromCartView(View):
    def post(self, request, product_id):
        """Видалити товар з кошика."""
        try:
            cart = Cart.objects.get_or_create_cart(request)
            product = get_object_or_404(Product, id=product_id)
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.delete()

            return JsonResponse({
                "message": "Товар видалено з кошика",
                "product_id": product_id,
            }, status=200)
        except CartItem.DoesNotExist:
            return JsonResponse({"error": "Товар не знайдено в кошику"}, status=404)
        except Product.DoesNotExist:
            return JsonResponse({"error": "Продукт не знайдено"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)