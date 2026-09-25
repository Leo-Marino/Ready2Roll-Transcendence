from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, UserProfileUpdateSerializer

@api_view(['POST']) # Diciamo a Django di accettare SOLO i dati in entrata (POST)
def signup_view(request):
    # 1. request.data contiene esattamente il JSON che il tuo amico ha inviato!
    serializer = UserSerializer(data=request.data)

    # 2. Controlliamo se i dati sono validi (es. se l'username non è già stato preso)
    if serializer.is_valid():
        serializer.save() # 3. BOOM! L'utente viene salvato nel Database Postgres
        return Response({"messaggio": "Utente registrato con successo!"}, status=status.HTTP_201_CREATED)

    # 4. Se c'è un errore, rimandiamo i dettagli a Vue.js
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    user = request.user
    serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True) #okay to have partial data
    if serializer.is_valid():
        serializer.save()
        return Response({"messaggio": "Utente profile modificato con successo!"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
