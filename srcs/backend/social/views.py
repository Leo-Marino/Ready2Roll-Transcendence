from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from events.models import Event

from .models import Subscription, Comment, EventLike, Reaction
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
    like, created = EventLike.objects.get_or_create(user=request.user, event=event)
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
        comments = (
            Comment.objects.filter(event=event, parent_comment__isnull=True)
            .select_related('user')
            .prefetch_related('reactions', 'replies__user', 'replies__reactions')
            .order_by('-created_at')
        )
        serializer = CommentSerializer(comments, many=True, context={'request':request})
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_comment_reaction_view(request, comment_id):
    """
    POST /api/social/comments/<comment_id>/react/
    Body: { "reaction_type": "like" | "laugh" | "wow" | "sad" | "angry" | "thumbs_up" | "thumbs_down" }
    """
    comment = get_object_or_404(Comment, pk=comment_id)
    reaction_type = request.data.get('reaction_type', 'like')

    valid_choices = dict(Reaction.REACTION_CHOICES).keys()
    if reaction_type not in valid_choices:
        return Response(
            {'error': f'Reaction non valida. Scelte: {list(valid_choices)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    existing = Reaction.objects.filter(user=request.user, comment=comment).first()

    if existing:
        if existing.reaction_type == reaction_type:
            # Stessa reaction cliccata -> rimuove
            existing.delete()
            user_reaction = None
        else:
            # Reaction diversa -> aggiorna
            existing.reaction_type = reaction_type
            existing.save()
            user_reaction = reaction_type
    else:
        Reaction.objects.create(
            user=request.user,
            comment=comment,
            reaction_type=reaction_type
        )
        user_reaction = reaction_type

    counts = comment.reactions.values('reaction_type').annotate(count=Count('id'))
    reactions_count = {item['reaction_type']: item['count'] for item in counts}

    return Response({
        'comment_id': comment.id,
        'user_reaction': user_reaction,
        'reactions_count': reactions_count,
    })
