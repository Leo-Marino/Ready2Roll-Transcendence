from django.contrib.auth import get_user_model
from django.db.models import Case, IntegerField, Q, Value, When
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Event
from .serializers import DEFAULT_AVATAR, FeedEventSerializer

MAX_USERS = 20
MAX_EVENTS = 30


def _avatar(user):
    if user.avatar_url:
        raw = str(user.avatar_url)
        return raw if raw.startswith('http') else user.avatar_url.url
    return DEFAULT_AVATAR


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_view(request):
    q = (request.query_params.get('q') or '').strip().lstrip('#@').strip()[:50]
    if not q:
        return Response({'query': '', 'users': [], 'events': []})

    User = get_user_model()
    rank = Case(
        When(username__iexact=q, then=Value(0)),
        When(username__istartswith=q, then=Value(1)),
        default=Value(2),
        output_field=IntegerField(),
    )
    users = (
        User.objects
        .filter(is_active=True)
        .filter(Q(username__icontains=q) | Q(legal_name__icontains=q))
        .exclude(pk=request.user.pk)
        .exclude(username__iexact='admin')
        .annotate(rank=rank)
        .order_by('rank', 'username')[:MAX_USERS]
    )
    users_data = [{
        'id': u.id,
        'username': u.username,
        'display_name': u.legal_name or u.username,
        'avatar': _avatar(u),
        'is_business': u.type_of_user == 'business',
        'is_verified': u.is_verified,
        'bio': (u.bio or '')[:100],
    } for u in users]

    events = (
        Event.objects
        .filter(status__iexact='active', media__isnull=False)
        .filter(Q(title__icontains=q) | Q(tags__tag_name__icontains=q))
        .select_related('organizer')
        .prefetch_related('media')
        .distinct()
        .order_by('-created_at')[:MAX_EVENTS]
    )
    events_data = FeedEventSerializer(events, many=True, context={'request': request}).data

    return Response({'query': q, 'users': users_data, 'events': events_data})
