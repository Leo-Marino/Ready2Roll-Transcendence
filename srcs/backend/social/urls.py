from django.urls import path
from .views import toggle_follow_view, event_comments_view, toggle_like_view

urlpatterns = [
    path('follow/<int:user_id>/', toggle_follow_view, name='toggle_follow'),
	path('events/<int:event_id>/like/', toggle_like_view, name='toggle_like'),
	path('events/<int:event_id>/comments/', event_comments_view, name='event_comments'),

]
