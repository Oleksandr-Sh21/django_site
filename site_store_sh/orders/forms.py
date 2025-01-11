from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    customer_name = forms.CharField(
        max_length=255,
        label="Ім'я та Прізвище",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Ваше ім'я"})
    )
    customer_email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "example@mail.com"})
    )
    customer_phone = forms.CharField(
        max_length=20,
        label="Телефон",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "+380 ХХХ ХХХ ХХХХ"})
    )
    delivery_method = forms.ChoiceField(
        choices=Order.DeliveryMethod.choices,
        label="Тип доставки",
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    payment_method = forms.ChoiceField(
        choices=Order.PaymentMethod.choices,
        label="Спосіб оплати",
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    city = forms.CharField(
        label="Введіть населений пункт",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Введіть населений пункт..."})
    )

    branch = forms.CharField(
        required=False,
        label="Номер або назва відділення",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Введіть номер або назву відділення..."})
    )

    parcel_locker = forms.CharField(
        required=False,
        label="Адреса або номер поштомату",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Введіть адресу або номер поштомату..."})
    )

    street = forms.CharField(
        required=False,
        label="Вулиця",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Введіть назву вулиці..."})
    )

    house_number = forms.CharField(
        required=False,
        label="Номер будинку",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Введіть номер будинку..."})
    )

    apartment_number = forms.CharField(
        required=False,
        label="Номер квартири",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Введіть номер квартири..."})
    )

    class Meta:
        model = Order
        fields = ['customer_name', 'customer_email', 'customer_phone',
                  'delivery_method', 'payment_method', 'city', 'branch', 'parcel_locker', 'street', 'house_number', 'apartment_number']

    def clean(self):
        cleaned_data = super().clean()
        delivery_method = cleaned_data.get('delivery_method')

        # Перевірка тільки для способу доставки "поштомат"
        if delivery_method == Order.DeliveryMethod.PARCEL_LOCKER:
            parcel_locker = cleaned_data.get('parcel_locker', '').strip()
            if not parcel_locker:
                self.add_error('parcel_locker', "Виберіть поштомат.")  # Залишаємо помилку, якщо поле порожнє

        # Перевірка для відділень
        elif delivery_method == Order.DeliveryMethod.BRANCH:
            if not cleaned_data.get('branch', '').strip():
                self.add_error('branch', "Виберіть відділення.")

        # Перевірка для кур'єрської доставки
        elif delivery_method == Order.DeliveryMethod.COURIER:
            if not cleaned_data.get('street', '').strip():
                self.add_error('street', "Введіть вулицю.")
            if not cleaned_data.get('house_number', '').strip():
                self.add_error('house_number', "Введіть номер будинку.")

        return cleaned_data

