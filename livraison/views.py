from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Livraison
from .serializers import LivraisonSerializer
from orders.models import Commande
from livraison.kafka_producer import envoyer_evenement

class LivraisonViewSet(viewsets.ModelViewSet):
    queryset = Livraison.objects.all()
    serializer_class = LivraisonSerializer

    @action(detail=True, methods=['post'])
    def demarrer_livraison(self, request, pk=None):
        """ Met à jour le statut et envoie un événement Kafka """
        livraison = self.get_object()
        livraison.statut = 'en_cours'
        livraison.save()

        # Publier l'événement Kafka
        message = {
            "id": livraison.id,
            "commande_id": livraison.commande.id,
            "statut": livraison.statut,
        }
        envoyer_evenement('livraison_topic', message)

        return Response({"message": "Livraison démarrée 🚚"})
