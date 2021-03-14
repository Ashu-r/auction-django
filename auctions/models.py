from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField(
        'ListingItem', related_name="users_on_watchlist", blank=True)

    def __str__(self):
        return self.username


class ListingItem(models.Model):
    is_active = models.BooleanField(default=True)
    title = models.CharField(max_length=20)
    description = models.CharField(max_length=100)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    time_created = models.DateTimeField()
    item_category = models.ManyToManyField(
        "Category", related_name="item", blank=True)
    image_url = models.URLField(max_length=150, blank=True)
    seller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='listings')

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=20, unique=True, primary_key=True)
    # item = models.ManyToManyField(
    #     ListingItem, related_name='categories')

    def __str__(self):
        return self.name


class Bid(models.Model):
    bidder = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='bids')
    bidding_time = models.DateTimeField()
    bidding_amount = models.DecimalField(
        max_digits=10, decimal_places=2)
    item = models.ForeignKey(
        ListingItem, on_delete=models.CASCADE, related_name='biddings')

    def __str__(self):
        return str(self.bidding_amount)


class Comment(models.Model):
    listing = models.ForeignKey(
        ListingItem, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    comment_text = models.CharField(max_length=250)
    likes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.comment_text
