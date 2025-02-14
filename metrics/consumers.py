import json
from channels.generic.websocket import AsyncWebsocketConsumer


try:
    from metrics.utils import get_current_metrics
except ImportError:

    # Fonction de secours : renvoie des métriques par défaut
    async def get_current_metrics():
        return {"orders": 0, "revenue": 0, "stock": 0}

class MetricsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "metrics"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print(f"🖥️ Metrics WebSocket connecté ! Client : {self.channel_name}")

        # Envoyer immédiatement les métriques actuelles lors de la connexion
        try:
            current_metrics = await get_current_metrics() 
            print(f"📊 Métriques actuelles récupérées : {current_metrics}")
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des métriques actuelles : {e}")
            current_metrics = {"orders": 0, "revenue": 0, "stock": 0}
        try:
            await self.send(text_data=json.dumps(current_metrics))
            print("✅ Envoi initial réussi au WebSocket !")
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi initial via WebSocket : {e}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print(f"❌ Metrics WebSocket déconnecté (code: {close_code})")

    async def broadcast_metrics(self, event):
        metrics = event["metrics"]
        print(f"📡 Diffusion des métriques via WebSocket : {metrics}")

        try:
            await self.send(text_data=json.dumps(metrics))
            print("✅ Envoi réussi au WebSocket !")
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi WebSocket : {e}")
