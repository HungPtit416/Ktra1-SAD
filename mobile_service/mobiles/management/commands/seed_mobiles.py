from django.core.management.base import BaseCommand

from mobiles.models import Mobile


class Command(BaseCommand):
    help = "Seed sample mobiles for testing"

    def handle(self, *args, **options):
        mobiles = [
            {
                "name": "iPhone 15",
                "price": "21990000.00",
                "brand": "Apple",
                "specs": "6.1-inch, A16, 128GB",
                "stock": 20,
            },
            {
                "name": "iPhone 15 Pro",
                "price": "27990000.00",
                "brand": "Apple",
                "specs": "6.1-inch, A17 Pro, 256GB",
                "stock": 12,
            },
            {
                "name": "Samsung Galaxy S24",
                "price": "19990000.00",
                "brand": "Samsung",
                "specs": "6.2-inch, Exynos/Snapdragon, 256GB",
                "stock": 25,
            },
            {
                "name": "Samsung Galaxy Z Flip5",
                "price": "22990000.00",
                "brand": "Samsung",
                "specs": "Foldable 6.7-inch, 256GB",
                "stock": 9,
            },
            {
                "name": "Xiaomi 14",
                "price": "16990000.00",
                "brand": "Xiaomi",
                "specs": "6.36-inch, Snapdragon 8 Gen 3, 256GB",
                "stock": 22,
            },
            {
                "name": "OPPO Find X7",
                "price": "18990000.00",
                "brand": "OPPO",
                "specs": "6.78-inch, 256GB",
                "stock": 14,
            },
            {
                "name": "Google Pixel 8",
                "price": "17990000.00",
                "brand": "Google",
                "specs": "6.2-inch, Tensor G3, 128GB",
                "stock": 11,
            },
            {
                "name": "vivo V30",
                "price": "10990000.00",
                "brand": "vivo",
                "specs": "6.78-inch, 256GB",
                "stock": 19,
            },
        ]

        created = 0
        updated = 0

        for item in mobiles:
            _, was_created = Mobile.objects.update_or_create(name=item["name"], defaults=item)
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded mobiles: created={created}, updated={updated}"))
