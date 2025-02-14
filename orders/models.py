from django.db import models
from stock.models import Produit  

class Commande(models.Model):
    STATUT_CHOICES = [
        ('pending', 'Pending'),
        ('prepared', 'Prepared'),
        ('livraison_en_cours', 'Livraison en cours'),
        ('delivered', 'Delivered'),
    ]
    
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE) 
    quantite = models.IntegerField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='pending')
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.produit.nom} - {self.quantite} unités"
