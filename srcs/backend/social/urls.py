from django.urls import path
from .views import toggle_follow_view

urlpatterns = [
    path('follow/<int:user_id>/', toggle_follow_view, name='toggle_follow'),
]
