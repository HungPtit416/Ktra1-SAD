from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from carts.models import Cart, CartItem
from customers.models import CustomerMeta


class Command(BaseCommand):
    help = "Seed sample customer users and carts for testing"

    def handle(self, *args, **options):
        customers = [
            {
                "username": "customer01",
                "email": "customer01@example.com",
                "password": "Customer@123",
            },
            {
                "username": "customer02",
                "email": "customer02@example.com",
                "password": "Customer@123",
            },
            {
                "username": "customer03",
                "email": "customer03@example.com",
                "password": "Customer@123",
            },
        ]

        created_users = 0
        updated_users = 0

        for item in customers:
            user, was_created = User.objects.get_or_create(
                username=item["username"],
                defaults={"email": item["email"]},
            )
            user.email = item["email"]
            user.set_password(item["password"])
            user.is_active = True
            user.save()

            CustomerMeta.objects.update_or_create(user_id=user.id)

            cart, _ = Cart.objects.get_or_create(user=user)
            if item["username"] == "customer01":
                CartItem.objects.update_or_create(
                    cart=cart,
                    product_type="laptop",
                    product_id=1,
                    defaults={"quantity": 1},
                )
                CartItem.objects.update_or_create(
                    cart=cart,
                    product_type="mobile",
                    product_id=1,
                    defaults={"quantity": 2},
                )

            if was_created:
                created_users += 1
            else:
                updated_users += 1

        self.stdout.write(
            self.style.SUCCESS(f"Seeded customers: created={created_users}, updated={updated_users}")
        )
