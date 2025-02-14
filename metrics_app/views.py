from collections import defaultdict
from decimal import Decimal
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, F
from orders.models import Commande
from stock.models import Produit  
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

def get_total_stock():
    """Récupère directement le stock total depuis la base de données."""
    try:
        total_stock = Produit.objects.aggregate(stock_total=Sum('quantite_disponible'))['stock_total'] or 0
        return total_stock
    except Exception as e:
        print(f"❌ Erreur lors de la récupération du stock : {e}")
        return 0

def get_metrics_data():
    """Retourne les métriques mises à jour."""
    total_orders = Commande.objects.count()
    total_revenue = Commande.objects.aggregate(
        revenue=Sum(F('quantite') * F('produit__prix'))
    )['revenue'] or 0.0
    stock_disponible = get_total_stock()

    return {
        "orders": total_orders,
        "revenue": float(total_revenue),
        "stock": stock_disponible,
    }

def send_metrics_to_websocket(metrics):
    """Envoie les métriques mises à jour via WebSocket."""
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "dashboard_metrics",
            {
                "type": "update.metrics",
                "data": json.dumps(metrics),
            },
        )
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi des métriques via WebSocket : {e}")

@api_view(['GET'])
def get_metrics(request):
    """
    Vue retournant les métriques courantes (celles affichées en temps réel sur le dashboard).
    """
    try:
        data = get_metrics_data()
    except Exception as e:
        print(f"❌ Erreur lors du calcul des métriques : {e}")
        data = {"orders": 0, "revenue": 0, "stock": get_total_stock()}
    
    return Response(data)

@api_view(["DELETE"])
def supprimer_commande(request, id):
    try:
        commande = Commande.objects.get(id=id)
        commande.delete()

        # ⚡️ Recalcul des métriques et envoi via WebSocket
        nouvelles_metriques = get_metrics_data()
        send_metrics_to_websocket(nouvelles_metriques)

        return Response({"message": "Commande supprimée"}, status=200)
    except Commande.DoesNotExist:
        return Response({"message": "Commande non trouvée"}, status=404)

@api_view(['GET'])
def historical_metrics(request):
    """
    Vue retournant les métriques historiques agrégées par jour.
    """
    try:
        # Récupérer les produits pour construire un dictionnaire nom -> prix
        product_prices = {produit.nom: Decimal(produit.prix) for produit in Produit.objects.all()}
        
        # Récupérer toutes les commandes
        commandes = Commande.objects.all()
        
        # Agréger les métriques par date
        metrics_by_date = defaultdict(lambda: {'orders': 0, 'revenue': Decimal("0.00")})

        for commande in commandes:
            commande_date = commande.date_creation.date()
            metrics_by_date[commande_date]['orders'] += 1
            
            product_price = product_prices.get(commande.produit.nom, Decimal("0.00"))
            revenue = commande.quantite * product_price
            metrics_by_date[commande_date]['revenue'] += revenue

        # Trier les dates pour un affichage chronologique
        sorted_dates = sorted(metrics_by_date.keys())
        
        # Récupérer le stock actuel
        current_stock = get_total_stock()
        
        # Préparer les données pour la réponse
        data = []
        for dt in sorted_dates:
            data.append({
                "date": dt.isoformat(),
                "orders": metrics_by_date[dt]['orders'],
                "revenue": float(metrics_by_date[dt]['revenue']),
                "stock": current_stock,
            })

        return Response(data)

    except Exception as e:
        print(f"❌ Erreur lors du calcul des métriques historiques : {e}")
        return Response({"error": "Erreur lors de la récupération des données"}, status=500)
