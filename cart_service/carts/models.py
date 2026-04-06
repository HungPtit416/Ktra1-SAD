from django.db import models


class Cart(models.Model):
    customer_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'

    def __str__(self):
        return f"Cart #{self.id} (Customer {self.customer_id})"


class CartItem(models.Model):
    PRODUCT_TYPE_CHOICES = (
        ('laptop', 'Laptop'),
        ('mobile', 'Mobile'),
    )

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES)
    product_id = models.IntegerField()
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cart_items'
        unique_together = ('cart', 'product_type', 'product_id')

    def __str__(self):
        return f"{self.product_type.capitalize()} #{self.product_id} x{self.quantity}"
