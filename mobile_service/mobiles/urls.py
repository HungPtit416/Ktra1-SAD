from rest_framework.routers import DefaultRouter
from .views import MobileViewSet

router = DefaultRouter()
router.register("mobiles", MobileViewSet, basename="mobile")

urlpatterns = router.urls
