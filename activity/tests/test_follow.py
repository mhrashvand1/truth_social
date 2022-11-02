
from activity.tests.base_test import BaseTest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from activity.models import Follow
from account.models import User

class TestFollow(BaseTest):
    
    def test_get_followers_and_followings(self):
        # client = APIClient()
        # client.force_authenticate()
        # client.post(
        #     reverse(),
        #     data={},
        #     format='json'
        # )
        
        Follow.objects.create(from_user=self.user_a, to_user=self.user_f)
        Follow.objects.create(from_user=self.user_b, to_user=self.user_f)
        Follow.objects.create(from_user=self.user_c, to_user=self.user_f)

        Follow.objects.create(from_user=self.user_f, to_user=self.user_a)
        Follow.objects.create(from_user=self.user_f, to_user=self.user_d)
        Follow.objects.create(from_user=self.user_f, to_user=self.user_e)

        f_followers = self.user_f.followers.all()
        f_followings = self.user_f.followings.all()
        self.assertEqual(
            (
                self.user_a in f_followers, 
                self.user_b in f_followers, 
                self.user_e in f_followers,
                self.user_e in f_followings
            ),
            (True, True, False, True)
        )
        
