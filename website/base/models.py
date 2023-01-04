from django.db import models
from django.contrib.auth import get_user_model
from responder.models import (
    Admin

)


User = get_user_model()


class ShortenedUrl(models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)
    hash_code = models.CharField(max_length=15, null=True)
    given_url = models.CharField(max_length=250)
    shortened_url = models.CharField(max_length=250)

    def __str__(self):
        return self.given_url


class Messenger(models.Model):
    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name
        
class Support(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    messenger = models.ForeignKey(Messenger, on_delete=models.CASCADE)
    msgr_id = models.CharField(max_length=20)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    is_close = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

class DefaultNotification(models.Model):
    user_default = models.TextField(null=True,blank=True)
    visitor_default = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.user_default

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.TextField(null=True,blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Contact(models.Model):
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15,blank=True, null=True)
    skype = models.CharField(max_length=25,blank=True, null=True)
    telegram = models.CharField(max_length=25,blank=True, null=True)

    def __str__(self):
        return self.email

class Chat(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    sent = models.TextField(blank=True, null=True)
    received = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_created = models.BooleanField(default=False)

    def __str__(self):
        return self.admin.username

class CronTest(models.Model):
    test = models.CharField(max_length=50)

    def __str__(self):
        return self.test