from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from .models import FriendList, InviteList


#class UsersSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Users
#        fields = ('id', 'username')

class FriendsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendList
        fields = ('user1', 'user2')

class InvitesSerializer(serializers.ModelSerializer):
    class Meta:
        model = InviteList
        fields = ('sender', 'getter')
