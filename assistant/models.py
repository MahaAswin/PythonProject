from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        swappable = 'AUTH_USER_MODEL'

class VoiceCommand(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='voice_commands')
    command = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'voice_commands'
        ordering = ['-timestamp']
