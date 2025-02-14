from django.urls import re_path
from metrics.consumers import MetricsConsumer  
websocket_urlpatterns = [
    re_path(r'^ws/metrics/$', MetricsConsumer.as_asgi()),
]
