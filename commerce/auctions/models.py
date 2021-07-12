from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


# define possible categories
category_choices = (
    ("none", "None"),
    ("electronics", "Electronics"),
    ("fashion", "Fashion"),
    ("toys", "Toys"),
    ("home", "Home & Garden"),
    ("sports", "Sports"),
    ("auto", "Automotive"),
)



class Listing(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=256)
    starting_bid = models.FloatField(max_length=64)
    image = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=64, choices=category_choices, default="none")

    def __str__(self):
        return f"Title: {self.title}"
    

class Bid(models.Model):
    pass

class Comment(models.Model):
    pass


class Category(models.Model):
    pass