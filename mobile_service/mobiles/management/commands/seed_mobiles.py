from django.core.management.base import BaseCommand

from mobiles.models import Mobile


class Command(BaseCommand):
    help = "Seed sample mobiles for testing"

    def handle(self, *args, **options):
        mobiles = [
            # Budget phones under 10M
            {
                "name": "vivo Y36",
                "price": "5990000.00",
                "brand": "vivo",
                "specs": "MediaTek Helio G99, 4GB RAM, 128GB, 6.51 inch",
                "stock": 30,
            },
            {
                "name": "Xiaomi Redmi Note 12",
                "price": "7490000.00",
                "brand": "Xiaomi",
                "specs": "Snapdragon 4 Gen 1, 6GB RAM, 128GB, 6.67 AMOLED",
                "stock": 28,
            },
            {
                "name": "Realme C35",
                "price": "6990000.00",
                "brand": "Realme",
                "specs": "Snapdragon 680, 4GB RAM, 128GB, 6.5 inch",
                "stock": 25,
            },
            {
                "name": "OPPO A17k",
                "price": "6990000.00",
                "brand": "OPPO",
                "specs": "MediaTek Helio G88, 4GB RAM, 128GB, 6.5 inch",
                "stock": 26,
            },
            
            # Mid-budget 10-15M
            {
                "name": "Samsung Galaxy A54",
                "price": "12990000.00",
                "brand": "Samsung",
                "specs": "Exynos 1280, 6GB RAM, 128GB, 6.4 AMOLED",
                "stock": 22,
            },
            {
                "name": "vivo V30",
                "price": "10990000.00",
                "brand": "vivo",
                "specs": "Snapdragon 8 Gen 3, 12GB RAM, 256GB, 6.78 OLED",
                "stock": 19,
            },
            {
                "name": "Xiaomi 14",
                "price": "12990000.00",
                "brand": "Xiaomi",
                "specs": "Snapdragon 8 Gen 3, 12GB RAM, 256GB, 6.36 AMOLED",
                "stock": 20,
            },
            {
                "name": "Motorola Edge 50",
                "price": "11990000.00",
                "brand": "Motorola",
                "specs": "Snapdragon 7 Gen 1, 8GB RAM, 256GB, 6.55 OLED",
                "stock": 17,
            },
            
            # Mid-range 15-20M
            {
                "name": "Samsung Galaxy S24",
                "price": "19990000.00",
                "brand": "Samsung",
                "specs": "Snapdragon 8 Gen 3, 8GB RAM, 256GB, 6.2 Dynamic AMOLED",
                "stock": 25,
            },
            {
                "name": "OPPO Find X7",
                "price": "18990000.00",
                "brand": "OPPO",
                "specs": "Snapdragon 8 Gen 3, 12GB RAM, 256GB, 6.78 AMOLED",
                "stock": 14,
            },
            {
                "name": "Google Pixel 8",
                "price": "17990000.00",
                "brand": "Google",
                "specs": "Tensor G3, 8GB RAM, 128GB, 6.2 OLED",
                "stock": 11,
            },
            {
                "name": "OnePlus 12",
                "price": "16990000.00",
                "brand": "OnePlus",
                "specs": "Snapdragon 8 Gen 3, 12GB RAM, 256GB, 6.7 AMOLED",
                "stock": 13,
            },
            
            # Premium 20-25M
            {
                "name": "iPhone 15",
                "price": "21990000.00",
                "brand": "Apple",
                "specs": "A17 Pro, 6GB RAM, 128GB, 6.1 Super Retina",
                "stock": 20,
            },
            {
                "name": "Samsung Galaxy S24+",
                "price": "23990000.00",
                "brand": "Samsung",
                "specs": "Snapdragon 8 Gen 3, 12GB RAM, 256GB, 6.7 Dynamic AMOLED 2X",
                "stock": 18,
            },
            {
                "name": "Xiaomi 14 Ultra",
                "price": "21990000.00",
                "brand": "Xiaomi",
                "specs": "Snapdragon 8 Gen 3, 16GB RAM, 512GB, 6.73 LTPO AMOLED",
                "stock": 15,
            },
            {
                "name": "vivo X100",
                "price": "22990000.00",
                "brand": "vivo",
                "specs": "MediaTek Dimensity 9300, 16GB RAM, 512GB, 6.78 AMOLED",
                "stock": 16,
            },
            
            # Flagship/Premium 25-30M
            {
                "name": "iPhone 15 Pro",
                "price": "27990000.00",
                "brand": "Apple",
                "specs": "A17 Pro, 8GB RAM, 256GB, 6.1 Super Retina Titanium",
                "stock": 12,
            },
            {
                "name": "Samsung Galaxy S24 Ultra",
                "price": "28990000.00",
                "brand": "Samsung",
                "specs": "Snapdragon 8 Gen 3, 12GB RAM, 256GB, 6.8 Dynamic AMOLED",
                "stock": 14,
            },
            {
                "name": "iPhone 15 Pro Max",
                "price": "32990000.00",
                "brand": "Apple",
                "specs": "A17 Pro, 8GB RAM, 256GB, 6.7 Super Retina Titanium",
                "stock": 10,
            },
            
            # Foldable & Special
            {
                "name": "Samsung Galaxy Z Flip5",
                "price": "22990000.00",
                "brand": "Samsung",
                "specs": "Snapdragon 8 Gen 2, 8GB RAM, 256GB, Foldable 6.7 OLED",
                "stock": 9,
            },
            {
                "name": "Samsung Galaxy Z Fold5",
                "price": "37990000.00",
                "brand": "Samsung",
                "specs": "Snapdragon 8 Gen 2, 12GB RAM, 256GB, Foldable 7.6 OLED",
                "stock": 7,
            },
            {
                "name": "Motorola Razr 40",
                "price": "21990000.00",
                "brand": "Motorola",
                "specs": "Snapdragon 8 Gen 1, 8GB RAM, 256GB, Foldable 6.9 OLED",
                "stock": 8,
            },
            
            # Gaming phones
            {
                "name": "ASUS ROG Phone 8",
                "price": "20990000.00",
                "brand": "ASUS",
                "specs": "Snapdragon 8 Gen 3, 16GB RAM, 512GB, 6.78 AMOLED 165Hz",
                "stock": 10,
            },
            {
                "name": "Xiaomi Black Shark 6 Pro",
                "price": "16990000.00",
                "brand": "Xiaomi",
                "specs": "Snapdragon 8 Gen 2 Ultra, 16GB RAM, 512GB, 6.78 AMOLED",
                "stock": 11,
            },
            
            # Budget premium
            {
                "name": "Nothing Phone 2a",
                "price": "9990000.00",
                "brand": "Nothing",
                "specs": "Snapdragon 7 Gen 1, 8GB RAM, 128GB, 6.7 AMOLED",
                "stock": 16,
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
