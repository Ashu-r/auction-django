from django.contrib import admin
from .models import User, ListingItem, Category, Bid, Comment
# Register your models here.

admin.site.register(User)
admin.site.register(ListingItem)
admin.site.register(Category)
admin.site.register(Bid)
admin.site.register(Comment)
