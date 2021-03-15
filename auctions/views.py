from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import fields
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import *


def index(request):
    listings = ListingItem.objects.filter(is_active=True)
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
        if not password:
            return render(request, "auctions/register.html", {
                "message": "Please enter the password."
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
    listings = ListingItem.objects.filter(
        item_category=this_category.title(), is_active=True)
    return render(request, "auctions/index.html", {
        "listings": listings,
        "category": this_category.title(),
    })


def listing(request, id):
    listing_item = ListingItem.objects.get(id=int(id))
    bidding_placed = True if listing_item.biddings.last() else False
    last_bid = listing_item.biddings.last(
    ).bidding_amount if bidding_placed else listing_item.starting_bid
    comments = listing_item.comments.filter(active=True)

    try:
        request.user.watchlist.get(id=listing_item.id)
        on_watchlist = True
    except:
        on_watchlist = False

    if request.method == "POST":
        invalid_request = False
        if 'comment_text' in request.POST:
            comment_text = request.POST['comment_text']
            new_comment = Comment(
                listing=listing_item, author=request.user, comment_text=comment_text)
            new_comment.save()
            messages.success(request, "Your comment has been added.")

        else:
            bid = float(request.POST["bid"])
            if bidding_placed:
                if not bid > last_bid:
                    messages.success(
                        request, f"Your bid of {bid} should be more than\n {last_bid}. Please bid higher.")
                    invalid_request = True

            elif not bid >= last_bid:
                messages.success(
                    request, f"Your bid of {bid} should be more than\n or should match {last_bid}. Please bid higher.")
                invalid_request = True
            if not invalid_request:
                try:
                    bid = Bid(bidder=request.user, bidding_time=timezone.now(),
                              bidding_amount=bid, item=listing_item)
                    bid.save()
                    messages.success(
                        request, f"Your bid of {bid} is successfully\n placed.")
                except Exception as e:
                    messages.success(request, e)

        return HttpResponseRedirect(reverse('listing', kwargs={'id': id}))

    # messages.success(request, None)
    return render(request, "auctions/listing.html", {
        "item": listing_item,
        "on_watchlist": on_watchlist,
        'comments': comments,
    })


@ login_required
def watchlist_toggle(request, id):
    listing_item = ListingItem.objects.get(id=int(id))
    try:
        request.user.watchlist.get(id=listing_item.id)
        on_watchlist = True
    except:
        on_watchlist = False
    if on_watchlist:
        request.user.watchlist.remove(listing_item)
        return HttpResponseRedirect(reverse('listing', kwargs={'id': id}))
    request.user.watchlist.add(listing_item)
    return HttpResponseRedirect(reverse('listing', kwargs={'id': id}))


@ login_required
def close_bidding(request, id):
    listing_item = ListingItem.objects.get(id=int(id))
    if not listing_item.seller.get_username() == request.user.username:
        return HttpResponse("Access Denied")
    listing_item.is_active = False
    listing_item.save()
    return HttpResponseRedirect(reverse('listing', kwargs={'id': id}))


@ login_required
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


@ login_required
def watchlist(request):
    listings = request.user.watchlist.all()
    return render(request, "auctions/index.html", {
        "listings": listings,
        "heading": "Watchlist",
    })
