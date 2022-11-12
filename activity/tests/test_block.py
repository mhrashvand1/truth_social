from activity.tests.base_test import BaseTest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from activity.models import Follow
from account.models import User


class TestBlock(BaseTest):
    
    def test_block_unblock(self):
        # is_blocked, blocked_you
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
            reverse('activity:block-block'),
            data={'username':self.user_a.username}
        )
        res = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(res['username'][0], f'Can not block/unblock yourself.')
        
        response = client_a.post(
            reverse('activity:block-block'),
            data={'username':self.user_b.username}
        )
        self.assertEqual(response.status_code, 200)
         
        response = client_a.post(
            reverse('activity:block-block'),
            data={'username':self.user_b.username}
        )
        res = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(res['username'][0], f'User with username {self.user_b.username} has already blocked.')
    
    
        response = client_a.post(
            reverse('activity:block-is_blocked'),
            data={"username":self.user_b.username}
        )
        res = response.json()
        self.assertEqual(res['is_blocked'], True)
    
        response = client_b.post(
            reverse('activity:block-blocked_you'),
            data={"username":self.user_a.username}
        )
        res = response.json()
        self.assertEqual(res['blocked_you'], True)
    
        response = client_a.post(
            reverse('activity:block-unblock'),
            data={'username':self.user_c.username}
        )
        res = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(res['username'][0], f'User with username {self.user_c.username} is not blocked.')
    
        response = client_a.post(
            reverse('activity:block-unblock'),
            data={'username':self.user_b.username}
        )
        self.assertEqual(response.status_code, 200)
    
        response = client_a.post(
            reverse('activity:block-is_blocked'),
            data={"username":self.user_b.username}
        )
        res = response.json()
        self.assertEqual(res['is_blocked'], False)
    
        response = client_b.post(
            reverse('activity:block-blocked_you'),
            data={"username":self.user_a.username}
        )
        res = response.json()
        self.assertEqual(res['blocked_you'], False)
    
    
    def test_blockings(self):
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
            reverse('activity:block-block'),
            data={'username':self.user_b.username}
        )
        self.assertEqual(response.status_code, 200)
        
        response = client_a.post(
            reverse('activity:block-block'),
            data={'username':self.user_c.username}
        )
        self.assertEqual(response.status_code, 200)
        
        response = client_a.post(
            reverse('activity:block-block'),
            data={'username':self.user_d.username}
        )
        self.assertEqual(response.status_code, 200)  
        
        response = client_a.get(
            reverse('activity:block-blockings')
        )
        res = response.json()
        self.assertEqual(response.status_code, 200)  
        self.assertEqual(res['count'], 3)
        blockings_list = (user['username'] for user in res['results'])
        self.assertEqual('b' in blockings_list, True)
        self.assertEqual('c' in blockings_list, True)
        self.assertEqual('d' in blockings_list, True)
        self.assertEqual('e' in blockings_list, False)

    
    def test_delete_follows_after_block(self):
        client_a = APIClient()
        client_a.force_authenticate(user=self.user_a)
        client_b = APIClient()
        client_b.force_authenticate(user=self.user_b)        

        response = client_a.post(
            reverse('activity:follow'),
            data={'username':self.user_b.username}
        )
        self.assertEqual(response.status_code, 200)
        
        response = client_b.post(
            reverse('activity:follow'),
            data={'username':self.user_a.username}
        )
        self.assertEqual(response.status_code, 200)
            
        response = client_a.get(
            reverse('activity:user-is_followed', kwargs={'username':self.user_b.username})
        ).json()
        self.assertEqual(response['is_followed'], True)
        
        response = client_a.get(
            reverse('activity:user-followed_you', kwargs={'username':self.user_b.username})
        ).json()
        self.assertEqual(response['followed_you'], True)
    
        # Now user_a block user_b
        response = client_a.post(
            reverse('activity:block-block'),
            data={'username':self.user_b.username}
        )
        self.assertEqual(response.status_code, 200)
        # Then:
        response = client_a.get(
            reverse('activity:user-is_followed', kwargs={'username':self.user_b.username})
        ).json()
        self.assertEqual(response['is_followed'], False)
        
        response = client_a.get(
            reverse('activity:user-followed_you', kwargs={'username':self.user_b.username})
        ).json()
        self.assertEqual(response['followed_you'], False)
    
    
    def test_delete_bells_after_block(self):
        client_a = APIClient()
        client_a.force_authenticate(user=self.user_a)
        client_b = APIClient()
        client_b.force_authenticate(user=self.user_b)   
               
        response = client_a.post(
            reverse('activity:follow'),
            data={'username':self.user_b.username}
        )
        self.assertEqual(response.status_code, 200)
        
        response = client_b.post(
            reverse('activity:follow'),
            data={'username':self.user_a.username}
        )
        self.assertEqual(response.status_code, 200)
            
        response = client_a.post(
            reverse('notification:bell-enable_bell'),
            data={'username':self.user_b.username, 'priority':3}
        )
        res = response.json()
        self.assertEqual(response.status_code, 200)
        
        response = client_b.post(
            reverse('notification:bell-enable_bell'),
            data={'username':self.user_a.username, 'priority':3}
        )
        self.assertEqual(response.status_code, 200)
        
        response = client_a.post(
            reverse('notification:bell-bell_status'),
            data={"username":self.user_b.username}
        )
        res = response.json()
        self.assertEqual(res['status'], 'enable')
        
        response = client_b.post(
            reverse('notification:bell-bell_status'),
            data={"username":self.user_a.username}
        )
        res = response.json()
        self.assertEqual(res['status'], 'enable')

    
        # Now user_a block user_b
        response = client_a.post(
            reverse('activity:block-block'),
            data={'username':self.user_b.username}
        )
        self.assertEqual(response.status_code, 200)
        
        # Then:
        
        response = client_a.post(
            reverse('notification:bell-bell_status'),
            data={"username":self.user_b.username}
        )
        res = response.json()
        self.assertEqual(res['status'], 'disable')
        
        response = client_b.post(
            reverse('notification:bell-bell_status'),
            data={"username":self.user_a.username}
        )
        res = response.json()
        self.assertEqual(res['status'], 'disable')   