from django.db import models


class Account(models.Model):
    auth_id = models.CharField(max_length=40)
    username = models.CharField(max_length=40)

    class Meta:
        db_table = "account"
