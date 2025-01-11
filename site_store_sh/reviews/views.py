from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import CreateView, FormView

from products.models import Product
from reviews.forms import ReviewForm, ReplyForm, ReactionForm
from reviews.models import Review, Reply, Reaction


class ReviewCreate(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm

    def form_valid(self, form):
        """Прив'язує користувача і продукт до відгуку"""
        # Отримуємо об'єкт продукту за допомогою `product_id`
        product = get_object_or_404(Product, id=self.kwargs['product_id'])
        form.instance.user = self.request.user
        form.instance.product = product  # Прив'язуємо продукт до відгуку
        self.object = form.save()  # Зберігаємо форму
        return JsonResponse({'message': 'Відгук успішно створено!'})  # JSON-відповідь

    def form_invalid(self, form):
        """Обробка помилок у випадку невалідних даних"""
        return JsonResponse({'errors': form.errors}, status=400)


class ReplyCreate(LoginRequiredMixin, CreateView):
    model = Reply
    form_class = ReplyForm

    def form_valid(self, form):
        """Прив'язує користувача і відгук до відповіді"""
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        form.instance.user = self.request.user
        form.instance.review = review  # Прив'язуємо відповідь до відгуку
        self.object = form.save()  # Зберігаємо форму
        return JsonResponse({'message': 'Коментар успішно створено!'})  # JSON-відповідь

    def form_invalid(self, form):
        """Обробка помилок у випадку невалідних даних"""
        return JsonResponse({'errors': form.errors}, status=400)


def load_more_comments(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    offset = int(request.GET.get('offset', 0))  # Поточний офсет
    comments = Reply.objects.filter(review=review).order_by('-created_at')[offset:offset + 3]
    has_more = Reply.objects.filter(review=review).count() > offset + 3

    data = {
        'comments': [{'user': comment.user.username, 'content': comment.content} for comment in comments],
        'has_more': has_more,
    }
    return JsonResponse(data)


class ReactView(FormView):
    form_class = ReactionForm

    def form_valid(self, form):
        reaction = form.save(commit=False)
        reaction.user = self.request.user

        # Перевірка чи користувач автентифікований
        if not self.request.user.is_authenticated:
            return JsonResponse({'error': 'Not authenticated'}, status=403)

        review = form.cleaned_data.get('review')
        reply = form.cleaned_data.get('reply')

        # Знаходимо вже існуючу реакцію цього користувача до об'єкта
        existing_reaction = Reaction.objects.filter(
            user=self.request.user,
            review=review,
            reply=reply
        ).first()

        if existing_reaction:
            # Якщо реакція вже існує
            if existing_reaction.reaction == reaction.reaction:
                # Якщо користувач повторно натиснув ту ж реакцію, видаляємо її
                existing_reaction.delete()
            else:
                # Якщо реакція інша, оновлюємо значення
                existing_reaction.reaction = reaction.reaction
                existing_reaction.save()
        else:
            # Якщо ж реакції не було, створюємо нову
            reaction.save()

        target = review if review else reply

        return JsonResponse({
            'likes': target.like_count(),
            'dislikes': target.dislike_count(),
        })

    def form_invalid(self, form):
        return JsonResponse({'error': 'Invalid form data', 'details': form.errors}, status=400)