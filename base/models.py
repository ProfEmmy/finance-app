from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.FloatField()
    account_number = models.BigIntegerField(editable=True, unique=True)
    account_name = models.CharField(max_length=200)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.account_name

class Action(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="senders_account")
    receiver_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="receivers_account")
    amount = models.IntegerField()
    transaction_type = models.CharField(max_length=100)
    updated = models.DateTimeField(auto_now=True, editable=True)
    created = models.DateTimeField(auto_now_add=True, editable=True)

    class Meta:
        ordering = ['-created', '-updated']

    def __str__(self):
        return f'{self.account.account_name} {self.transaction_type}ed {self.amount} to {self.receiver_account.account_name}'