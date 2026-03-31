from rest_framework import serializers


class ProductProxySerializer(serializers.Serializer):
    product_type = serializers.ChoiceField(choices=["laptop", "mobile"])
    name = serializers.CharField(max_length=200)
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    brand = serializers.CharField(max_length=100)
    specs = serializers.CharField()
    stock = serializers.IntegerField(min_value=0)
