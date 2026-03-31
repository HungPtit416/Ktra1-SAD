from django.conf import settings
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsInternalOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.headers.get("X-Internal-API-Key") == settings.INTERNAL_API_KEY
