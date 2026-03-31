from django.core.management.base import BaseCommand

from laptops.models import Laptop


class Command(BaseCommand):
    help = "Seed sample laptops for testing"

    def handle(self, *args, **options):
        laptops = [
            {
                "name": "MacBook Air M3 13",
                "price": "28990000.00",
                "brand": "Apple",
                "specs": "M3, 16GB RAM, 512GB SSD, 13-inch",
                "stock": 12,
            },
            {
                "name": "MacBook Pro M3 Pro 14",
                "price": "49990000.00",
                "brand": "Apple",
                "specs": "M3 Pro, 18GB RAM, 512GB SSD, 14-inch",
                "stock": 7,
            },
            {
                "name": "Dell XPS 13 Plus",
                "price": "36990000.00",
                "brand": "Dell",
                "specs": "Intel Core Ultra 7, 16GB RAM, 1TB SSD",
                "stock": 10,
            },
            {
                "name": "Dell Inspiron 15",
                "price": "17990000.00",
                "brand": "Dell",
                "specs": "Intel Core i5, 16GB RAM, 512GB SSD",
                "stock": 20,
            },
            {
                "name": "HP Pavilion 14",
                "price": "18990000.00",
                "brand": "HP",
                "specs": "Intel Core i5, 16GB RAM, 512GB SSD",
                "stock": 16,
            },
            {
                "name": "Lenovo ThinkPad X1 Carbon Gen 12",
                "price": "42990000.00",
                "brand": "Lenovo",
                "specs": "Intel Core Ultra 7, 32GB RAM, 1TB SSD",
                "stock": 8,
            },
            {
                "name": "ASUS ROG Zephyrus G14",
                "price": "40990000.00",
                "brand": "ASUS",
                "specs": "Ryzen 9, RTX 4060, 16GB RAM, 1TB SSD",
                "stock": 6,
            },
            {
                "name": "Acer Aspire 5",
                "price": "15990000.00",
                "brand": "Acer",
                "specs": "Intel Core i5, 8GB RAM, 512GB SSD",
                "stock": 18,
            },
        ]

        created = 0
        updated = 0

        for item in laptops:
            _, was_created = Laptop.objects.update_or_create(name=item["name"], defaults=item)
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded laptops: created={created}, updated={updated}"))
