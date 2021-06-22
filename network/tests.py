from django.test import TestCase

# Create your tests here.
from .models import Profile, User

class ProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username = 'abc', password = '123')
        self.userb = User.objects.create_user(username = 'xyz', password = '1234')

    def test_profile_created(self):
        qs = Profile.objects.all()
        self.assertEqual(qs.count(), 2)

    def test_following(self):
        first = self.user
        second = self.userb
        first.profile.followers.add(second) # added a follower
        second_user_following_whom = second.followings.all()
        qs = second.followings.filter( user = first) # from a user check the other user is being followed
        first_user_following_no_one = first.followings.all() #check new user has no followings
        self.assertTrue(qs.exists())
        self.assertFalse(first_user_following_no_one.exists())


