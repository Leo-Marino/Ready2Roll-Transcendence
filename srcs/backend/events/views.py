from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .recommender import build_feed
from .models import Event
from .serializers import EventSerializer, FeedEventSerializer

class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

class OwnerEventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return only the events created by the user making the request
        return Event.objects.filter(organizer=self.request.user).order_by('-created_at')


# class FeedView(generics.ListAPIView):
#     """GET /api/feed/  -> published (active) events that have a video/image, newest first."""
#     serializer_class = FeedEventSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return (
#             Event.objects
#             .filter(status__iexact='active', media__media_url__isnull=False)
#             .exclude(media__media_url='')
#             .select_related('organizer')
#             .prefetch_related('media')
#             .distinct()
#             .order_by('-created_at')
#         )

class FeedView(generics.ListAPIView):
    """GET /api/feed/?mode=for_you|discover|following"""
    serializer_class = FeedEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        mode = request.query_params.get('mode', 'for_you')
        ids = build_feed(request.user, mode)
        events = (Event.objects.filter(id__in=ids)
                  .select_related('organizer').prefetch_related('media'))
        by_id = {e.id: e for e in events}
        ordered = [by_id[i] for i in ids if i in by_id]
        return Response(self.get_serializer(ordered, many=True).data)
