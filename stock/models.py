from django.db import models

class Produit(models.Model):
    nom = models.CharField(max_length=255, unique=True)
    quantite_disponible = models.IntegerField(default=0)
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image_url = models.URLField(max_length=500, blank=True, null=True) 

    def __str__(self):
        return f"{self.nom} ({self.quantite_disponible} en stock) - {self.prix}€"
