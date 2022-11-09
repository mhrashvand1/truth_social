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
    path(
        'follow/users/<str:username>/followed_by/',
        FollowViewSet.as_view({"get":"followed_by"}),
        name='user-followed_by'
    ),
    path(
        'follow/users/<str:username>/followed_you/',
        FollowViewSet.as_view({"get":"followed_you"}),
        name='user-followed_you'
    ),
    path(
        'follow/users/<str:username>/is_followed/',
        FollowViewSet.as_view({"get":"is_followed"}),
        name='user-is_followed'
    )
]
urlpatterns += block_router.urls