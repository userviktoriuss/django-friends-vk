from django.contrib import admin
from django.urls import path, include, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from friends.views import *

urlpatterns = [
    # admin
    path('admin/', admin.site.urls),

    # api
    path('api/v1/friends/', FriendsView.as_view({'get': 'retrieve'})),
    path('api/v1/friends/<int:pk>', FriendsView.as_view({'delete': 'destroy'})),

    path('api/v1/invites/', InvitesView.as_view({'get': 'list'})),
    path('api/v1/invite/<int:pk>/', InvitesView.as_view({'post': 'partial_update', 'delete': 'destroy'})),
    path('api/v1/invites/<int:pk>/', InvitesView.as_view({'get': 'retrieve', 'post': 'update'})),

    # auth
    path('api/v1/drf-auth/', include('rest_framework.urls')),
    path('api/v1/auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),

    # docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
]

