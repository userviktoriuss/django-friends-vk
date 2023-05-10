from rest_framework import serializers

from .models import FriendList, InviteList


class FriendsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendList
        fields = ('user1', 'user2')

class InvitesSerializer(serializers.ModelSerializer):
    class Meta:
        model = InviteList
        fields = ('sender', 'getter')
