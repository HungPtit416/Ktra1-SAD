from django.core.management.base import BaseCommand

from laptops.models import Laptop


class Command(BaseCommand):
    help = "Seed sample laptops for testing"

    def handle(self, *args, **options):
        laptops = [
            # Budget laptops under 20M
            {
                "name": "Acer Aspire 5 15",
                "price": "14990000.00",
                "brand": "Acer",
                "specs": "Intel Core i5-1235U, 8GB RAM, 512GB SSD, 15.6 FHD",
                "stock": 25,
            },
            {
                "name": "HP 15s-fq5110TU",
                "price": "15990000.00",
                "brand": "HP",
                "specs": "Intel Core i5, 8GB RAM, 512GB SSD, 15.6 inch",
                "stock": 22,
            },
            {
                "name": "Dell Inspiron 15 3520",
                "price": "16990000.00",
                "brand": "Dell",
                "specs": "Intel Core i5-12450H, 8GB RAM, 512GB SSD",
                "stock": 20,
            },
            {
                "name": "ASUS Vivobook 15 X1504ZA",
                "price": "17990000.00",
                "brand": "ASUS",
                "specs": "Intel Core i5-1240P, 8GB RAM, 512GB SSD, 15.6 FHD",
                "stock": 18,
            },
            
            # Mid-range laptops 20-30M
            {
                "name": "Lenovo IdeaPad 5 Pro",
                "price": "21990000.00",
                "brand": "Lenovo",
                "specs": "Intel Core i7-12700H, 16GB RAM, 512GB SSD, 16 inch",
                "stock": 16,
            },
            {
                "name": "HP Pavilion 15-eg0xxx",
                "price": "22990000.00",
                "brand": "HP",
                "specs": "Intel Core i7, 16GB RAM, 512GB SSD, 15.6 inch Touch",
                "stock": 15,
            },
            {
                "name": "ASUS TUF Gaming A15",
                "price": "23990000.00",
                "brand": "ASUS",
                "specs": "AMD Ryzen 7, RTX 3050, 16GB RAM, 512GB SSD",
                "stock": 14,
            },
            {
                "name": "Dell G15 5530",
                "price": "24990000.00",
                "brand": "Dell",
                "specs": "Intel Core i7-13700H, RTX 4060, 16GB RAM, 512GB SSD",
                "stock": 12,
            },
            {
                "name": "MSI Modern 14 B13M",
                "price": "25990000.00",
                "brand": "MSI",
                "specs": "Intel Core i7-1360P, 16GB RAM, 512GB SSD, 14 inch",
                "stock": 13,
            },
            
            # Gaming/High-Performance 30-40M
            {
                "name": "ASUS ROG Strix G16",
                "price": "31990000.00",
                "brand": "ASUS",
                "specs": "Intel Core i7-13700H, RTX 4070, 16GB RAM, 1TB SSD, 16 inch",
                "stock": 10,
            },
            {
                "name": "MSI Stealth GS77 12UE",
                "price": "32990000.00",
                "brand": "MSI",
                "specs": "Intel Core i7-12700H, RTX 3080 Ti, 32GB RAM, 1TB SSD",
                "stock": 9,
            },
            {
                "name": "Razer Blade 15 Studio",
                "price": "35990000.00",
                "brand": "Razer",
                "specs": "Intel Core i7, RTX 4060, 16GB RAM, 1TB SSD, OLED Display",
                "stock": 8,
            },
            {
                "name": "Dell Alienware m16",
                "price": "36990000.00",
                "brand": "Dell",
                "specs": "Intel Core i9-13900K, RTX 4090, 32GB RAM, 1TB SSD",
                "stock": 7,
            },
            
            # Premium/Ultrabook 35-50M
            {
                "name": "Dell XPS 13 Plus",
                "price": "36990000.00",
                "brand": "Dell",
                "specs": "Intel Core Ultra 7, 16GB RAM, 1TB SSD, 13.4 OLED",
                "stock": 10,
            },
            {
                "name": "HP Spectre x360 16",
                "price": "38990000.00",
                "brand": "HP",
                "specs": "Intel Core i7-1365U, Iris Xe, 32GB RAM, 1TB SSD, OLED Touch",
                "stock": 9,
            },
            {
                "name": "Lenovo ThinkPad X1 Carbon Gen 12",
                "price": "42990000.00",
                "brand": "Lenovo",
                "specs": "Intel Core Ultra 7, 32GB RAM, 1TB SSD, 14 OLED",
                "stock": 8,
            },
            {
                "name": "ASUS ZenBook 14 OLED",
                "price": "39990000.00",
                "brand": "ASUS",
                "specs": "AMD Ryzen 7, 16GB RAM, 1TB SSD, 14 OLED, 1.39kg",
                "stock": 11,
            },
            
            # Mac ecosystem 30-50M
            {
                "name": "MacBook Air M3 13",
                "price": "28990000.00",
                "brand": "Apple",
                "specs": "M3, 16GB RAM, 512GB SSD, 13.6 inch Retina",
                "stock": 12,
            },
            {
                "name": "MacBook Air M3 15",
                "price": "32990000.00",
                "brand": "Apple",
                "specs": "M3, 16GB RAM, 512GB SSD, 15.3 inch Retina",
                "stock": 10,
            },
            {
                "name": "MacBook Pro M3 14",
                "price": "49990000.00",
                "brand": "Apple",
                "specs": "M3 Pro, 18GB RAM, 512GB SSD, 14.2 inch ProMotion",
                "stock": 7,
            },
            {
                "name": "MacBook Pro M3 Max 16",
                "price": "59990000.00",
                "brand": "Apple",
                "specs": "M3 Max, 36GB RAM, 1TB SSD, 16 inch ProMotion",
                "stock": 5,
            },
            
            # Work & Development laptops 25-45M
            {
                "name": "Framework Laptop 16",
                "price": "27990000.00",
                "brand": "Framework",
                "specs": "Intel Core i7-1360P, RTX 4060, 32GB RAM, 1TB SSD, Modular",
                "stock": 6,
            },
            {
                "name": "System76 Lemur Pro",
                "price": "24990000.00",
                "brand": "System76",
                "specs": "Intel Core i7-1360P, 32GB RAM, 1TB SSD, Linux Optimized",
                "stock": 8,
            },
            {
                "name": "Purism Librem 14",
                "price": "28990000.00",
                "brand": "Purism",
                "specs": "Intel Core i7, 32GB RAM, 1TB SSD, Privacy-focused",
                "stock": 5,
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

