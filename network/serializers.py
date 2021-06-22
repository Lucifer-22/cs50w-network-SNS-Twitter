from django.db.models import fields
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from .models import Tweet, TweetLike, User, Profile

MAX_TWEET_LENGTH = 500
TWEET_ACTION_OPTIONS = ["like", "unlike", "retweet"]
TO_FOLLOW = ["follow", "unfollow"]

class TweetActionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    action = serializers.CharField()
    content = serializers.CharField(allow_blank = True, required = False)

    def validate_action(self, value):
        value = value.lower().strip()
        if not value in TWEET_ACTION_OPTIONS:
            raise serializers.ValidationError("Not a valid action")

        return value


class TweetCreateSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = Tweet
        fields = ['id', 'content', 'likes']
        
    def get_likes(self, obj):
        return obj.likes.count()
        
    def validate_content(self, value):
        if len(value) > MAX_TWEET_LENGTH:
            raise serializers.ValidationError("This tweet is too long")

        return value

class TweetUserSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only = True)
    followers = serializers.SerializerMethodField(read_only = True)
    followings = serializers.SerializerMethodField(read_only = True)
    username = serializers.CharField()
    currentUser = serializers.CharField()
    action = serializers.CharField()

    def validate_action(self, value):
        value = value.lower().strip()
        if not value in TO_FOLLOW:
            raise serializers.ValidationError("Not a valid action")

        return value


    class Meta:
        model = Profile
        fields = ['id', 'user', 'followers', 'following']

    def get_user(self, obj):
        return obj.user.username

    def get_followers(self, obj):
        return obj.followers.count()

    def get_followings(self, obj):
        return obj.followings.count()


class TweetSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField(read_only = True)
    user = serializers.SerializerMethodField(read_only = True)
    #parent = TweetCreateSerializer(read_only = True)
    timestamp = serializers.DateTimeField()

    class Meta:
        model = Tweet
        fields = ['id', 'content','user', 'likes', 'timestamp']
        
    def get_likes(self, obj):
        return obj.likes.count()

    def get_user(self, obj):
        return obj.user.username

    def get_timestamp(self, obj):
        return obj.timestamp

    
