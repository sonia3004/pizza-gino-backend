from django.db import models

class Metrics(models.Model):
    orders = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock = models.PositiveIntegerField(default=0)  
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Metrics (Orders: {self.orders}, Revenue: {self.revenue} €, Stock: {self.stock})"
