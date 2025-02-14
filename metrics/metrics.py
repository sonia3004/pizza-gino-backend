#!/usr/bin/env python
import os
import django
import json
from django.db.models import Sum, F
from kafka import KafkaConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Configuration de Django avant d'utiliser get_channel_layer()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_system.settings')
django.setup()

from metrics_app.models import Metrics
from stock.models import Produit
from orders.models import Commande

def get_stock_disponible():
    """Récupérer la quantité totale de stock disponible."""
    try:
        stock_total = Produit.objects.aggregate(stock_total=Sum('quantite_disponible'))['stock_total'] or 0
        print(f"📦 Stock disponible recalculé : {stock_total}")
        return stock_total
    except Exception as e:
        print(f"❌ Erreur lors de la récupération du stock : {e}")
        return 0

def recalculate_orders():
    """Recalcule le nombre total de commandes existantes."""
    try:
        total_orders = Commande.objects.count()
        print(f"🛒 Nombre de commandes recalculé : {total_orders}")
        return total_orders
    except Exception as e:
        print(f"❌ Erreur lors du recalcul du nombre de commandes : {e}")
        return 0

def recalculate_revenue():
    """Recalcule le chiffre d'affaires en fonction des commandes existantes."""
    try:
        total_revenue = Commande.objects.aggregate(
            total_revenue=Sum(F('quantite') * F('produit__prix'))
        )['total_revenue'] or 0.0

        print(f"💰 Chiffre d'affaires recalculé : {total_revenue}€")
        return total_revenue
    except Exception as e:
        print(f"❌ Erreur lors du recalcul du chiffre d'affaires : {e}")
        return 0.0

def update_persistent_metrics():
    """Recalcule toutes les métriques et met à jour l'enregistrement en base."""
    try:
        total_orders = recalculate_orders()
        total_revenue = recalculate_revenue()

        metrics_obj, created = Metrics.objects.get_or_create(id=1)
        metrics_obj.orders = total_orders
        metrics_obj.revenue = total_revenue
        metrics_obj.save()

        print(f"✅ Metrics mises à jour EN BASE : {metrics_obj.orders} commandes, {metrics_obj.revenue}€ de chiffre d'affaires")
        return metrics_obj
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour des métriques : {e}")
        return None

def broadcast_metrics():
    """Envoie les métriques recalculées via WebSocket."""
    try:
        metrics_obj = update_persistent_metrics()
        stock_disponible = get_stock_disponible()

        if not metrics_obj:
            print("❌ Impossible de récupérer les métriques pour diffusion WebSocket")
            return

        metrics = {
            "orders": metrics_obj.orders,
            "revenue": float(metrics_obj.revenue),
            "stock": stock_disponible,
        }

        print(f"📡 Diffusion des métriques via WebSocket (VALEURS ACTUALISÉES) : {metrics}")
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "metrics",
            {
                "type": "broadcast_metrics",
                "metrics": metrics,
            }
        )
        print("✅ Envoi réussi via WebSocket !")

    except Exception as e:
        print(f"❌ Erreur lors de l'envoi WebSocket : {e}")

def run_metrics_consumer():
    """Consumer Kafka pour écouter les mises à jour des commandes."""
    consumer = KafkaConsumer(
        'commande_topic',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='latest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    print("📊 Metrics Consumer : En attente des mises à jour des commandes...")

    for message in consumer:
        data = message.value
        print(f"📡 Message reçu de Kafka : {data}")

        if "commande_id" in data:
            print(f"🛒 Commande ID: {data['commande_id']} reçue.")

            # Met à jour immédiatement les métriques et les envoie via WebSocket
            broadcast_metrics()
        else:
            print(f"⚠️ Événement Kafka inattendu, ignoré : {data}")

if __name__ == '__main__':
    run_metrics_consumer()
