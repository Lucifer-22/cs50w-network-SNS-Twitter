from re import template
from django.core import paginator
from network.serializers import TweetSerializer
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, response
from django.http.response import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.generic import UpdateView

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import permissions, serializers
from rest_framework.pagination import PageNumberPagination
from .forms import TweetForm
from .models import (User, Tweet, TweetLike, Profile)
from .serializers import TweetSerializer, TweetCreateSerializer, TweetActionSerializer, TweetUserSerializer

def index(request):
    return render(request, "network/index.html")

def myfeed(request):
    return render(request, "network/myfeed.html")

def profile(request):
    return render(request, "network/profile.html")


@api_view(['POST', 'GET'])
@permission_classes((permissions.AllowAny, permissions.IsAuthenticated))
def tweet_create_view(request, *args, **kwargs):
    serializer = TweetCreateSerializer(data = request.POST)
    if serializer.is_valid(raise_exception=True):
        serializer.save(user = request.user)
        return Response(serializer.data, status = 201)
    return Response({}, status = 400)


@permission_classes((permissions.AllowAny, permissions.IsAuthenticated))
def tweet_edit_view(request, tweet_id, *args, **kwargs):
    qs = Tweet.objects.filter(id = tweet_id)
    if not qs.exists():
        return JsonResponse({}, status = 404)
    qs = qs.filter(user = request.user)
    if not qs.exists():
        return JsonResponse({"message": "You are not permitted to delete this tweet."}, status = 401)
    post = qs.first()
    if request.method == 'POST':
        form = TweetForm(request.POST, instance = post)
        if form.is_valid():
            form.save()
            return render(request, 'network/edit.html', context={"form": form, "tweet": post})
    else:
        form = TweetForm(instance = post)

    if form.errors:
        if request.is_ajax():
            return JsonResponse(form.errors, status = 400)
    return render(request, 'network/edit.html', context={"form": form, "tweet": post})

    
@api_view(['GET'])
@permission_classes((permissions.AllowAny, permissions.IsAuthenticated))
def tweet_list_view(request, *args, **kwargs):
    paginator = PageNumberPagination()
    paginator.page_size = 10
    qs = Tweet.objects.order_by("-timestamp").all()
    paginated_qs = paginator.paginate_queryset(qs, request)
    serializer = TweetSerializer(paginated_qs, many=True)
    context = {
        "currentUser": request.user.username,
        "tweets": serializer.data,
    }
    return paginator.get_paginated_response(context)
    #return Response(serializer.data, status=200)


@api_view(['GET'])
@permission_classes((permissions.AllowAny, permissions.IsAuthenticated))
def tweet_feed_view(request, *args, **kwargs):
    user = request.user
    qs = Tweet.objects.feed(user)
    paginator = PageNumberPagination()
    paginator.page_size = 10
    paginated_qs = paginator.paginate_queryset(qs, request)
    serializer = TweetSerializer(paginated_qs, many=True)
    context = {
        "currentUser": request.user.username,
        "tweets": serializer.data,
    }
    return paginator.get_paginated_response(context)
    #return Response(serializer.data, status=200)


@api_view(['GET'])
@permission_classes((permissions.AllowAny, permissions.IsAuthenticated))
def tweet_detail_view(request, tweet_id, *args, **kwargs):
    qs = Tweet.objects.filter(id = tweet_id)
    if not qs.exists():
        return Response({}, status = 404)
    obj = qs.first()
    serializer = TweetSerializer(obj)
    return Response(serializer.data, status = 200)
    

@api_view(['DELETE', 'POST', 'GET'])
@permission_classes((permissions.AllowAny, permissions.IsAuthenticated))
def tweet_delete_view(request, tweet_id, *args, **kwargs):
    qs = Tweet.objects.filter(id = tweet_id)
    if not qs.exists():
        return Response({}, status = 404)
    qs = qs.filter(user = request.user)
    if not qs.exists():
        return Response({"message": "You are not permitted to delete this tweet."}, status = 401)
    obj = qs.first()
    #print(qs)
    obj.delete()
    return Response({"message": "Tweet Removed"}, status = 200)

@api_view(['POST'])
@permission_classes((permissions.AllowAny, permissions.IsAuthenticated))
def tweet_action_view(request, *args, **kwargs):
    serializer = TweetActionSerializer(data = request.data)
    if serializer.is_valid(raise_exception=True):
        data = serializer.validated_data
        tweet_id = data.get("id")
        action = data.get("action")
        content = data.get("content")
        qs = Tweet.objects.filter(id = tweet_id)
        if not qs.exists():
            return Response({}, status = 404)
        obj = qs.first()
        if (action == "like"):
            obj.likes.add(request.user)
            serializer = TweetSerializer(obj)
            return Response(serializer.data, status = 200)
        elif (action == "unlike"):
            obj.likes.remove(request.user)
        elif (action == "retweet"):
            parent_obj = obj
            new_tweet = Tweet.objects.create(user = request.user, 
                                            parent = parent_obj,
                                            content = content)
            serializer = TweetSerializer(new_tweet)
            return Response(serializer.data, status = 200)        
    return Response({}, status = 200)

