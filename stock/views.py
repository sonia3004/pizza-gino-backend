from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Produit
from .serializers import ProduitSerializer

class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer

    @action(detail=True, methods=['post'])
    def reduire_stock(self, request, pk=None):
        """ Réduire le stock après une commande """
        produit = self.get_object()
        quantite = request.data.get("quantite", 1)

        if produit.quantite_disponible >= int(quantite):
            produit.quantite_disponible -= int(quantite)
            produit.save()
            return Response({"message": f"Stock mis à jour : {produit.quantite_disponible} restants"})
        else:
            return Response({"error": "Stock insuffisant"}, status=400)

