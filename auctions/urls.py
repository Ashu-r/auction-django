from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('categories', views.categories, name="categories"),
    path('categories/<str:this_category>',
         views.specific_category, name="category"),
    path('watchlist', views.watchlist, name="watchlist"),
    path('new', views.new_listing, name="new_listing"),
    path('listing/<int:id>', views.listing, name="listing"),
    path('listing/<int:id>/watchlist_toggle',
         views.watchlist_toggle, name="watchlist_toggle")
]
