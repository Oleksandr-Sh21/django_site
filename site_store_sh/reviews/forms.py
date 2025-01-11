from django import forms

from .models import Review, Reply, Reaction


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'content', 'advantages', 'disadvantages']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1, 'max': 5, 'step': 1,
                'class': 'form-control',
                'placeholder': 'Оцініть продукт від 1 до 5'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Напишіть ваш відгук',
                'rows': 5
            }),
            'advantages': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Перелічіть переваги продукту (необов’язково)',
                'rows': 3
            }),
            'disadvantages': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Перелічіть недоліки продукту (необов’язково)',
                'rows': 3
            }),
        }
        labels = {
            'rating': 'Оцінка',
            'content': 'Відгук',
            'advantages': 'Переваги',
            'disadvantages': 'Недоліки',
        }
        help_texts = {
            'rating': 'Оцінка має бути від 1 до 5.',
        }


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Напишіть ваш коментар',
                'rows': 5
            }),
        }
        labels = {
            'content': 'Коментар',
        }


class ReactionForm(forms.ModelForm):
    class Meta:
        model = Reaction
        fields = ['reaction', 'review', 'reply']
        widgets = {
            'reaction': forms.HiddenInput(),
            'review': forms.HiddenInput(),
            'reply': forms.HiddenInput(),
        }