from decimal import Decimal

import requests
from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsStaffUser
from .serializers import ProductProxySerializer


def convert_decimals(obj):
    """Convert Decimal objects to float for JSON serialization."""
    if isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, Decimal):
        return float(obj)
    return obj


class ProductProxyView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsStaffUser]

    def _target_url(self, product_type, product_id=None):
        if product_type == "laptop":
            base = f"{settings.LAPTOP_SERVICE_URL}/api/laptops/"
        else:
            base = f"{settings.MOBILE_SERVICE_URL}/api/mobiles/"
        return f"{base}{product_id}/" if product_id else base

    def get(self, request):
        result = []
        errors = []

        for product_type, base_url in [
            ("laptop", f"{settings.LAPTOP_SERVICE_URL}/api/laptops/"),
            ("mobile", f"{settings.MOBILE_SERVICE_URL}/api/mobiles/"),
        ]:
            try:
                resp = requests.get(base_url, timeout=5)
                resp.raise_for_status()
                items = resp.json()
                for item in items:
                    item["product_type"] = product_type
                result.extend(items)
            except requests.RequestException as exc:
                errors.append({"service": product_type, "error": str(exc)})

        return Response({"products": result, "errors": errors})

    def post(self, request):
        serializer = ProductProxySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        product_type = data.pop("product_type")
        url = self._target_url(product_type)

        # Convert Decimal to float for JSON serialization, then forward with internal key
        data = convert_decimals(data)
        headers = {"X-Internal-API-Key": settings.INTERNAL_API_KEY}
        resp = requests.post(url, json=data, headers=headers, timeout=5)
        return Response(resp.json(), status=resp.status_code)


class ProductProxyDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsStaffUser]

    def _target_url(self, product_type, product_id):
        if product_type == "laptop":
            return f"{settings.LAPTOP_SERVICE_URL}/api/laptops/{product_id}/"
        return f"{settings.MOBILE_SERVICE_URL}/api/mobiles/{product_id}/"

    def put(self, request, product_type, product_id):
        if product_type not in ["laptop", "mobile"]:
            return Response({"detail": "Invalid product_type"}, status=status.HTTP_400_BAD_REQUEST)
        url = self._target_url(product_type, product_id)
        data = convert_decimals(request.data)
        headers = {"X-Internal-API-Key": settings.INTERNAL_API_KEY}
        resp = requests.put(url, json=data, headers=headers, timeout=5)
        return Response(resp.json(), status=resp.status_code)

    def delete(self, request, product_type, product_id):
        if product_type not in ["laptop", "mobile"]:
            return Response({"detail": "Invalid product_type"}, status=status.HTTP_400_BAD_REQUEST)
        url = self._target_url(product_type, product_id)
        headers = {"X-Internal-API-Key": settings.INTERNAL_API_KEY}
        resp = requests.delete(url, headers=headers, timeout=5)
        if resp.content:
            return Response(resp.json(), status=resp.status_code)
        return Response(status=resp.status_code)
