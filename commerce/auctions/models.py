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
    ("health", "Health")
)



class Listing(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=256)
    starting_bid = models.FloatField(max_length=64)
    image = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=64, choices=category_choices, default="none")

    def __str__(self):
        return f"{self.title}"

    def title_to_url(self):
        return self.title.replace(" ", "-")
    

class Bid(models.Model):
    amount = models.FloatField(max_length=10, default=0)
    bidder = models.ForeignKey('User', on_delete=models.CASCADE)
    item = models.ForeignKey('Listing', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"A bid for {self.amount} on {self.item} by {self.bidder}"
    

class Comment(models.Model):
    pass


class Category(models.Model):
    pass