from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.db.models import Max

from .models import User, Listing, Bid


def index(request):
    
    return render(request, "auctions/index.html", {

        "listings": Listing.objects.filter(is_active=True)

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
    return render(request, "auctions/index.html")

def watchlist(request):
    return render(request, "auctions/index.html")


# django form for creating a new listing
class NewListingForm(forms.Form):
    title = forms.CharField(label = "Title")
    description = forms.CharField(widget=forms.Textarea, label = "Description")
    starting_bid = forms.FloatField(label = "Starting Bid")
    image = forms.CharField(label = "Image Link", required = False)
    

@login_required
def create(request):

    # for get requests, display the form
    if request.method == "GET":
        return render(request, "auctions/create.html", {

            "form": NewListingForm()

        })

    elif request.method == "POST":

        form = NewListingForm(request.POST)

        
        if form.is_valid():

            form_title = form.cleaned_data["title"]
            form_description = form.cleaned_data["description"]
            form_starting_bid = form.cleaned_data["starting_bid"]
            form_image = form.cleaned_data["image"]

            listing = Listing(title=form_title, description=form_description, starting_bid=form_starting_bid, image=form_image)
            listing.save()

            bid = Bid(amount=form_starting_bid, item=listing, bidder=request.user)
            bid.save()

            return HttpResponseRedirect(reverse("index"))

        else: 
            return render(request, "auctions/create.html", {
                "form": form
            })


def listing(request, listing):

    listing_to_display = Listing.objects.get(title=listing)

    #if (Bid.objects.get(item = listing_to_display)):
        # highest_bid = Bid.objects.get(item = listing_to_display)
    all_bids = Bid.objects.filter(item = listing_to_display)
    highest_bid = all_bids.aggregate(Max('amount'))

    return render(request, "auctions/listings/listing.html", {

        "listing": listing_to_display,
        "bid": highest_bid['amount__max']
        
    })


def bid(request):
    
    # retrieve listing title from html
    title = request.GET.get('listing')

    # use title to find listing object from database
    listing = Listing.objects.get(title=title)

    # retrieve bid amount from html
    amount = request.GET.get('amount')

    try:

        # check new bid is greater than current price
        if (float(amount) > listing.starting_bid):

            # create and save bid
            bid = Bid(amount=amount, item=listing, bidder=request.user)
            bid.save()

            # update listing's current price
            listing.starting_bid = amount
            listing.save()

            return HttpResponseRedirect(reverse("index"))


        else:
            return HttpResponse("Your bid was too low!")


    # protect against non-numeric bids
    except ValueError:
        return HttpResponse("Invalid Bid")
