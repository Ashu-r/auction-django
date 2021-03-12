from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import *


def index(request):
    listings = ListingItem.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def specific_category(request, this_category):
    listings = ListingItem.objects.filter(item_category=this_category.title())
    return render(request, "auctions/index.html", {
        "listings": listings,
        "category": this_category.title(),
    })


@login_required
def new_listing(request):
    categories = Category.objects.all()
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        image_url = request.POST["image_url"]
        item_category = []
        for category in categories:
            if category.name in request.POST:
                item_category.append(category)
                # print(request.POST[category])
        try:
            current_time = timezone.now()
            user = ListingItem(title=title, description=description,
                               starting_bid=starting_bid, image_url=image_url, time_created=current_time, seller=request.user)

            user.save()
            if request.POST["new_cat"]:
                new_category = Category(name=request.POST["new_cat"].title())
                new_category.save()
                item_category.append(new_category)
            user.item_category.set(item_category)

        except Exception as e:
            return render(request, "auctions/new_listing.html", {
                "message": e
            })
        return HttpResponseRedirect(reverse("index"))

    else:

        return render(request, "auctions/new_listing.html", {
            "categories": categories
        })


@login_required
def watchlist(request):
    pass
