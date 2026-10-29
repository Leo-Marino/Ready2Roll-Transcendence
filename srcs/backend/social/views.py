from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from events.models import Event
#from users.serializers import PublicUserProfileSerializer ##ilyas he did it u can take it off
from rest_framework.views import APIView
from .models import DirectMessage
from django.db.models import Q
from django.contrib.auth import get_user_model

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
    return Response(
        CommentSerializer(comment, context={'request':request}).data, status=status.HTTP_201_CREATED,
        )

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
            {'error': f'Reaction not valid. Choises: {list(valid_choices)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    reaction, created = Reaction.objects.get_or_create(
        user=request.user,
        comment=comment,
        defaults={'reaction_type': reaction_type}
    )

    if created:
        user_reaction=reaction_type
    elif reaction.reaction_type == reaction_type:
        reaction.delete()
        user_reaction = None
    else:
        reaction.reaction_type = reaction_type
        reaction.save(update_fields=['reaction_type'])
        user_reaction = reaction_type

    counts = comment.reactions.values('reaction_type').annotate(count=Count('id'))
    reactions_count = {item['reaction_type']: item['count'] for item in counts}

    return Response({
        'comment_id': comment.id,
        'user_reaction': user_reaction,
        'reactions_count': reactions_count,
    })

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_followers_view(request, user_id):
#     """ Returns the list of users following the given user_id """
#     target_user = get_object_or_404(User, pk=user_id)
#     followers_subs = target_user.followers.select_related('follower').all()
#     followers_users = [sub.follower for sub in followers_subs]

#     serializer = PublicUserProfileSerializer(followers_users, many=True, context={'request': request})
#     return Response(serializer.data)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_following_view(request, user_id):
#     """ Returns the list of users that the given user_id is following """
#     target_user = get_object_or_404(User, pk=user_id)
#     following_subs = target_user.following.select_related('followed').all()
#     followed_users = [sub.followed for sub in following_subs]

#     serializer = PublicUserProfileSerializer(followed_users, many=True, context={'request': request})
#     return Response(serializer.data)
class ChatHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        messages = DirectMessage.objects.filter(
            Q(sender=request.user, receiver_id=user_id) |
            Q(sender_id=user_id, receiver=request.user)
        ).select_related('sender').order_by('created_at')

        # Opening the conversation = the messages received from this user are now read
        DirectMessage.objects.filter(
            sender_id=user_id, receiver=request.user, is_read=False
        ).update(is_read=True)

        data = [{
            "id": m.id,
            "sender_id": m.sender_id,
            "sender": m.sender.username,
            "text": m.content,
            "isMe": m.sender_id == request.user.id,
            "created_at": m.created_at.isoformat()
        } for m in messages]
        return Response(data)

class ContactsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        me = request.user

        # Walk through all my DMs, newest first: the first message we meet
        # for a given contact is the last message of that conversation.
        last_msg = {}      # other_user_id -> DirectMessage
        unread = {}        # other_user_id -> number of unread messages received
        dms = (
            DirectMessage.objects
            .filter(Q(sender=me) | Q(receiver=me))
            .order_by('-created_at', '-id')
        )
        for m in dms:
            other_id = m.receiver_id if m.sender_id == me.id else m.sender_id
            if other_id not in last_msg:
                last_msg[other_id] = m
            if m.receiver_id == me.id and not m.is_read:
                unread[other_id] = unread.get(other_id, 0) + 1

        data = []
        for u in User.objects.exclude(id=me.id):
            m = last_msg.get(u.id)
            if m:
                prefix = "You: " if m.sender_id == me.id else ""
                last_text = prefix + m.content
                last_at = m.created_at.isoformat()
            else:
                last_text = "Click to chat..."
                last_at = None
            data.append({
                "id": u.id,
                "name": u.username,
                # Fallback to a placeholder if they don't have an avatar setup yet
                "img": "https://i.pravatar.cc/150?u=" + str(u.id),
                "lastMsg": last_text,
                "lastMsgAt": last_at,
                "unread": unread.get(u.id, 0),
            })

        return Response(data)
        # Latest conversation first; users we never talked to go at the bottom (A-Z)
        with_msgs = sorted((d for d in data if d["lastMsgAt"]), key=lambda d: d["lastMsgAt"], reverse=True)
        without = sorted((d for d in data if not d["lastMsgAt"]), key=lambda d: d["name"].lower())
        return Response(with_msgs + without)
