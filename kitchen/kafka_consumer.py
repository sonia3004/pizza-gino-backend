import os
import django
import json
import time
from kafka import KafkaConsumer, KafkaProducer

# Charger Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_system.settings')
django.setup()

from kitchen.models import KitchenTask
from orders.models import Commande
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

#  Fonction pour diffuser les commandes WebSocket
def broadcast_commandes():
    """Diffuse la mise à jour des commandes via WebSockets"""
    channel_layer = get_channel_layer()
    commandes = list(Commande.objects.all().values("id", "produit_id", "produit__nom", "quantite", "statut")) 

    print(f"📡 Diffusion WebSocket : {commandes}")  

    async_to_sync(channel_layer.group_send)(
        "commandes",
        {"type": "broadcast_commandes", "commandes": commandes},
    )

# Kafka Consumer pour écouter les nouvelles commandes
consumer = KafkaConsumer(
    'commande_topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Kafka Producer pour envoyer les événements de statut
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("👨‍🍳 Service Kitchen : En attente des commandes...")

for message in consumer:
    try:
        
        print("📩 Message Kafka brut reçu :", message.value)

        data = message.value
        commande_id = data.get("id") or data.get("commande_id")

        if not commande_id:
            print("❌ Erreur : Message Kafka ne contient ni 'id' ni 'commande_id' !", data)
            continue

        statut_commande = data.get("statut", "")

        if statut_commande == "pending": 
            try:
                commande = Commande.objects.get(id=commande_id)

                # Vérifier si une tâche Kitchen existe déjà pour cette commande
                kitchen_task, created = KitchenTask.objects.get_or_create(commande=commande)

                if not created:
                    print(f"⚠️ Tâche Kitchen déjà existante pour la commande {commande_id}, on ne la recrée pas.")
                    continue

                print(f"🔥 La commande {commande_id} entre en préparation...")

                #  Étape 1 : Passer en préparation
                kitchen_task.statut = "en_preparation"
                kitchen_task.save()
                commande.statut = "en préparation"
                commande.save()

                # Diffuser WebSocket
                broadcast_commandes()

                print(f"⏳ Attente de 10 secondes...")
                time.sleep(10)

                # Étape 2 : Passer en prête
                kitchen_task.statut = "prete"
                kitchen_task.save()
                commande.statut = "prepared"
                commande.save()
                print(f"✅ Commande {commande_id} prête et mise à jour en base !")

                #  Diffuser WebSocket
                broadcast_commandes()

                # Publier l'événement sur Kafka pour la livraison
                event_message = {
                    "commande_id": commande_id,
                    "statut": "prepared"
                }
                producer.send("kitchen_topic", event_message)
                producer.flush()
                print(f"📢 Événement envoyé à Kafka : commande {commande_id} prête")

            except Commande.DoesNotExist:
                print(f"❌ Commande {commande_id} introuvable !")

    except json.JSONDecodeError:
        print("❌ Erreur de parsing JSON sur le message reçu.")
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
