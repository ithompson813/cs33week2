from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=256)
    starting_bid = models.FloatField(max_length=64)
    image = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"Title: {self.title}, Desc: {self.description}, Starting Bid: {self.starting_bid}"
    

class Bid(models.Model):
    pass

class Comment(models.Model):
    pass

class Category(models.Model):
    pass