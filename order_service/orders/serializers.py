from rest_framework import serializers
from .models import Order, OrderItem
import requests
import os

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product_type', 'product_id', 'quantity', 'price']
        read_only_fields = ['id', 'order']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = ['id', 'customer_id', 'status', 'total_amount', 'items', 'created_at', 'updated_at']
        read_only_fields = ['customer_id', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            # Reduce stock from product service
            self._reduce_product_stock(item_data)
        
        return order
    
    def _reduce_product_stock(self, item_data):
        """Reduce stock from laptop or mobile service"""
        product_type = item_data.get('product_type')
        product_id = item_data.get('product_id')
        quantity = item_data.get('quantity', 1)
        
        try:
            if product_type.lower() == 'laptop':
                url = f'http://laptop-service:8000/api/laptops/{product_id}/reduce_stock/'
            elif product_type.lower() == 'mobile':
                url = f'http://mobile-service:8000/api/mobiles/{product_id}/reduce_stock/'
            else:
                return
            
            headers = {'X-Internal-API-Key': 'internal-shared-key'}
            response = requests.post(url, json={'quantity': quantity}, headers=headers, timeout=5)
            if response.status_code != 200:
                print(f"Failed to reduce stock: {response.text}")
        except Exception as e:
            print(f"Error reducing stock: {str(e)}")

