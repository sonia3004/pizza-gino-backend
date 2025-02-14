from rest_framework import serializers
from .models import KitchenTask

class KitchenTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = KitchenTask
        fields = '__all__'
