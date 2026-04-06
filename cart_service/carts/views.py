from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
import requests


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        return Cart.objects.filter(customer_id=user_id)

    def perform_create(self, serializer):
        serializer.save(customer_id=self.request.user.id)


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        return CartItem.objects.filter(cart__customer_id=user_id)

    def create(self, request, *args, **kwargs):
        cart_id = request.data.get('cart')
        product_type = request.data.get('product_type')
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        cart = Cart.objects.filter(id=cart_id, customer_id=request.user.id).first()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check stock before adding to cart
        has_stock = self._check_product_stock(product_type, product_id, quantity)
        if not has_stock:
            return Response(
                {'error': 'Insufficient stock'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_type=product_type,
            product_id=product_id,
            defaults={'quantity': quantity, 'price': request.data.get('price', 0)}
        )

        if not created:
            # Check if total quantity would exceed stock
            new_quantity = item.quantity + quantity
            if not self._check_product_stock(product_type, product_id, new_quantity):
                return Response(
                    {'error': 'Insufficient stock for requested quantity'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            item.quantity = new_quantity
            item.save()

        serializer = self.get_serializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _check_product_stock(self, product_type, product_id, quantity):
        """Check if product has enough stock"""
        try:
            if product_type.lower() == 'laptop':
                url = f'http://laptop-service:8000/api/laptops/{product_id}/check_stock/'
            elif product_type.lower() == 'mobile':
                url = f'http://mobile-service:8000/api/mobiles/{product_id}/check_stock/'
            else:
                return False
            
            response = requests.get(url, params={'quantity': quantity}, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('has_stock', False)
            return False
        except Exception as e:
            print(f"Error checking stock: {str(e)}")
            return False
