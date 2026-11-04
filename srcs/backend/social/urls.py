from django.urls import path
from .views import (toggle_follow_view, event_comments_view, toggle_like_view,
                    toggle_comment_reaction_view, ChatHistoryView,
					ContactsView, UnreadMessagesCountView, liked_events_view)

urlpatterns = [
    path('follow/<int:user_id>/', toggle_follow_view, name='toggle_follow'),
	path('events/<int:event_id>/like/', toggle_like_view, name='toggle_like'),
	path('events/<int:event_id>/comments/', event_comments_view, name='event_comments'),
	path('comments/<int:comment_id>/react/', toggle_comment_reaction_view, name='toggle_comment_reaction'),
	#path('events/<int:event_id>/like/', toggle_like_view, name='toggle_like'),
	#path('users/<int:user_id>/followers/', get_followers_view, name='get_followers'),
    #path('users/<int:user_id>/following/', get_following_view, name='get_following'),
	path('messages/<int:user_id>/', ChatHistoryView.as_view(), name='chat-history'),
	path('messages/unread-count/', UnreadMessagesCountView.as_view(), name='chat-unread-count'),
	path('contacts/', ContactsView.as_view(), name='chat-contacts'),
	path('liked-events/', liked_events_view, name='liked_events')
]
