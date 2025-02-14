from django.db import models
from orders.models import Commande  

class Livraison(models.Model):
    STATUT_CHOICES = [
        ('livraison_en_cours', 'Livraison en cours'),
        ('delivered', 'Delivered'),
    ]

    commande = models.OneToOneField(Commande, on_delete=models.CASCADE)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_cours')
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Livraison {self.id} - {self.statut}"
