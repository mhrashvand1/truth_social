from django.urls import path, re_path, include
from account.views import TokenObtainPairView, TokenBlackListView
from rest_framework_simplejwt.views import (
TokenRefreshView, TokenVerifyView,
)

# Can be do:
# nested routers
# extend routers

app_name = 'account'
urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('create-token/', TokenObtainPairView.as_view(), name='create-token'),
    path('refresh-token/', TokenRefreshView.as_view(), name='refresh-token'),
    path('verify-token/', TokenVerifyView.as_view(), name='verify-token'),
    path('blacklist-token/', TokenBlackListView.as_view(), name='blacklist-token'),
]
