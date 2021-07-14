from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.category_list, name="categories"),
    path("categories/<str:category>", views.category_options, name="category_options"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("create", views.create, name="create"),
    path("listings/<str:listing>", views.listing, name="listing"),
    path("bid", views.bid, name="bid"),
    path("close", views.close, name="close"),
    path("comment", views.comment, name="comment")
]
