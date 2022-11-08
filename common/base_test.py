from rest_framework.test import APITestCase
from account.models import User, Profile
from activity.models import OnlineStatus


class BaseTest(APITestCase):
    def setUp(self):
        user_a = User.objects.create_user(
            username='a', password='a', email='a@gmail.com', name='a'
        )
        Profile.objects.create(user=user_a)
        OnlineStatus.objects.create(user=user_a)
        self.user_a = user_a
        
        user_b = User.objects.create_user(
            username='b', password='b', email='b@gmail.com', name='b'
        )
        Profile.objects.create(user=user_b)
        OnlineStatus.objects.create(user=user_b)
        self.user_b = user_b
        
        user_c = User.objects.create_user(
            username='c', password='c', email='c@gmail.com', name='c'
        )
        Profile.objects.create(user=user_c)
        OnlineStatus.objects.create(user=user_c)
        self.user_c = user_c

        user_d = User.objects.create_user(
            username='d', password='d', email='d@gmail.com', name='d'
        )
        Profile.objects.create(user=user_d)  
        OnlineStatus.objects.create(user=user_d)   
        self.user_d = user_d

        user_e = User.objects.create_user(
            username='e', password='e', email='e@gmail.com', name='e'
        )
        Profile.objects.create(user=user_e)
        OnlineStatus.objects.create(user=user_e)
        self.user_e = user_e

        user_f = User.objects.create_user(
            username='f', password='f', email='f@gmail.com', name='f'
        )
        Profile.objects.create(user=user_f) 
        OnlineStatus.objects.create(user=user_f)    
        self.user_f = user_f

        return super().setUp()
    
    
    def tearDown(self):
        return super().tearDown()