from django.contrib import admin

# Register your models here.
from .models import Tweet, TweetLike, User

admin.site.register(User)
admin.site.register(Tweet)
admin.site.register(TweetLike)
#admin.site.register(Profile)

