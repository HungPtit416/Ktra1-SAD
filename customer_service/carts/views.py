from rest_framework import mixins, permissions, serializers, viewsets

from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartSerializer


class CartViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        cart_id = serializer.validated_data.pop("cart", None)
        cart = Cart.objects.filter(id=cart_id, user=self.request.user).first()
        if not cart:
            raise serializers.ValidationError("Invalid cart for this user")
        serializer.save(cart=cart)
