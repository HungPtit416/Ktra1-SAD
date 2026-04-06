from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenVerifyView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("carts.urls")),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
