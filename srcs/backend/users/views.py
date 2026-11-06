from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q # ALEK
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    UserSerializer,
    UserProfileUpdateSerializer,
    UserProfileSerializer,
    PublicUserProfileSerializer,
    FollowUserSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from events.models import Event
from events.serializers import EventSerializer

User = get_user_model()

@api_view(['POST']) # WIP ALEK
def signup_view(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save() # WIP ALEK
        refresh = RefreshToken.for_user(user)
        return Response({
            "messaggio": "Utente registrato con successo!",
            "token": str(refresh.access_token), # WIP ALEK
            "refresh": str(refresh), # WIP ALEK
            }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    serializer = UserProfileSerializer(user)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    user = request.user
    serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True) # WIP ALEK
    if serializer.is_valid():
        serializer.save()
        return Response({"messaggio": "Utente profile modificato con successo!"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail_view(request, user_id):
    user = get_object_or_404(User, pk=user_id, is_active=True)
    serializer = PublicUserProfileSerializer(user, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_events_view(request, user_id):
    user = get_object_or_404(User, pk=user_id, is_active=True)
    events = Event.objects.filter(organizer=user).order_by('-created_at')
    if request.user.pk != user.pk:
        events = events.filter(status__iexact='active')
    serializer = EventSerializer(events, many=True, context={'request': request})
    return Response(serializer.data)

class UserFollowersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        target_user = get_object_or_404(User, pk=user_id)
        subscriptions = target_user.followers.select_related('follower').all()
        follower_list = [sub.follower for sub in subscriptions]
        serializer = FollowUserSerializer(follower_list, many=True, context={'request': request}) # WIP ALEK
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserFollowingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        target_user = get_object_or_404(User, pk=user_id)
        subscriptions = target_user.following.select_related('followed').all()
        following_list = [sub.followed for sub in subscriptions]
        serializer = FollowUserSerializer(following_list, many=True, context={'request': request}) # WIP ALEK
        return Response(serializer.data, status=status.HTTP_200_OK)


 # WIP ALEK

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_contacts_view(request, user_id=None):
    """
    Restituisce i contatti con cui l'utente ha chat attive.
    Se non ci sono chat attive, restituisce una lista vuota.
    """
    user = request.user
    return Response([], status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_search_view(request):
    """
    Cerca tra tutti gli utenti registrati nel database per avviare una nuova chat.
    Endpoint: GET /api/social/users/search/?q=...
    """
    query = request.GET.get('q', '').strip()
    user = request.user
    if not query:
        return Response([], status=status.HTTP_200_OK)
    users = User.objects.filter(
        Q(username__icontains=query) | Q(email__icontains=query),
        is_active=True
    ).exclude(id=user.id).exclude(username__iexact='admin').exclude(email__iexact='admin')[:15]
    
    serializer = FollowUserSerializer(users, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)

# WIP ALEK