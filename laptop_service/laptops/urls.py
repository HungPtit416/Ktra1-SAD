from rest_framework.routers import DefaultRouter
from .views import LaptopViewSet

router = DefaultRouter()
router.register("laptops", LaptopViewSet, basename="laptop")

urlpatterns = router.urls
