from django.urls import path
from .views import ProductSearchView, RegisterView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("products/search/", ProductSearchView.as_view(), name="product-search"),
]
