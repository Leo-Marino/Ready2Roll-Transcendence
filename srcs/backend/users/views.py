from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
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

@api_view(['POST']) # Diciamo a Django di accettare SOLO i dati in entrata (POST)
def signup_view(request):
    # 1. request.data contiene esattamente il JSON che il tuo amico ha inviato!
    serializer = UserSerializer(data=request.data)

    # 2. Controlliamo se i dati sono validi (es. se l'username non è già stato preso)
    if serializer.is_valid():
        user = serializer.save() # 3. BOOM! L'utente viene salvato nel Database Postgres
        refresh = RefreshToken.for_user(user)
        return Response({
            "messaggio": "Utente registrato con successo!",
            "token":str(refresh.access_token),
            "refresh":str(refresh),
            }, status=status.HTTP_201_CREATED)
    # 4. Se c'è un errore, rimandiamo i dettagli a Vue.js
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Restituisce i dati del profilo dell'utente loggato.
    """
    # L'utente viene estratto automaticamente dal token JWT inviato da Vue
    user = request.user

    # Serializziamo l'utente (convertiamo l'oggetto del database in un dizionario)
    serializer = UserProfileSerializer(user)
    # Restituiamo i dati formattati in JSON
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    user = request.user
    serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True) #okay to have partial data
    if serializer.is_valid():
        serializer.save()
        return Response({"messaggio": "Utente profile modificato con successo!"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail_view(request, user_id):
    """
    Profilo pubblico di un altro utente (GET /api/users/<id>/).
    Usato da OtherUserProfileView.vue. Non espone email/telefono.
    """
    user = get_object_or_404(User, pk=user_id, is_active=True)
    serializer = PublicUserProfileSerializer(user, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_events_view(request, user_id):
    """
    GET /api/users/<id>/events/
    Events (with their video/image) created by that user.
    Other people only see ACTIVE events; the owner also sees drafts/scheduled.
    """
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
        serializer = FollowUserSerializer(follower_list, many = True, context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserFollowingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        target_user = get_object_or_404(User, pk=user_id)
        subscriptions = target_user.following.select_related('followed').all()
        following_list = [sub.followed for sub in subscriptions]
        serializer = FollowUserSerializer(following_list, many = True, context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)



