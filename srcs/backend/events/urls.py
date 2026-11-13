from django.urls import path
from .views import EventListCreateView, EventDetailView, OwnerEventListView, FeedView, TagListView, event_ask_view
from .search_views import search_view

urlpatterns = [
		path('tags/', TagListView.as_view(), name='tag-list'),
		path('events/', EventListCreateView.as_view(), name='event-list-create'),
		path('events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
		path('feed/', FeedView.as_view(), name='feed'),
		path('owner/events/', OwnerEventListView.as_view(), name='owner-events'),
		path('events/<int:event_id>/ask/', event_ask_view, name='event-ask'),
		path('search/', search_view, name='search'),
]
