from django.urls import path
from .views import notification_list_view, unread_count_view, mark_all_read_view

urlpatterns = [
    path('', notification_list_view, name='notification-list'),
    path('unread-count/', unread_count_view, name='notification-unread-count'),
    path('read/', mark_all_read_view, name='notification-mark-read'),
]
