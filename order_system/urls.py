from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from orders.views import CommandeViewSet, publier_evenement
from stock.views import ProduitViewSet
from livraison.views import LivraisonViewSet
from kitchen.views import KitchenViewSet
from django.conf import settings
from django.conf.urls.static import static
from metrics_app.views import get_metrics, historical_metrics  

# Import des WebSockets
import orders.routing

# Configuration du router API
router = DefaultRouter()
router.register(r'commandes', CommandeViewSet)
router.register(r'produits', ProduitViewSet)
router.register(r'livraisons', LivraisonViewSet)
router.register(r'kitchen', KitchenViewSet)

# URLs principales
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    # Ajout de la route pour l'endpoint publier_evenement
    path('api/publier_evenement/<int:commande_id>/', publier_evenement, name="publier_evenement"),
    path('ws/', include(orders.routing.websocket_urlpatterns)),  # WebSockets pour le Dashboard
    path('api/metrics/', get_metrics, name='get_metrics'),
    path('api/metrics/historical/', historical_metrics, name='historical_metrics'),
]

# Ajout des fichiers statiques en mode DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
