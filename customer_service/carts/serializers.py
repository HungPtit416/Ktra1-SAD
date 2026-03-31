from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    cart = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = CartItem
        fields = ["id", "cart", "product_type", "product_id", "quantity", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        if self.instance is None and "cart" not in attrs:
            raise serializers.ValidationError({"cart": "This field is required."})
        return attrs


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "created_at", "updated_at", "items"]
        read_only_fields = ["id", "created_at", "updated_at", "items"]
