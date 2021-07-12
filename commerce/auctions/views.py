from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listing


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

            return HttpResponseRedirect(reverse("index"))

        else: 
            return render(request, "auctions/create.html", {
                "form": form
            })
