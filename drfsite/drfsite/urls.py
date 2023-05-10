from django.contrib import admin
from django.urls import path, include, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from friends.views import *
from rest_framework import routers


urlpatterns = [
    # admin & services
    path('admin/', admin.site.urls),

    # api
    path('api/v1/friendlist/', FriendsView.as_view({'get': 'retrieve'})),
    path('api/v1/friends/<int:pk>', FriendsView.as_view({'delete': 'destroy'})),

    path('api/v1/invitelist/', InvitesView.as_view({'get': 'get_invites'})),
    path('api/v1/invite/<int:pk>/', InvitesView.as_view({'post': 'invite', 'delete': 'destroy'})),
    path('api/v1/invites/<int:pk>/', InvitesView.as_view({'get': 'get_status', 'post': 'answer_invitation'})),

    # auth
    path('api/v1/drf-auth/', include('rest_framework.urls')),  # Авторизация по сессии.
    path('api/v1/auth/', include('djoser.urls')),  # Авторизация по токену.
    re_path(r'^auth/', include('djoser.urls.authtoken')),  # Авторизация по токену.

    # docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
]
