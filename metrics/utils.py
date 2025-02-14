from metrics_app.models import Metrics
from stock.models import Produit
from asgiref.sync import sync_to_async

async def get_stock_disponible():
    """Récupérer la quantité totale de stock disponible depuis les produits en mode asynchrone."""
    produits = await sync_to_async(list)(Produit.objects.all())
    return sum(produit.quantite_disponible for produit in produits)

async def get_current_metrics():
    """Récupérer les métriques actuelles en base de données en mode asynchrone."""
    try:
        metrics_obj = await sync_to_async(Metrics.objects.get)(id=1)
        stock = await get_stock_disponible()
        return {
            "orders": metrics_obj.orders,
            "revenue": float(metrics_obj.revenue),
            "stock": stock,
        }
    except Metrics.DoesNotExist:
        print("❌ Aucune métrique trouvée en base, initialisation à zéro.")
        stock = await get_stock_disponible()
        return {"orders": 0, "revenue": 0, "stock": stock}
