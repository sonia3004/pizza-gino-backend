import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "order_system.settings")
django.setup()  

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from orders.routing import websocket_urlpatterns as orders_ws_urlpatterns
from metrics.routing import websocket_urlpatterns as metrics_ws_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(orders_ws_urlpatterns + metrics_ws_urlpatterns),
})
