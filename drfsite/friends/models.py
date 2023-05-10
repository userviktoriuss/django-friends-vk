from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
#class Users(models.Model):
#    id = models.BigAutoField(primary_key=True)
#    username = models.CharField(max_length=31)
#
#    def __str__(self):
#        return '{1}(id{0})'.format(self.id, self.username)



class FriendList(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='user1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='user2')

    def __str__(self):
        return 'friendpair({0}, {1})'.format(self.user1, self.user2)


class InviteList(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='sender')
    getter = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='getter')

    def __str__(self):
        return 'invitepair({0}, {1})'.format(self.sender, self.getter)
