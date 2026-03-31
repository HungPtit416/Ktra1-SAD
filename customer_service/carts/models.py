from django.conf import settings
from django.db import models


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart<{self.id}> for {self.user.username}"


class CartItem(models.Model):
    PRODUCT_TYPES = (
        ("laptop", "Laptop"),
        ("mobile", "Mobile"),
    )

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES)
    product_id = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "product_type", "product_id")

    def __str__(self):
        return f"{self.product_type}:{self.product_id} x {self.quantity}"
