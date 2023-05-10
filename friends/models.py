from django.conf import settings
from django.db import models


class FriendList(models.Model):
    # Два пользователя, добавивших друг друга в друзья
    # Порядок не поддерживается, но гарантируется,
    # что пара встречается всего один раз
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='user1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='user2')

    def __str__(self):
        return 'friendpair({0}, {1})'.format(self.user1, self.user2)


class InviteList(models.Model):
    # Отправитель и получатель запроса в друзья соответственно
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='sender')
    getter = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='getter')

    def __str__(self):
        return 'invitepair({0}, {1})'.format(self.sender, self.getter)
