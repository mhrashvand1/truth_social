from django.urls import path
from rest_framework.routers import DefaultRouter
from activity.views import (
    FollowViewSet, 
    BlockViewSet,
)

block_router = DefaultRouter()
block_router.register('block', BlockViewSet, basename='block')

app_name = 'activity'
urlpatterns = [
    
    path(
        'follow/follow/', 
        FollowViewSet.as_view({'post':'follow'}),
        name='follow'
    ),    
    path(
        'follow/unfollow/',
        FollowViewSet.as_view({'post':'unfollow'}),
        name='unfollow'
    ),
    path(
        'follow/users/<str:username>/followers/', 
        FollowViewSet.as_view({"get":"followers"}),
        name='user-followers'
    ),
    path(
        'follow/users/<str:username>/followings/', 
        FollowViewSet.as_view({"get":"followings"}),
        name='user-followings'
    ),
]
urlpatterns += block_router.urls