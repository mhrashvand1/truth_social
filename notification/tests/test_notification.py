from notification.tests.base_test import BaseTest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from activity.models import Follow
from account.models import User


class TestNotification(BaseTest):
        
    def test_follow_notification(self):
        client_a = APIClient()
        client_a.force_authenticate(user=self.user_a)
        client_b = APIClient()
        client_b.force_authenticate(user=self.user_b)    
        
        response = client_a.post(
            reverse('activity:follow'),
            data={"username":self.user_b.username},
            format='json'
        )
        res = response.json()
        self.assertEqual(response.status_code, 200),
        
        
        response = client_b.get(
            reverse('notification:notification-list')
        )
        res = response.json()
        notif = res['results'][0]
        
        self.assertEqual(notif['to'], self.user_b.username)
        self.assertEqual(notif['has_read'], False)
        self.assertEqual(notif['notif_type'], 'follow')
        self.assertEqual(notif['message']['actor']['name'], 'a')
        

        response = client_b.get(
            reverse('notification:notification-detail', kwargs={"pk":notif['id']})
        )
        res = response.json()
        self.assertEqual(res['has_read'], True)