from notification.tests.base_test import BaseTest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from activity.models import Follow
from account.models import User


class TestBell(BaseTest):
    
    def test_enable_disable_bell(self):
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
            reverse('notification:bell-enable_bell'),
            data={"username":self.user_a.username, 'priority':3}
        )
        res = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(res['username'][0], f"You can not enable/disable the bell of yourself.")
        
        response = client_a.post(
            reverse('notification:bell-enable_bell'),
            data={"username":self.user_b.username, 'priority':3}
        )
        res = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            res['username'][0], 
            f'You can not enable the bell of user with username {self.user_b.username} , because you have not followed it.'
        )
        
        ##############
        response = client_a.post(
            reverse('activity:follow'),
            data={'username':self.user_b.username}
        )
        self.assertEqual(response.status_code, 200)
        
        response = client_a.post(
            reverse('notification:bell-enable_bell'),
            data={"username":self.user_b.username, 'priority':3}
        )
        res = response.json()
        self.assertEqual(response.status_code, 200)    
           
        response = client_a.post(
            reverse('notification:bell-enable_bell'),
            data={"username":self.user_b.username, 'priority':3}
        )
        res = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            res['username'][0], 
            f'The bell of user with username {self.user_b.username} has already enabled.'
        )
        ###########
        response = client_a.post(
            reverse('notification:bell-disable_bell'),
            data={"username":self.user_b.username, 'priority':3}
        )
        res = response.json()
        self.assertEqual(response.status_code, 200)
        
        response = client_a.post(
            reverse('notification:bell-disable_bell'),
            data={"username":self.user_b.username, 'priority':3}
        )
        res = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            res['username'][0], 
            f'The bell of user with username {self.user_b.username} is not enable.'
        )      
                 
    def test_bell_status(self):
        client_a = APIClient()
        client_a.force_authenticate(user=self.user_a)
        client_b = APIClient()
        client_b.force_authenticate(user=self.user_b)     
        
        response = client_a.post(
            reverse('notification:bell-bell_status'),
            data={'username':'bullshit'}
        )   
        self.assertEqual(response.status_code, 404)
                
        response = client_a.post(
            reverse('notification:bell-bell_status'),
            data={'username':self.user_b.username}
        )   
        res = response.json()
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(res['status'], 'disable')
        self.assertEqual(res['priority'], None)
        
        response = client_a.post(
            reverse('activity:follow'),
            data={'username':self.user_b.username}
        )
        self.assertEqual(response.status_code, 200)
        
        response = client_a.post(
            reverse('notification:bell-enable_bell'),
            data={"username":self.user_b.username, 'priority':3}
        )
        res = response.json()
        self.assertEqual(response.status_code, 200)    
            
        response = client_a.post(
            reverse('notification:bell-bell_status'),
            data={'username':self.user_b.username}
        )   
        res = response.json()
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(res['status'], 'enable')
        self.assertEqual(res['priority'], 3)
        
    
    def test_change_bell_priority(self):
        client_a = APIClient()
        client_a.force_authenticate(user=self.user_a)
        client_b = APIClient()
        client_b.force_authenticate(user=self.user_b)        

        response = client_a.put(
            reverse('notification:bell-change_priority'),
            data={'username':'bullshit', 'priority':3}
        )
        res = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            res['username'][0], 
            'User with username bullshit is not in your bell enablings.'
        )
        
        response = client_a.put(
            reverse('notification:bell-change_priority'),
            data={'username':self.user_b.username, 'priority':3}
        )
        res = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            res['username'][0], 
            f'User with username {self.user_b.username} is not in your bell enablings.'
        )
        
        ##########
        response = client_a.post(
            reverse('activity:follow'),
            data={'username':self.user_b.username}
        )
        self.assertEqual(response.status_code, 200)
        
        response = client_a.post(
            reverse('notification:bell-enable_bell'),
            data={"username":self.user_b.username, 'priority':3}
        )
        res = response.json()
        self.assertEqual(response.status_code, 200)    
            
        response = client_a.post(
            reverse('notification:bell-bell_status'),
            data={'username':self.user_b.username}
        )   
        res = response.json()
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(res['status'], 'enable')
        self.assertEqual(res['priority'], 3)
 
        ###
        response = client_a.put(
            reverse('notification:bell-change_priority'),
            data={'username':self.user_b.username, 'priority':5}
        )
        res = response.json()
        self.assertEqual(response.status_code, 200)

        response = client_a.post(
            reverse('notification:bell-bell_status'),
            data={'username':self.user_b.username}
        )   
        res = response.json()
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(res['status'], 'enable')
        self.assertEqual(res['priority'], 5)
        
        
    def test_bell_enablings(self):
        client_a = APIClient()
        client_a.force_authenticate(user=self.user_a)
        client_b = APIClient()
        client_b.force_authenticate(user=self.user_b) 
        
        response = client_a.post(
            reverse('activity:follow'),
            data={'username':self.user_b.username}
        )
        self.assertEqual(response.status_code, 200)
        
        response = client_a.post(
            reverse('notification:bell-enable_bell'),
            data={"username":self.user_b.username, 'priority':3}
        )
        res = response.json()
        self.assertEqual(response.status_code, 200)   
        
        response = client_a.get(
            reverse('notification:bell-bell_enablings')
        )
        res = response.json()
        self.assertEqual(res['count'], 1)
        self.assertEqual(res['results'][0]['username'], 'b')

            
    def test_tweet_notification_after_enable_bell(self):
        pass