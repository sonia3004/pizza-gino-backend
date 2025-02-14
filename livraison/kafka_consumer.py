import os
import django
import time  # Pour les délais
import json
from kafka import KafkaConsumer, KafkaProducer

# Charger Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_system.settings')
django.setup()

from livraison.models import Livraison
from orders.models import Commande
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Fonction pour diffuser les commandes WebSocket
def broadcast_commandes():
    """Diffuse la mise à jour des commandes via WebSockets"""
    channel_layer = get_channel_layer()
    commandes = list(Commande.objects.all().values("id", "produit_id", "produit__nom", "quantite", "statut"))  

    print(f"📡 Diffusion WebSocket : {commandes}")  

    async_to_sync(channel_layer.group_send)(
        "commandes",
        {"type": "broadcast_commandes", "commandes": commandes},
    )

# Kafka Consumer pour écouter Kitchen
consumer = KafkaConsumer(
    'kitchen_topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Kafka Producer pour envoyer l'événement "livraison en cours / delivered"
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("🚚 Service Livraison : En attente des commandes prêtes...")

for message in consumer:
    try:
        data = message.value
        commande_id = data['commande_id']
        statut_commande = data['statut']

        if statut_commande == 'prepared':  # Si Kitchen a terminé la commande
            try:
                commande = Commande.objects.get(id=commande_id)

                # Étape 1 : Attente pour garder "prepared" visible
                print(f"⏳ Attente de 10 secondes pour laisser le statut 'prepared' visible pour la commande {commande_id}...")
                time.sleep(10)

                # Étape 2 : Passer en "livraison_en_cours"
                commande.statut = "livraison_en_cours"
                commande.save()

                # Essayer de récupérer la livraison existante
                try:
                    livraison = Livraison.objects.get(commande=commande)
                    livraison.statut = "livraison_en_cours"
                    livraison.save()
                    print(f"📦 Livraison mise à jour pour la commande {commande_id} avec le statut 'livraison_en_cours'.")
                except Livraison.DoesNotExist:
                    # Sinon, créer la livraison avec le statut souhaité
                    livraison = Livraison.objects.create(
                        commande=commande,
                        statut="livraison_en_cours"
                    )
                    print(f"📦 Livraison démarrée pour la commande {commande_id} avec le statut 'livraison_en_cours'.")

                #  Diffuser WebSocket après mise à jour
                broadcast_commandes()

                #  Attente de 10 secondes avant de passer à "delivered"
                print("⏳ Attente de 10 secondes avant de passer au statut 'delivered'...")
                time.sleep(10)

                # Étape 3 : Passer en "delivered"
                commande.statut = 'delivered'
                commande.save()

                livraison.statut = 'delivered'
                livraison.save()

                # Diffuser WebSocket après mise à jour
                broadcast_commandes()

                # Publier l'événement sur Kafka pour notifier que la livraison est terminée
                event_message = {
                    "commande_id": commande_id,
                    "statut": "delivered"
                }
                producer.send('livraison_topic', event_message)
                producer.flush()

                print(f"📢 Événement envoyé à Kafka : commande {commande_id} est 'delivered'.")

            except Commande.DoesNotExist:
                print(f"❌ Commande {commande_id} introuvable pour la livraison !")

    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
