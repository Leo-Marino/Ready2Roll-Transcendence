from django.urls import path
from .views import EventListCreateView, EventDetailView, OwnerEventListView, FeedView

urlpatterns = [
		path('events/', EventListCreateView.as_view(), name='event-list-create'),
		path('events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
		path('feed/', FeedView.as_view(), name='feed'),
		path('owner/events/', OwnerEventListView.as_view(), name='owner-events'),
]
