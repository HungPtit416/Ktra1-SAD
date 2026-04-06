from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Mobile
from .permissions import IsInternalOrReadOnly
from .serializers import MobileSerializer


class MobileViewSet(viewsets.ModelViewSet):
    serializer_class = MobileSerializer
    permission_classes = [IsInternalOrReadOnly]

    def get_queryset(self):
        queryset = Mobile.objects.all().order_by("-created_at")
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
        mobile = self.get_object()
        quantity = int(request.query_params.get('quantity', 1))
        has_stock = mobile.stock >= quantity
        return Response({
            'product_id': mobile.id,
            'stock': mobile.stock,
            'required': quantity,
            'has_stock': has_stock
        })

    @action(detail=True, methods=['post'])
    def reduce_stock(self, request, pk=None):
        """Reduce stock by quantity"""
        mobile = self.get_object()
        quantity = int(request.data.get('quantity', 1))
        
        if mobile.stock < quantity:
            return Response(
                {'error': f'Insufficient stock. Available: {mobile.stock}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        mobile.stock -= quantity
        mobile.save()
        return Response({
            'product_id': mobile.id,
            'stock_reduced': quantity,
            'remaining_stock': mobile.stock
        })
