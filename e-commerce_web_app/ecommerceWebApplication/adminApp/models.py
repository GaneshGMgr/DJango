from django.db import models
from authApp.models import User

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    department = models.CharField(max_length=100)
    permissions = models.JSONField(default=dict)

class Inventory(models.Model):
    product = models.OneToOneField('ecommerceApp.Product', on_delete=models.CASCADE, related_name='inventory')
    quantity = models.PositiveIntegerField()
    low_stock_threshold = models.PositiveIntegerField(default=5)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gte=0),
                name="non_negative_quantity"
            )
        ]

class InventoryHistory(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20)
    quantity_change = models.IntegerField()
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class OrderNote(models.Model):
    order = models.ForeignKey('ecommerceApp.Order', on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    note = models.TextField()
    is_private = models.BooleanField(default=True)