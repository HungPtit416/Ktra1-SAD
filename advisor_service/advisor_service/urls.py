"""
URL configuration for advisor_service project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from advisor.views import ChatViewSet, BehaviorAnalysisViewSet

router = DefaultRouter()
router.register(r'chat', ChatViewSet, basename='chat')
router.register(r'behavior', BehaviorAnalysisViewSet, basename='behavior')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/advisor/', include('advisor.urls')),
]
