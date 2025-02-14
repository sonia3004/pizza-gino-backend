from django.db import models
from orders.models import Commande

class KitchenTask(models.Model):
    commande = models.OneToOneField(Commande, on_delete=models.CASCADE)
    statut = models.CharField(max_length=20, choices=[
        ('en_attente', 'En attente'),
        ('en_preparation', 'En préparation'),
        ('prepared', 'Prête')  
    ], default='en_attente')
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commande {self.commande.id} - {self.statut}"
