from django.urls import path
from .views import ReviewCreate, ReplyCreate, ReactView

app_name = 'reviews'

urlpatterns = [
    path('review/<int:product_id>/create/', ReviewCreate.as_view(), name='review_create'),
    path('reply/<int:review_id>/create/', ReplyCreate.as_view(), name='reply_create'),
    path('react/', ReactView.as_view(), name='react'),
]
