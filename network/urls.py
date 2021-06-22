
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("myfeed", views.myfeed, name="myfeed"),
    path("profile", views.profile, name="profile"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("login", views.login_view, name="login"),
    path("tweets", views.tweet_list_view, name="tweet_list_view"),
    path("feeds", views.tweet_feed_view, name="tweet_feed_view"),
    path("tweet-create", views.tweet_create_view, name="tweet_create_view"),
    path("tweets/<int:tweet_id>", views.tweet_detail_view, name="tweet_detail_view"),
    path("api/tweets/action", views.tweet_action_view, name="tweet_action_view"),
    path("api/tweets/<int:tweet_id>/delete", views.tweet_delete_view, name="tweet_delete_view"),
    path("api/tweets/<int:tweet_id>/edit", views.tweet_edit_view, name="tweet_edit_view"),
    path("profile/<str:username>", views.profile_detail_view, name="profile_detail_view"),
    #path("follow/<int:id>", views.follow, name="follow"),
    path("profile/<str:username>/action", views.user_follow_view, name="user_follow_view"),
]
