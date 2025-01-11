from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView

from cart.models import CartItem
from orders.models import Order

from products.models import Product
from users.forms import LoginUserForm, RegisterUserForm, UserPasswordChangeForm, ProfileUserForm
from users.models import Favorite


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    extra_context = {'title': 'Реєстрація'}
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save(commit=False)
        phone_number = form.cleaned_data.get('phone_number')
        if phone_number:
            user.phone_number = phone_number
        user.save()
        return super().form_valid(form)


class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change.html'


class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'users/password_reset_email.html'
    template_name = 'users/password_reset_form.html'  # Шаблон для самої форми
    success_url = reverse_lazy('users:password_reset_done')  # URL після успішного відправлення листа


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy("users:password_reset_complete")


class Profile(LoginRequiredMixin, DetailView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    login_url = "/users/login/"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        # Викликаємо базовий метод для отримання стандартного контексту
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        # Додаємо дані для вкладок
        context['orders'] = Order.objects.filter(user=user).order_by('-created_at')
        context['favorites'] = Favorite.objects.filter(user=user)

        # Додаткові дані
        context['title'] = 'Профіль'
        context['active_tab'] = self.request.GET.get('tab', 'profile-overview')  # Для керування активною вкладкою

        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/edit_profile.html'

    def get_success_url(self):
        return reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


class AddFavorite(LoginRequiredMixin, View):
    def post(self, request, product_id):
        try:
            user = request.user
            product = get_object_or_404(Product, id=product_id)

            # Використовуємо get_or_create
            favorite, created = Favorite.objects.get_or_create(user=user, product=product)

            if created:
                message = "Товар додано до вподобаних."
            else:
                message = "Товар видалено з вподобаних."
                favorite.delete()

            return JsonResponse({
                "message": message,
                "product_name": product.name,
            }, status=200)
        except Product.DoesNotExist:
            return JsonResponse({"error": "Продукт не знайдено"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class RemoveFavorite(LoginRequiredMixin, View):

    def post(self, request, product_id):
        try:
            user = request.user
            product = get_object_or_404(Product, id=product_id)

            # Видаляємо вподобане, якщо існує
            favorite = Favorite.objects.filter(user=user, product=product)
            if favorite.exists():
                favorite.delete()
                return JsonResponse({
                    "message": "Товар видалено з вподобаних.",
                    "product_name": product.name,
                }, status=200)
            else:
                return JsonResponse({
                    "error": "Товар не знайдено у вподобаних."
                }, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

