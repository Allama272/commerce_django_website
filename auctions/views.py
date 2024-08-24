from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, Auction, Bids, Comments, Categories
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Add a comment', 'rows': 4}),
        }
        labels = {
            "text": ""
        }


class BidForm(forms.ModelForm):
    class Meta:
        model = Bids
        fields = ["price"]
        widgets = {
            "price": forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Place Your Bid!'}),
        }
        labels = {"price": ""}


class CreateListingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateListingForm, self).__init__(*args, **kwargs)
        self.fields['price'].widget.attrs['min'] = 1

    class Meta:
        model = Auction
        fields = ["title", "description", "price", "category", "photo"]
        widgets = {
            "title": forms.TextInput(attrs={'class': 'form-control'}),
            "description": forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            "price": forms.NumberInput(attrs={'class': 'form-control'}),
            "category": forms.Select(attrs={'class': 'form-control'}),
            "photo": forms.URLInput(attrs={'class': 'form-control'})
        }
        labels = {
            "price": "Starting Price:",
            "photo": "Link To Photo (Optional):"
        }


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Auction.objects.all().annotate(highest_bid=Max('bidders__price'))
    })


def categories_page(request):
    categories_list = [[i, j] for i, j in Categories.choices]
    categories_list[0][0] = "NOTHING"

    return render(request, "auctions/categories_page.html", {
        "categories": categories_list})


def find_title(category):
    for i, j in Categories.choices:
        if i.lower() == category.lower():
            return j
        if category == 'Nothing':
            return "None"
    return None


def category_page(request, category):
    listings = Auction.objects.filter(category=category)

    return render(request, "auctions/category_page.html", {
        "listings": listings,
        "category": find_title(category)
    })


def watchlist_page(request):
    listings_watched = request.user.watching.all()
    print(listings_watched)
    return render(request, "auctions/watchlist_page.html", {
        "listings": listings_watched,
    })


def create_listing(request):
    if request.method == "POST":
        print("entered here")
        listing_filled = CreateListingForm(request.POST)
        if int(listing_filled.data["price"]) <= 0:
            messages.error(request, "Price Must Be Higher Than 0")
            return HttpResponseRedirect(reverse("create_listing"))
        listing_row = listing_filled.save(commit=False)
        listing_row.owner = request.user
        listing_row.save()
        print("creating")
        return HttpResponseRedirect(reverse("index"))
    create_form = CreateListingForm()

    return render(request, "auctions/create_listing.html", {
        "create_form": create_form
    })


@login_required
def new_comment(request, listing):
    if request.method == "POST":
        comment = CommentForm(request.POST)
        if comment.is_valid():
            comment_row = comment.save(commit=False)
            comment_row.user = request.user
            comment_row.auction = Auction.objects.get(id=listing)
            comment_row.save()
            return HttpResponseRedirect(reverse("item", args={listing, }))
        else:
            return HttpResponseRedirect(reverse("item", args={listing, }))


@login_required
def remove_watchlist(request, listing):
    if request.method == "POST":
        item_to_remove = Auction.objects.get(id=listing)
        item_to_remove.watchers.remove(request.user)
        return HttpResponseRedirect(reverse("item", args={listing, }))


@login_required
def add_watchlist(request, listing):
    if request.method == "POST":
        item = Auction.objects.get(id=listing)
        item.watchers.add(request.user)
        return HttpResponseRedirect(reverse("item", args={listing, }))


def close_auction(request, listing):
    if request.method == "POST":
        item = Auction.objects.get(id=listing)
        item_owner = item.owner
        if item_owner == request.user:
            item.active = False
            item.save()
            messages.success(request, "Auction Successfully Closed")
        else:
            messages.error(request, "Must Be The Auction Owner To End The Auction")
        return HttpResponseRedirect(reverse("item", args={listing, }))


def item(request, id):
    listing = Auction.objects.get(id=id)
    try:
        highest_bidder = listing.bidders.all().order_by('-price').first()
        highest_bidder_name = User.objects.filter(id=highest_bidder.user_id).first().username
        total_biddings = listing.bidders.all().count()
    except:
        highest_bidder = None
        highest_bidder_name = None
        total_biddings = 0
    current_user = request.user

    # bid form
    if request.method == "POST":
        bid = BidForm(request.POST)
        highest_price = highest_bidder
        if highest_price is None:
            highest_price = 0
        else:
            highest_price = highest_bidder.price
        if not listing.active:
            messages.error(request, "Auction Is Closed")
            return HttpResponseRedirect(reverse("item", args={listing.id, }))
        if bid.is_valid() and int(bid.data["price"]) > int(highest_price) and int(bid.data["price"]) >= listing.price:
            bid_row = bid.save(commit=False)
            bid_row.user = request.user
            bid_row.auction = listing
            bid_row.save()
            messages.success(request, "Bid Placed Successfully")
            return HttpResponseRedirect(reverse("item", args={listing.id, }))
        else:
            messages.error(request, f"Bid Must Be Higher Than The Highest Bid: {highest_price} & At Least Equal To "
                                    f"The Original Price: {listing.price}")
            return HttpResponseRedirect(reverse("item", args={listing.id, }))
    watching = User.objects.filter(watching=listing, id=current_user.id).exists()
    comments = listing.commenters.all()
    user_ids = comments.values_list('user_id', flat=True)
    users = User.objects.in_bulk(user_ids)
    comment_form = CommentForm()
    bid_form = BidForm()
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watching": watching,
        "highest_bidder": highest_bidder,
        "total_biddings": total_biddings,
        "highest_bidder_name": highest_bidder_name,
        "comments": comments,
        "users": users,
        "comment_form": comment_form,
        "bid_form": bid_form
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
