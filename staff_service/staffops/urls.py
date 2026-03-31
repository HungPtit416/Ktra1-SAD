from django.urls import path
from .views import ProductProxyDetailView, ProductProxyView

urlpatterns = [
    path("products/", ProductProxyView.as_view(), name="products-proxy"),
    path("products/<str:product_type>/<int:product_id>/", ProductProxyDetailView.as_view(), name="products-proxy-detail"),
]
