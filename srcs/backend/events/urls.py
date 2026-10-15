from django.urls import path
from .views import EventListCreateView, EventDetailView, OwnerEventListView

urlpatterns = [
		path('events/', EventListCreateView.as_view(), name='event-list-create'),
		path('events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
		path('owner/events/', OwnerEventListView.as_view(), name='owner-events'),
]
