from django.db import models

from account.models import Account


class PhoneNumber(models.Model):
    number = models.CharField(max_length=40)
    account_id = models.ForeignKey(Account, on_delete=models.CASCADE, db_column='account_id')

    class Meta:
        db_table = "phone_number"
