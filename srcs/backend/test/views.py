from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def hello_vue(request):
    # Questo è un dizionario Python standard
    dati = {
        "messaggio": "Ciao dal Backend in Django! Il database è collegato e i CORS sono aperti 🚀",
        "status": "successo"
    }
    # Response() del REST Framework converte automaticamente il dizionario in puro JSON
    return Response(dati)
