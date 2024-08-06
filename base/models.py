from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    name = models.CharField(verbose_name='Full Name',max_length=200,null=True)
    email=models.EmailField(unique=True,verbose_name='Email Address',max_length=254)
    image = models.ImageField(default='avatar.svg',null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    bio = models.TextField(null=True)
    
class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100,verbose_name='Group Name')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    description = models.TextField(max_length=1000, blank=True,null=True)
    participants = models.ManyToManyField(User,related_name='participants',blank=True)
    # likes = models.IntegerField()
    # likes = models.ManyToManyField(User,related_name='likes',blank=True)
    
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    # class Meta:
    #     ordering=['-updated','-created']

    def __str__(self):
        return self.name


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField(max_length=500)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-updated','-created']
    def __str__(self):
        return self.body[0:50]


