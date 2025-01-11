from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm, UserChangeForm
from django import forms
from datetime import date


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логін', widget=forms.TextInput(attrs={'class': 'auth-form-control pl-5'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'auth-form-control pl-5'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логін', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Повторіть пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name', 'date_birthday', 'phone_number', 'password1',
                  'password2']

        labels = {
            'username': 'Логін',
            'email': 'Електронна пошта',
            'first_name': "Ім'я",
            'last_name': 'Прізвище',
            'date_birthday': 'Дата народження',
            'phone_number': 'Номер телефону',
        }

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_birthday': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date', 'max': date.today().strftime('%Y-%m-%d')}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError('Електронна адреса вже зареєстрована')
        return email


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Старий пароль", widget=forms.PasswordInput())
    new_password1 = forms.CharField(label="Новий пароль", widget=forms.PasswordInput())
    new_password2 = forms.CharField(label="Повторіть пароль", widget=forms.PasswordInput())


class ProfileUserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'date_birthday', 'phone_number', 'email')

        labels = {
            'email': 'Електронна пошта',
            'first_name': "Ім'я",
            'last_name': 'Прізвище',
            'date_birthday': 'Дата народження',
            'phone_number': 'Номер телефону',
        }

        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_birthday': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date', 'max': date.today().strftime('%Y-%m-%d')},
                format='%Y-%m-%d'),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
