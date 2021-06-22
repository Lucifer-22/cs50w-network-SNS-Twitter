from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.expressions import OrderBy
from django.conf import settings
from django.urls import reverse
from django.utils import tree
from django.db.models.signals import post_save
from django.db.models import Q



class User(AbstractUser):
    pass

class FollowerRelation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #followings = models.ManyToManyField( "User", 
    #                                    blank=True, 
    #                                    related_name="following")
    followers = models.ManyToManyField(User,blank=True, related_name="followings", through= FollowerRelation)
    timestamp = models.DateTimeField(auto_now_add=True)

    
    
    def __str__(self):
        return f"{self.user} follows {self.followers}"

class TweetLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tweet = models.ForeignKey("Tweet", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True) 

class TweetQuerySet(models.QuerySet):
    def feed(self, user):
        profiles_exist = user.followings.exists()
        followed_users_id = []
        if profiles_exist:
            followed_users_id = user.followings.values_list("user__id", flat=True)
        return self.filter(
            Q(user__id__in = followed_users_id) |
            Q(user = user)
        ).distinct().order_by("-timestamp")

class TweetManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return TweetQuerySet(self.model, using =self._db)
    
    def feed(self, user):
        return self.get_queryset().feed(user)


class Tweet(models.Model):
    parent = models.ForeignKey("self", null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField( User,
                                    related_name="likes",
                                    related_query_name="likes",
                                    through=TweetLike,
                                    blank=True)

    objects = TweetManager()
    class meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.content[:10]} ... by => {self.user}"

    @property
    def is_retweet(self):
        return self.parent != None

    def serialize(self):
        return {
            "id": self.id,
            "content": self.content,
            "likes": 0,
            "timestamp": self.timestamp,
        }
'''
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower", null=True, blank=True)
    #following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following", null=True, blank=True)

    def __str__(self):
        return f"{self.follower} follows {self.following}"
'''
def user_did_save(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.get_or_create(user = instance)

post_save.connect(user_did_save, sender = User)