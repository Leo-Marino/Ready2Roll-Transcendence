from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from events.serializers import DEFAULT_AVATAR
from .models import Notification

MAX_NOTIFICATIONS = 50


def _avatar(user):
    if user.avatar_url:
        raw = str(user.avatar_url)
        return raw if raw.startswith('http') else user.avatar_url.url
    return DEFAULT_AVATAR


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list_view(request):
    """GET /api/notifications/  -> le ultime 50 notifiche dell'utente loggato."""
    qs = (
        Notification.objects
        .filter(recipient=request.user)
        .select_related('sender', 'event')
        .order_by('-created_at', '-id')[:MAX_NOTIFICATIONS]
    )
    results = [{
        'id': n.id,
        'type': n.notification_type,
        'text': n.notification_txt,
        'is_read': n.is_read,
        'created_at': n.created_at.isoformat(),
        'sender': {
            'id': n.sender.id,
            'username': n.sender.username,
            'avatar': _avatar(n.sender),
        } if n.sender else None,
        'event_id': n.event_id,
        'event_title': n.event.title if n.event else None,
    } for n in qs]
    unread = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return Response({'unread_count': unread, 'results': results})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_count_view(request):
    """GET /api/notifications/unread-count/  -> leggero, il frontend lo chiede ogni 20 secondi."""
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return Response({'count': count})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read_view(request):
    """POST /api/notifications/read/  -> segna tutte come lette."""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return Response({'count': 0})
