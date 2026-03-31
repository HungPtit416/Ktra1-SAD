from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from staffops.models import StaffProfile


class Command(BaseCommand):
    help = "Seed sample staff users for testing"

    def handle(self, *args, **options):
        staff_accounts = [
            {
                "username": "staff01",
                "email": "staff01@example.com",
                "password": "Staff@123",
                "role": "manager",
            },
            {
                "username": "staff02",
                "email": "staff02@example.com",
                "password": "Staff@123",
                "role": "operator",
            },
        ]

        created_users = 0
        updated_users = 0

        for item in staff_accounts:
            user, was_created = User.objects.get_or_create(
                username=item["username"],
                defaults={"email": item["email"]},
            )
            user.email = item["email"]
            user.set_password(item["password"])
            user.is_active = True
            user.is_staff = True
            user.save()

            StaffProfile.objects.update_or_create(
                user_id=user.id,
                defaults={"role": item["role"]},
            )

            if was_created:
                created_users += 1
            else:
                updated_users += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded staff: created={created_users}, updated={updated_users}"))
