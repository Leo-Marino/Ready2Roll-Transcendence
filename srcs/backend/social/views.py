from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription

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
