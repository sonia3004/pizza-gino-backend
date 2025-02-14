import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_system.settings')
django.setup()

from stock.models import Produit  
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'commande_topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("🛒 Service Stock : En attente des commandes...")

for message in consumer:
    data = message.value
    produit_nom = data['produit']
    quantite = data['quantite']

    try:
        produit = Produit.objects.get(nom=produit_nom)
        if produit.quantite_disponible >= quantite:
            produit.quantite_disponible -= quantite
            produit.save()
            print(f"✅ Stock mis à jour pour {produit_nom} : {produit.quantite_disponible} restants")
        else:
            print(f"❌ Stock insuffisant pour {produit_nom} !")
    except Produit.DoesNotExist:
        print(f"❌ Produit {produit_nom} introuvable dans le stock !")