@api_view(['GET'])
@permission_classes((permissions.AllowAny, permissions.IsAuthenticated))
def profile_detail_view(request, username, *args, **kwargs):
    profileUser = User.objects.get(username = username)
    posts_qs = Tweet.objects.filter(user = profileUser).order_by("-timestamp").all()
    currentUser = request.user
    current_User_info = User.objects.get(username = currentUser.username)
    is_profile = username

    if currentUser.username == username:
        is_profile = currentUser.username

    profile_followers = profileUser.profile.followers.all().count()
    profile_following = profileUser.followings.all().count()
    
    if currentUser in profileUser.profile.followers.all():  #profileUser.followings.filter(user = currentUser).exists():
        is_followed = True
    else:
        is_followed = False

    #paginator = Paginator(posts_qs, 10)
    #page_number = request.GET.get('page')
    #page_obj = paginator.get_page(page_number)
    #serializer = TweetSerializer(page_obj, many = True)
    paginator=PageNumberPagination()
    paginator.page_size = 10
    paginated_qs = paginator.paginate_queryset(posts_qs, request)
    serializer = TweetSerializer(paginated_qs, many = True)

    context = {        
        "isProfile": is_profile,
        "currentUser_name": currentUser.username,
        "followers": profile_followers,
        "followings": profile_following,
        "isFollowed": is_followed,
        "Tweets": serializer.data,
    }
    return paginator.get_paginated_response(context)
    #return Response(context)

@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny, permissions.IsAuthenticated))
def user_follow_view(request, username, *args, **kwargs):
    currentUser = request.user
    profileUser_qs = User.objects.filter(username = username) 
    #profileUser_qs = Profile.objects.filter(user__username = username)
    
    if currentUser.username == username:
        currentUserFollowers = currentUser.profile.followers.all()
        context = {
            "followers": currentUser.profile.followers.all().count(),
            "followings": currentUser.followings.all().count()
        }
        return Response(context, status=200)

    if not profileUser_qs.exists():
        return Response({}, status = 404)
    profileUser = profileUser_qs.first()
    #profile = profileUser.profile
    data = request.data or {}
    action = data.get("action")
    if action == "unfollow":          # currentUser in profileUser.followers.all():
        profileUser.profile.followers.remove(currentUser)
    elif action == "follow":
        profileUser.profile.followers.add(currentUser)
    else:
        pass
    
    context = {
        "followers": profileUser.profile.followers.all().count(),
        "followings": profileUser_qs.first().followings.all().count(),
    }
    return Response(context, status=200)



'''

def tweet_create_view_check(request, *args, **kwargs):
    user = request.user
    if not request.user.is_authenticated:
        user = None
        if request.is_ajax():
            return JsonResponse({}, status = 401)
        return render(request, "network/login.html")

    form = TweetForm(request.POST)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = user 
        obj.save()
        if request.is_ajax():
            return JsonResponse(obj.serialize(), status=201) #201 is for creted items
    if form.errors:
        if request.is_ajax():
            return JsonResponse(form.errors, status = 400)
    return render(request, 'network/form.html', context={"form": form})


def tweet_list_view_pure(request, *args, **kwargs):
    qs = Tweet.objects.all()
    tweet_list = [x.serialize() for x in qs]
    data = {
        "isUser": False,
        "response":tweet_list
    }
    return JsonResponse(data)

def tweet_detail_view(request, tweet_id, *args, **kwargs):
    data={
        "id": tweet_id,
    }
    status = 200
    try:
        obj = Tweet.objects.get(id = tweet_id)
        data['content'] = obj.content
    except:
        data['message'] = "Not Found"
        status = 404   
    
    return JsonResponse(data, status=status)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def tweet_create_view_rest(request, *args, **kwargs):
    serializer = TweetCreateSerializer(data = request.POST)
    if serializer.is_valid(raise_exception=True):
        serializer.save(user = request.user)
        return Response(serializer.data, status = 201)
    return Response({}, status = 400)


@api_view(['GET'])
@permission_classes((permissions.AllowAny, permissions.IsAuthenticated))
def tweet_feed_view(request, *args, **kwargs):
    user = request.user
    following_profiles = user.followings.all()
    followed_users_id = []
    if following_profiles.exists():
        followed_users_id = [x.user.id for x in following_profiles]
    followed_users_id.append(user.id)
    paginator = PageNumberPagination()
    paginator.page_size = 10
    qs = Tweet.objects.filter(user__id__in = followed_users_id).order_by("-timestamp").all()
    paginated_qs = paginator.paginate_queryset(qs, request)
    serializer = TweetSerializer(paginated_qs, many=True)
    return paginator.get_paginated_response(serializer.data)
    #return Response(serializer.data, status=200)
'''



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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
