from django.db import models


class CustomerMeta(models.Model):
    user_id = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CustomerMeta<{self.user_id}>"
