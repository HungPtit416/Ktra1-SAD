from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Laptop
from .permissions import IsInternalOrReadOnly
from .serializers import LaptopSerializer


class LaptopViewSet(viewsets.ModelViewSet):
    serializer_class = LaptopSerializer
    permission_classes = [IsInternalOrReadOnly]

    def get_queryset(self):
        queryset = Laptop.objects.all().order_by("-created_at")
        query = self.request.query_params.get("search")
        if query:
            queryset = queryset.filter(name__icontains=query)
        brand = self.request.query_params.get("brand")
        if brand:
            queryset = queryset.filter(brand__icontains=brand)
        return queryset

    @action(detail=True, methods=['get'])
    def check_stock(self, request, pk=None):
        """Check if product has enough stock"""
        laptop = self.get_object()
        quantity = int(request.query_params.get('quantity', 1))
        has_stock = laptop.stock >= quantity
        return Response({
            'product_id': laptop.id,
            'stock': laptop.stock,
            'required': quantity,
            'has_stock': has_stock
        })

    @action(detail=True, methods=['post'])
    def reduce_stock(self, request, pk=None):
        """Reduce stock by quantity"""
        laptop = self.get_object()
        quantity = int(request.data.get('quantity', 1))
        
        if laptop.stock < quantity:
            return Response(
                {'error': f'Insufficient stock. Available: {laptop.stock}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        laptop.stock -= quantity
        laptop.save()
        return Response({
            'product_id': laptop.id,
            'stock_reduced': quantity,
            'remaining_stock': laptop.stock
        })
