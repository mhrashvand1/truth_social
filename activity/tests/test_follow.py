from activity.tests.base_test import BaseTest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from activity.models import Follow
from account.models import User
# from channels.testing import WebsocketCommunicator


class TestFollow(BaseTest):
    
    def test_follow_unfollow(self):
        client_a = APIClient()
        client_a.force_authenticate(user=self.user_a)
        client_b = APIClient()
        client_b.force_authenticate(user=self.user_b)        
        client_c = APIClient()
        client_c.force_authenticate(user=self.user_c)        
        client_d = APIClient()
        client_d.force_authenticate(user=self.user_d)        
        client_e = APIClient()
        client_e.force_authenticate(user=self.user_e)        
        client_f = APIClient()
        client_f.force_authenticate(user=self.user_f)        

        response = client_a.post(
            reverse('activity:follow'),
            data={"username":self.user_a.username},
            format='json'
        )
        res = response.json()
        self.assertEqual(response.status_code, 400),
        self.assertEqual(res['username'][0], 'Can not follow/unfollow yourself.')

        ################
        response = client_a.post(
            reverse('activity:follow'),
            data={"username":self.user_b.username},
            format='json'
        )
        res = response.json()
        self.assertEqual(response.status_code, 200),
        
        response = client_b.get(
            reverse('activity:user-followed_you', kwargs={"username":self.user_a.username}),
            format='json'
        )
        res = response.json()
        self.assertEqual(res['followed_you'], True),
        
        response = client_a.post(
            reverse('activity:follow'),
            data={"username":self.user_b.username},
            format='json'
        )
        res = response.json()
        self.assertEqual(response.status_code, 400),
        self.assertEqual(res['username'][0], f'User with username {self.user_b.username} has already followed.')
        
        #############
        response = client_c.post(
            reverse('activity:block-block'),
            data={"username":self.user_a.username},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        
        response = client_a.post(
            reverse('activity:follow'),
            data={"username":self.user_c.username},
            format='json'
        )
        res = response.json()
        self.assertEqual(response.status_code, 400),
        self.assertEqual(
            res['username'][0],
            f'You can not follow user with username {self.user_c.username} , because you are blocked.'
        )
        
        ###########
        response = client_a.post(
            reverse('activity:block-block'),
            data={"username":self.user_d.username},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        
        response = client_a.post(
            reverse('activity:follow'),
            data={"username":self.user_d.username},
            format='json'
        )
        res = response.json()
        self.assertEqual(response.status_code, 400),
        self.assertEqual(
            res['username'][0],
            f'You can not follow user with username {self.user_d.username} , bacause you have blocked it.'
        )
        
        ##############
        
        response = client_a.post(
            reverse('activity:unfollow'),
            data={"username":self.user_b.username},
            format='json'
        )
        res = response.json()
        self.assertEqual(response.status_code, 200),
        
        response = client_a.post(
            reverse('activity:unfollow'),
            data={"username":self.user_b.username},
            format='json'
        )
        res = response.json()
        self.assertEqual(response.status_code, 400),
        self.assertEqual(
            res['username'][0],
            f'User with username {self.user_b.username} is not followed.'
        )
        
        client_x = APIClient()
        response = client_x.get(
            reverse('activity:user-followed_you', kwargs={"username":self.user_a.username}),
            format='json'
        )
        self.assertEqual(response.status_code, 401),
        
        ##################################################################
        ################### for testing channels #########################
        # client.login(username='a', password='a')
        # print("\n\n", client.session.items(), "\n\n")
        # cl = WebsocketCommunicator(...)
        # cl.scope.update({'user':self.user_a, 'session':client.session})
        ##################################################################


    def test_followers_followings(self):
        client_a = APIClient()
        client_a.force_authenticate(user=self.user_a)
        client_b = APIClient()
        client_b.force_authenticate(user=self.user_b)        
        client_c = APIClient()
        client_c.force_authenticate(user=self.user_c)        
        client_d = APIClient()
        client_d.force_authenticate(user=self.user_d)        
        client_e = APIClient()
        client_e.force_authenticate(user=self.user_e)        
        client_f = APIClient()
        client_f.force_authenticate(user=self.user_f)   
        
        
        response = client_a.post(
            reverse('activity:follow'),
            data={"username":self.user_b.username},
            format='json'
        )
        self.assertEqual(response.status_code, 200),
        
        response = client_a.post(
            reverse('activity:follow'),
            data={"username":self.user_c.username},
            format='json'
        )
        self.assertEqual(response.status_code, 200),
        
        response = client_a.post(
            reverse('activity:follow'),
            data={"username":self.user_d.username},
            format='json'
        )
        self.assertEqual(response.status_code, 200),
        
        
        client_x = APIClient()
        response = client_x.get(
            reverse(
                'activity:user-followings',
                kwargs={"username":self.user_a.username}
            )
        )
        res = response.json()
        self.assertEqual(res['count'], 3)
        
        response = client_x.get(
            reverse(
                'activity:user-followers',
                kwargs={"username":self.user_b.username}
            )
        )
        res = response.json()
        self.assertEqual(res['count'], 1)
        


    def test_followed_by_others_you_now(self):        
        client_a = APIClient()
        client_a.force_authenticate(user=self.user_a)
        client_b = APIClient()
        client_b.force_authenticate(user=self.user_b)        
        client_c = APIClient()
        client_c.force_authenticate(user=self.user_c)        
        client_d = APIClient()
        client_d.force_authenticate(user=self.user_d)        
        client_e = APIClient()
        client_e.force_authenticate(user=self.user_e)        
        client_f = APIClient()
        client_f.force_authenticate(user=self.user_f)  
        
        
        # user_a follows user_d, user_e, user_f
        response = client_a.post(
            reverse('activity:follow'),
            data={"username":self.user_d.username},
            format='json'
        )
        self.assertEqual(response.status_code, 200),
        
        response = client_a.post(
            reverse('activity:follow'),
            data={"username":self.user_e.username},
            format='json'
        )
        self.assertEqual(response.status_code, 200),
        
        response = client_a.post(
            reverse('activity:follow'),
            data={"username":self.user_f.username},
            format='json'
        )
        self.assertEqual(response.status_code, 200),
        
        
        # user_c, user_d, user_f, user_e  follows user_b
        response = client_c.post(
            reverse('activity:follow'),
            data={"username":self.user_b.username},
            format='json'
        )
        self.assertEqual(response.status_code, 200),   
        
        response = client_d.post(
            reverse('activity:follow'),
            data={"username":self.user_b.username},
            format='json'
        )
        self.assertEqual(response.status_code, 200),   
        
        response = client_f.post(
            reverse('activity:follow'),
            data={"username":self.user_b.username},
            format='json'
        )
        self.assertEqual(response.status_code, 200),   
        
        
        response = client_e.post(
            reverse('activity:follow'),
            data={"username":self.user_b.username},
            format='json'
        )
        self.assertEqual(response.status_code, 200),   
               
        # test followed_by    
        response = client_a.get(
            reverse(
                'activity:user-followed_by',
                kwargs={"username":self.user_b.username}
            )
        )
        res = response.json()
        self.assertEqual(res['count'], 3)
        usernames = (
            res['results'][0]['username'], 
            res['results'][1]['username'],
            res['results'][2]['username']
        )
        self.assertEqual('d' in usernames, True)
        self.assertEqual('e' in usernames, True)        
        self.assertEqual('f' in usernames, True)
        self.assertEqual('c' in usernames, False)
        
        
    def test_delete_bell_after_unfollow(self):

        client_a = APIClient()
        client_a.force_authenticate(user=self.user_a)
        client_b = APIClient()
        client_b.force_authenticate(user=self.user_b)        
        client_c = APIClient()
        client_c.force_authenticate(user=self.user_c)        
        client_d = APIClient()
        client_d.force_authenticate(user=self.user_d)        
        client_e = APIClient()
        client_e.force_authenticate(user=self.user_e)        
        client_f = APIClient()
        client_f.force_authenticate(user=self.user_f)  
        
        
        response = client_a.post(
            reverse('activity:follow'),
            data={"username":self.user_b.username},
            format='json'
        )
        res = response.json()
        self.assertEqual(response.status_code, 200),
        
        response = client_a.post(
            reverse('notification:bell-enable_bell'),
            data={'username':self.user_b.username, 'priority':3}
        )
        self.assertEqual(response.status_code, 200)
        
        response = client_a.post(
            reverse('notification:bell-bell_status'),
            data={"username":self.user_b.username}
        )
        res = response.json()
        self.assertEqual(res['status'], 'enable')
        
        # Now user_a unfollow user_b
        response = client_a.post(
            reverse('activity:unfollow'),
            data={"username":self.user_b.username},
            format='json'
        )
        res = response.json()
        self.assertEqual(response.status_code, 200),
        
        # Then:
        response = client_a.post(
            reverse('notification:bell-bell_status'),
            data={"username":self.user_b.username}
        )
        res = response.json()
        self.assertEqual(res['status'], 'disable')
        