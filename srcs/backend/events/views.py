from rest_framework import generics, permissions, serializers
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .recommender import build_feed
from .models import Event, Tag
from .serializers import EventSerializer, FeedEventSerializer
from events.serializers import FeedEventSerializer

import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle

from .ai import AIBusyError, ask_about_event

logger = logging.getLogger(__name__)

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
#         )events/views.py

class FeedView(generics.ListAPIView):
    """GET /api/feed/?mode=for_you|discover|following"""
    serializer_class = FeedEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        mode = request.query_params.get('mode', 'for_you')
        ids = build_feed(request.user, mode)
        events = (Event.objects.filter(id__in=ids)
                  .select_related('organizer').prefetch_related('media', 'tags'))
        by_id = {e.id: e for e in events}
        ordered = [by_id[i] for i in ids if i in by_id]
        return Response(self.get_serializer(ordered, many=True).data)


class AskThrottle(UserRateThrottle):
    rate = '10/min'   # tetto per utente: protegge la quota gratuita


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([AskThrottle])
def event_ask_view(request, event_id):
    """POST /api/events/<id>/ask/   body: {question, history?}  ->  {answer}"""
    event = get_object_or_404(
        Event.objects.select_related('organizer').prefetch_related('tags'),
        pk=event_id, status__iexact='active',
    )
    question = (request.data.get('question') or '').strip()
    if not question or len(question) > 500:
        return Response({'error': 'Question must be 1-500 characters.'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        answer = ask_about_event(event, question, request.data.get('history'))
    except AIBusyError:
        return Response({'error': 'The assistant is busy, try again in a minute.'},
                        status=status.HTTP_429_TOO_MANY_REQUESTS)
    except Exception:
        logger.exception('AI assistant failed')
        return Response({'error': 'The assistant is not available right now.'},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({'answer': answer})

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'tag_name']

class TagListView(generics.ListAPIView):

    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        default_tags = [
            'Disco',
            'Trap',
            'Hip Hop',
            'Rock',
            'Jazz',
        ]

        for name in default_tags:
            Tag.objects.get_or_create(tag_name=name)

        return Tag.objects.order_by('tag_name')
