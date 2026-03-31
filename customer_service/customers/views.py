import requests
from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer


def _fetch_catalog(query=""):
    laptop_url = f"{settings.LAPTOP_SERVICE_URL}/api/laptops/"
    mobile_url = f"{settings.MOBILE_SERVICE_URL}/api/mobiles/"

    products = []
    errors = []

    try:
        laptop_resp = requests.get(laptop_url, params={"search": query}, timeout=5)
        laptop_resp.raise_for_status()
        for item in laptop_resp.json():
            item["product_type"] = "laptop"
            products.append(item)
    except requests.RequestException as exc:
        errors.append({"service": "laptop-service", "error": str(exc)})

    try:
        mobile_resp = requests.get(mobile_url, params={"search": query}, timeout=5)
        mobile_resp.raise_for_status()
        for item in mobile_resp.json():
            item["product_type"] = "mobile"
            products.append(item)
    except requests.RequestException as exc:
        errors.append({"service": "mobile-service", "error": str(exc)})

    products.sort(key=lambda x: x.get("id", 0), reverse=True)
    return products, errors


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProductSearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get("q", "")
        products, errors = _fetch_catalog(query=query)

        return Response(
            {"query": query, "products": products, "errors": errors},
            status=status.HTTP_200_OK,
        )
