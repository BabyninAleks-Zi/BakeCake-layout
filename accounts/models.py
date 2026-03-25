from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random

class Profile(models.Model):
    user = models.OneToOneField(
    	User,
    	on_delete=models.CASCADE,
    	null=True,
    	blank=True
    )
    phone = models.CharField(
    	max_length=20,
    	unique=True,
    	null=True,
    	blank=True
    )
    

class SMSCode(models.Model):
    phone = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

    @staticmethod
    def generate_code():
        return f"{random.randint(100000, 999999)}"
