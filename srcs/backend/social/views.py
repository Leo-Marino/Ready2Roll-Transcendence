from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from events.models import Event

from .models import Subscription, Comment, Like
from .serializers import CommentSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_follow_view(request, user_id):
    """
    POST /api/social/follow/<id>/
    Se l'utente loggato non segue <id> -> inizia a seguirlo.
    Se lo segue gia' -> smette di seguirlo.
    """
    target = get_object_or_404(User, pk=user_id, is_active=True)

    if target.pk == request.user.pk:
        return Response(
            {'detail': 'You cannot follow yourself.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    subscription, created = Subscription.objects.get_or_create(
        follower=request.user, followed=target
    )
    if not created:
        subscription.delete()

    return Response({
        'is_following': created,
        'followers_count': target.followers.count(),
        'following_count': target.following.count(),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like_view(request, event_id):
    """POST /api/social/events/<id>/like/  -> like / unlike toggle."""
    event = get_object_or_404(Event, pk=event_id)
    like, created = Like.objects.get_or_create(user=request.user, event=event)
    if not created:
        like.delete()
    return Response({'is_liked': created, 'likes_count': event.likes.count()})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def event_comments_view(request, event_id):
    # Verifica che l'evento esista
    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'GET':
        # Restituisce i commenti dal più recente al più vecchio
        comments = Comment.objects.filter(event=event).select_related('user').prefetch_related('replies__user').order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        content = (request.data.get('content') or '').strip()
        if not content:
            return Response({'error': 'Il contenuto del commento è obbligatorio.'}, status=status.HTTP_400_BAD_REQUEST)


    parent = None
    parent_id = request.data.get('parent_comment')
    if parent_id:
        # The parent must belong to the same event
        parent = get_object_or_404(Comment, pk=parent_id, event=event)
        # Replying to a reply? Attach it to the root comment (Instagram style)
        if parent.parent_comment_id is not None:
            parent = parent.parent_comment

    comment = Comment.objects.create(
        user=request.user,
        event=event,
        content=content,
        type_content='text',
        parent_comment=parent,
    )
    return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
