from django.db import models


class StaffProfile(models.Model):
    user_id = models.IntegerField(unique=True)
    role = models.CharField(max_length=100, default="manager")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"StaffProfile<{self.user_id}>"
