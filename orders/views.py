from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets
from django.http import JsonResponse
import json
import logging
from kafka import KafkaProducer
from orders.models import Commande
from orders.serializers import CommandeSerializer
from stock.models import Produit  

# Initialisation du logger
logger = logging.getLogger(__name__)

# Initialisation du producteur Kafka
try:
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    logger.info("✅ Kafka Producer initialisé")
except Exception as e:
    logger.error(f"❌ Erreur lors de l'initialisation de Kafka: {e}")
    producer = None

# Fonction pour diffuser les commandes WebSocket
def broadcast_commandes():
    """Diffuse les mises à jour des commandes via WebSockets"""
    channel_layer = get_channel_layer()
    commandes = list(Commande.objects.all().values("id", "produit_id", "quantite", "statut"))

    print(f"📡 Diffusion WebSocket : {commandes}")  

    async_to_sync(channel_layer.group_send)(
        "commandes",
        {"type": "broadcast_commandes", "commandes": commandes},
    )

class CommandeViewSet(viewsets.ModelViewSet):
    queryset = Commande.objects.all()
    serializer_class = CommandeSerializer

    def perform_create(self, serializer):
        """Créer une commande, décrémenter le stock et déclencher le workflow"""
        commande = serializer.save()
        logger.info(f"📦 Nouvelle commande créée : {commande.id}")

        # Gestion du stock
        try:
            produit = commande.produit  
            if produit.quantite_disponible >= commande.quantite:
                produit.quantite_disponible -= commande.quantite
                produit.save()
                logger.info(f"📉 Stock mis à jour : {produit.nom} - Nouveau stock : {produit.quantite_disponible}")
            else:
                logger.warning(f"⚠️ Stock insuffisant pour {produit.nom} ! Commande non prise en compte.")
                return  

        except Exception as e:
            logger.error(f"❌ Erreur lors de la mise à jour du stock : {e}")
            return 

        
        commande.statut = "pending"
        commande.save()
        logger.info(f"✅ Statut de la commande {commande.id} mis à 'pending'.")

        #  Envoi à Kafka avec le prix total
        try:
            event = {
                "commande_id": commande.id,
                "statut": commande.statut,
                "prix": float(produit.prix) * commande.quantite 
            }
            producer.send("commande_topic", value=event)
            producer.flush()
            logger.info(f"✅ Message envoyé à Kafka: {event}")
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'envoi Kafka : {e}")

        #  Diffuser WebSocket
        broadcast_commandes()


@csrf_exempt  
@api_view(["POST"])
def publier_evenement(request, commande_id):
    """Mise à jour d'une commande et envoi à Kafka"""
    try:
        commande = Commande.objects.get(id=commande_id)
        commande.statut = "pending"
        commande.save()
        logger.info(f"🔥 Commande {commande.id} mise à jour en 'pending', envoi Kafka...")

        #  Envoi à Kafka
        if producer:
            event = {"commande_id": commande.id, "statut": commande.statut}
            producer.send("commande_topic", value=event)
            producer.flush()
            logger.info(f"✅ Message envoyé à Kafka: {event}")
        else:
            logger.warning("⚠️ Kafka Producer non initialisé, message non envoyé")

        #  Diffuser WebSocket
        broadcast_commandes()

        return JsonResponse({"message": "Commande mise à jour et envoyée à Kafka"}, status=200)
    
    except Commande.DoesNotExist:
        logger.error(f"❌ Commande {commande_id} introuvable")
        return JsonResponse({"error": "Commande introuvable"}, status=404)

@csrf_exempt  
@api_view(["POST"])
def create_commande(request):
    """Créer une commande via API"""
    serializer = CommandeSerializer(data=request.data)
    if serializer.is_valid():
        commande = serializer.save()
        logger.info(f"📦 Commande ajoutée via API : {commande.id}")

        #  Diffuser WebSocket après création
        broadcast_commandes()

        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)
