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
from .serializers import CommentSerializer, DEFAULT_AVATAR
from events.serializers import FeedEventSerializer
from notifications.services import notify, unnotify, short
from .realtime import broadcast_social_action, push_message_signal, is_user_online

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
    if created:
        notify(target, request.user, 'subscription', 'started following you', unique=True)
    else:
        subscription.delete()
        unnotify(target, request.user, 'subscription')

    followers_count = target.followers.count()
    following_count = target.following.count()

    # Live update for everybody looking at the target's profile
    broadcast_social_action('follow', target.pk, {
        'actor_id': request.user.pk,
        'is_following': created,
        'followers_count': followers_count,
        'following_count': following_count,
    })

    return Response({
        'is_following': created,
        'followers_count': followers_count,
        'following_count': following_count,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like_view(request, event_id):
    """POST /api/social/events/<id>/like/  -> like / unlike toggle."""
    event = get_object_or_404(Event, pk=event_id)
    like, created = EventLike.objects.get_or_create(user=request.user, event=event)
    if created:
        notify(event.organizer, request.user, 'like',
               f'liked your event \u201c{event.title}\u201d', event=event, unique=True)
    else:
        like.delete()
        unnotify(event.organizer, request.user, 'like', event=event)

    likes_count = event.likes.count()
    broadcast_social_action('like', event.pk, {
        'actor_id': request.user.pk,
        'likes_count': likes_count,
    })
    return Response({'is_liked': created, 'likes_count': likes_count})


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
        if not content or len(content) > 500:
          return Response({'error': 'Comment must be between 1 and 500 characters.'}, status=status.HTTP_400_BAD_REQUEST)

        parent = None
        replied_to = None          # il commento a cui l'utente sta davvero rispondendo
        parent_id = request.data.get('parent_comment')
        if parent_id:
            # The parent must belong to the same event
            parent = get_object_or_404(Comment, pk=parent_id, event=event)
            replied_to = parent
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

        # Notifiche: risposta -> autore del commento; commento nuovo -> organizzatore dell'evento
        if replied_to is not None:
            notify(replied_to.user, request.user, 'reply',
                   f'replied to your comment: \u201c{short(content)}\u201d',
                   event=event, comment=comment)
        else:
            notify(event.organizer, request.user, 'comment',
                   f'commented on your event \u201c{event.title}\u201d: \u201c{short(content)}\u201d',
                   event=event, comment=comment)

        # Same number the feed shows: comments + replies
        broadcast_social_action('comment', event.pk, {
            'actor_id': request.user.pk,
            'comment_id': comment.pk,
            'parent_comment_id': parent.pk if parent else None,
            'comments_count': event.comments.count(),
        })

        return Response(
            CommentSerializer(comment, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
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

    emoji = dict(Reaction.REACTION_CHOICES)[reaction_type]
    reaction_text = f'reacted {emoji} to your comment: \u201c{short(comment.content, 40)}\u201d'

    if created:
        user_reaction = reaction_type
        notify(comment.user, request.user, 'reaction', reaction_text,
               event=comment.event, comment=comment, unique=True)
    elif reaction.reaction_type == reaction_type:
        reaction.delete()
        user_reaction = None
        unnotify(comment.user, request.user, 'reaction', event=comment.event, comment=comment)
    else:
        reaction.reaction_type = reaction_type
        reaction.save(update_fields=['reaction_type'])
        user_reaction = reaction_type
        notify(comment.user, request.user, 'reaction', reaction_text,
               event=comment.event, comment=comment, unique=True)

    counts = comment.reactions.values('reaction_type').annotate(count=Count('id'))
    reactions_count = {item['reaction_type']: item['count'] for item in counts}

    broadcast_social_action('comment_reaction', comment.pk, {
        'actor_id': request.user.pk,
        'event_id': comment.event_id,
        'reactions_count': reactions_count,
    })

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
        marked = DirectMessage.objects.filter(
            sender_id=user_id, receiver=request.user, is_read=False
        ).update(is_read=True)
        if marked:
            push_message_signal(request.user.id)   # other tabs: refresh the chat dot

        data = [{
            "id": m.id,
            "sender_id": m.sender_id,
            "sender": m.sender.username,
            "text": m.content,
            "isMe": m.sender_id == request.user.id,
            "created_at": m.created_at.isoformat()
        } for m in messages]
        return Response(data)

class UnreadMessagesCountView(APIView):
    """How many direct messages I received and have not read yet.
    Very light: used by the dot on the chat icon in the navbar."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = DirectMessage.objects.filter(receiver=request.user, is_read=False).count()
        return Response({"count": count})

class ContactsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        me = request.user

        # 1. Gather all active DMs and count unread messages
        last_msg = {}
        unread = {}
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
        # 3. Only return users in this combined list
        for u in User.objects.filter(id__in=last_msg).exclude(id=me.id):
            m = last_msg.get(u.id)
            if m:
                prefix = "You: " if m.sender_id == me.id else ""
                last_text = prefix + m.content
                last_at = m.created_at.isoformat()
            else:
                last_text = "Click to start chatting"
                last_at = None

            # Send the REAL avatar_url so Vue can construct the MinIO link
            data.append({
                "id": u.id,
                "username": u.username,
                "avatar_url": str(u.avatar_url) if u.avatar_url else DEFAULT_AVATAR,
                "lastMsg": last_text,
                "lastMsgAt": last_at,
                "unread": unread.get(u.id, 0),
                "is_online": is_user_online(u.id),
            })

        return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liked_events_view(request):
    likes = (
        EventLike.objects
        .filter(user=request.user, event__status__iexact='active')
        .select_related('event__organizer')
        .prefetch_related('event__media')
        .order_by('-created_at')
    )
    events = [like.event for like in likes]
    serializer = FeedEventSerializer(events, many=True, context={'request':request})
    return Response(serializer.data)
