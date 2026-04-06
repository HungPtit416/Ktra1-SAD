from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sessions', views.ChatViewSet, basename='sessions')
router.register(r'analysis', views.BehaviorAnalysisViewSet, basename='analysis')

app_name = 'advisor'

urlpatterns = [
    path('', include(router.urls)),
]
