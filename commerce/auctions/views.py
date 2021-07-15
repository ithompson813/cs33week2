from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.db.models import Max

from .models import Comment, User, Listing, Bid, category_choices

# default route for the site
def index(request):
    
    # show a list of all active listings
    return render(request, "auctions/index.html", {

        "listings": Listing.objects.filter(is_active=True),
        "header_text": "All Active Listings"

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


# shows a list of available categories to user
def category_list(request):

    # pass the category_choices list defined in models.py to site to display
    return render(request, "auctions/categories.html", {
    
        "categories": category_choices

    })


# shows active listings in a chosen category
def category_options(request, category):

    # aggregate all active lisings of desired category
    list_of_listings = Listing.objects.filter(category = category, is_active=True)

    # pass info to html page and display
    return render(request, "auctions/categories/category.html", {

        "listings": list_of_listings,
        "category": category

    })


# django form for creating a new listing
class NewListingForm(forms.Form):
    title = forms.CharField(label = "Title")
    description = forms.CharField(widget=forms.Textarea, label = "Description")
    starting_bid = forms.FloatField(label = "Starting Bid")
    image = forms.CharField(label = "Image Link", required = False)
    category = forms.CharField(label= "Category", widget=forms.Select(choices=category_choices))
    

# create a new listing
@login_required
def create(request):

    # for get requests, display the form
    if request.method == "GET":
        return render(request, "auctions/create.html", {

            "form": NewListingForm()

        })

    # when received as a post request, attempt to create new listing
    elif request.method == "POST":

        # store data received from NewListingForm
        form = NewListingForm(request.POST)
        
        # check data validity
        if form.is_valid():

            form_title = form.cleaned_data["title"]
            form_description = form.cleaned_data["description"]
            form_starting_bid = form.cleaned_data["starting_bid"]
            form_image = form.cleaned_data["image"]
            form_category = form.cleaned_data["category"]

            # check if a listing already exists
            number_of_results = Listing.objects.filter(title = form_title).count()

            if number_of_results > 0:
                return HttpResponse("Error: Title not unique")

            # create and save new listing item with data from form
            listing = Listing(title=form_title, description=form_description, category=form_category,
                                 starting_bid=form_starting_bid, image=form_image, creator=request.user)
            listing.save()

            # create a starting bid for the item
            bid = Bid(amount=form_starting_bid, item=listing, bidder=request.user)
            bid.save()

            # return user to index
            return HttpResponseRedirect(reverse("index"))

        # if data is invalid, return user to form
        else: 
            return render(request, "auctions/create.html", {
                "form": form
            })


# display listing page
def listing(request, listing):

    # store listing object
    listing_to_display = Listing.objects.get(title=listing)

    # determine max bid by first aggregating all bids on the listing and selecting the max by value amount
    all_bids = Bid.objects.filter(item = listing_to_display)
    highest_bid_amount = all_bids.aggregate(Max('amount'))
    highest_bid = Bid.objects.get(item = listing_to_display, amount = highest_bid_amount['amount__max'])
    
    # get comment data
    comments = Comment.objects.filter(item=listing_to_display)

    # get user's watchlist data if user is signed in
    if request.user.is_anonymous:
        watchlist = None
    else:
        watchlist = request.user.saved_listing.all()

    # render html page with this data
    return render(request, "auctions/listings/listing.html", {

        "listing": listing_to_display,
        'bid': highest_bid,
        "bid_count": all_bids.count(),
        "current_user": request.user,
        "comments": comments,
        "watchlist": watchlist
        
    })


# add a bid to a listing
@login_required
def bid(request):
    
    # retrieve listing title from html
    title = request.GET.get('listing')

    # use title to find listing object from database
    listing = Listing.objects.get(title=title)

    # retrieve bid amount from html
    amount = request.GET.get('amount')

    try:

        # check if new bid is greater than current price
        if (float(amount) > listing.starting_bid):

            # create and save bid
            bid = Bid(amount=amount, item=listing, bidder=request.user)
            bid.save()

            # update listing's current price
            listing.starting_bid = amount
            listing.save()

            # return user to listings page
            return HttpResponseRedirect(reverse("index"))

        # display an error if bid is below current price
        else:
            return HttpResponse("Your bid was too low!")

    # protect against non-numeric bids
    except ValueError:
        return HttpResponse("Invalid Bid")


# closes an active listing
@login_required
def close(request):

    # retrieve data from html form
    title = request.GET.get('listing')

    # save listing to variable
    item = Listing.objects.get(title=title)

    # deactivate listing
    item.is_active = False
    item.save()
    
    # return to listing page
    return (listing(request, item))


# add a comment to a listing page
@login_required
def comment(request):

    # retrieve data from html form
    title = request.GET.get('listing')
    text = request.GET.get('text')

    # save listing to variable
    item = Listing.objects.get(title=title)

    # create and save new comment
    comment = Comment(text=text, item=item, writer=request.user)
    comment.save()

    # return user to listing page
    return (listing(request, item))


# display listings in user's watchlist
@login_required
def watchlist(request):

    # retrieve listings in user's watchlist
    saved_listings = request.user.saved_listing.all()

    # pass info the html page and display
    # this method shares the index.html, but renders a different headline
    return render(request, "auctions/index.html", {

        "listings": saved_listings,
        "header_text": "Watchlist"

    })


# save a listing to a user's watchlist
@login_required
def save_listing(request):

    # retrieve data from html form
    title = request.GET.get('listing')

    # save listing to variable
    item = Listing.objects.get(title=title)

    # add listing to user's watchlist
    request.user.saved_listing.add(item)
    request.user.save()

    # return to page
    return listing(request, item)


# remove a listing from user's watchlist
@login_required
def remove_listing(request):

    # retrieve data from html form
    title = request.GET.get('listing')

    # save listing to variable
    item = Listing.objects.get(title=title)

    # remove listing from user's watchlist
    request.user.saved_listing.remove(item)
    request.user.save()

    # return to page
    return listing(request, item)


