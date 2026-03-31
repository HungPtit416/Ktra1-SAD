from rest_framework import viewsets
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
