from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<int:id>", views.item, name="item"),
    path("new_comment/<int:listing>", views.new_comment, name="new_comment"),
    path("remove_watchlist/<int:listing>", views.remove_watchlist, name="remove_watchlist"),
    path("add_watchlist/<int:listing>", views.add_watchlist, name="add_watchlist"),
    path("close_auction/<int:listing>", views.close_auction, name="close_auction"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("categories_page", views.categories_page, name="categories_page"),
    path("category_page/<str:category>", views.category_page, name="category_page"),
    path("watchlist_page", views.watchlist_page, name="watchlist_page")

]
