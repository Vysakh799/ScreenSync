from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Create your models here.


def generate_admin_code():
    return str(uuid.uuid4()).split("-")[0].upper()

class User(AbstractUser):
    admin_code = models.CharField(
        max_length=20,
        unique=True,
        default=generate_admin_code,
        null=True,
        blank=True
    )

class Session(models.Model):
    admin = models.ForeignKey(User,on_delete=models.CASCADE,related_name='sessions')
    student_name = models.CharField(max_length=100)
    joined_at = models.DateTimeField(auto_now_add=True,null=True)
    is_active = models.BooleanField(default=True)
