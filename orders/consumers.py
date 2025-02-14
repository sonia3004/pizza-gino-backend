import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async
from orders.models import Commande

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Connexion WebSocket et ajout au groupe de diffusion."""
        await self.accept()
        self.room_group_name = "commandes"

        # Ajouter le client WebSocket au groupe
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        print("🖥️ Connexion WebSocket établie !")

        # Envoyer immédiatement les commandes existantes au client connecté
        await self.send_commandes()

    async def disconnect(self, close_code):
        """Déconnexion du WebSocket et suppression du groupe."""
        print(f"❌ Déconnexion WebSocket (code: {close_code})")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Écoute des messages entrants (optionnel si on ne reçoit rien du front)."""
        print("📩 Message WebSocket reçu :", text_data)

    async def send_commandes(self):
        """Récupère et envoie toutes les commandes en temps réel au client connecté."""
        commandes = await sync_to_async(list)(
            Commande.objects.all().values("id", "produit", "quantite", "statut")
        )
        print("📡 Envoi initial des commandes en temps réel :", commandes)

        # Envoyer les commandes immédiatement après la connexion
        await self.send(text_data=json.dumps(commandes))

    async def broadcast_commandes(self, event):
        """Envoie les commandes mises à jour à tous les clients WebSocket."""
        print("📡 Diffusion WebSocket des nouvelles commandes :", event["commandes"])
        await self.send(text_data=json.dumps(event["commandes"]))
