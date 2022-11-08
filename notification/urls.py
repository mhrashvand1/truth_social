from django.urls import path
from rest_framework.routers import DefaultRouter
from notification.views import BellViewSet, NotificationViewSet

router = DefaultRouter()
router.register('bell', BellViewSet, basename='bell')
router.register('notifications', NotificationViewSet, basename='notification')

app_name = 'notification'
urlpatterns = [
]
urlpatterns += router.urls
