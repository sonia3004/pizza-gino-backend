from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import KitchenTask
from .serializers import KitchenTaskSerializer
from orders.models import Commande
from kitchen.kafka_producer import envoyer_evenement
import time

class KitchenViewSet(viewsets.ModelViewSet):
    queryset = KitchenTask.objects.all()
    serializer_class = KitchenTaskSerializer

    @action(detail=True, methods=['post'])
    def demarrer_preparation(self, request, pk=None):
        """ Passe une commande en statut 'en_preparation' et simule la cuisson """
        kitchen_task = self.get_object()
        kitchen_task.statut = 'en_preparation'
        kitchen_task.save()

        # Simuler la préparation avec un délai
        time.sleep(5)  # Simule 5 secondes de cuisson
        kitchen_task.statut = 'prete'
        kitchen_task.save()

        # Publier un événement Kafka pour signaler que la commande est prête
        message = {
            "id": kitchen_task.id,
            "commande_id": kitchen_task.commande.id,
            "statut": kitchen_task.statut,
        }
        envoyer_evenement('kitchen_topic', message)

        return Response({"message": "Commande préparée 🍕"})

