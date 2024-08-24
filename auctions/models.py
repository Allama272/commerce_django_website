from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now


class Categories(models.TextChoices):
    NOTHING = "", "NONE"
    ELECTRONICS = "ELEC", "Electronics"
    CLOTHING = "CLTH", "Clothing"
    TOYS = "TOYS", "Toys"
    FOOD = "FOOD", "Food and Beverage"
    FURNITURE = "FURN", "Furniture and Decor"
    MEDICINE = "MEDI", "Medicine"
    OFFICE = "OFIC", "Office Equipment"
    OTHER = "OTHR", "Others"


class User(AbstractUser):
    pass


class Auction(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=64)
    description = models.TextField()
    price = models.PositiveIntegerField()
    category = models.CharField(choices=Categories.choices,  max_length=4,default=Categories.NOTHING, blank=True, null=True)
    photo = models.TextField(max_length=2048, default=None, blank=True, null=True)
    active = models.BooleanField(default=True)
    watchers = models.ManyToManyField(User, related_name="watching", default=None, blank=True, null=True)
    created_date = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.title} by  {self.owner}"


class Bids(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="biddings")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bidders")
    price = models.PositiveIntegerField()


class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="commenters")
    text = models.TextField()
    created_date = models.DateTimeField(default=now)

