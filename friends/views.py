from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import *


@extend_schema(tags=["FriendsView"])
@extend_schema_view(
    retrieve=extend_schema(
        summary="Возвращает список друзей текущего пользователя",
    ),
    destroy=extend_schema(
        summary="Удаляет пользователя из друзей.",
    )
)
class FriendsView(viewsets.ModelViewSet):
    queryset = FriendList.objects.all()
    serializer_class = FriendsSerializer
    permission_classes = [IsAuthenticated]

    # Возвращает список друзей текущего пользователя.
    def retrieve(self, request, *args, **kwargs):
        # TODO: убрать себя из вывода (два сериалайзера, тупая лямбда, ...)
        fr1 = FriendList.objects.filter(user1=request.user)
        fr2 = FriendList.objects.filter(user2=request.user)
        fr1 = fr1.union(fr2)

        return Response({'friends': FriendsSerializer(fr1, many=True).data})

    # Удаляет пользователя из друзей.
    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        sender = request.user
        if not pk:  # Неправильный запрос
            return Response({'error': 'Method DELETE is not allowed.'})

        try:  # Пользователь не существует
            getter = User.objects.get(pk=pk)
        except Exception:
            return Response({'error': 'Object does not exist.'})

        if not self.are_friends(sender, getter):
            return Response({'error': f'User {getter} is not in your friend list.'})

        # Удаляет пару (sender, getter) или (getter, sender)
        if FriendList.objects.filter(
                user1=sender,
                user2=getter).all().count() != 0:
            FriendList.objects.get(
                user1=sender,
                user2=getter).delete()
        else:
            FriendList.objects.get(
                user1=getter,
                user2=sender).delete()

        return Response({'info': f'User {getter} removed from your friends.'})

    # Проверяет, что два пользователя друзья.
    @classmethod
    def are_friends(cls, sender, getter):
        fr1 = FriendList.objects.filter(user1=sender, user2=getter)
        fr2 = FriendList.objects.filter(user1=getter, user2=sender)
        fr = fr1.union(fr2)

        return fr.count() != 0

    # Делает пользователей друзьями.
    @classmethod
    def make_friends(cls, sender, getter):
        FriendList.objects.create(
            user1=sender,
            user2=getter
        )


@extend_schema(tags=["InvitesView"])
@extend_schema_view(
    list=extend_schema(
        summary="Получает все входящие и исходящие запросы дружбы.",
        parameters=[
            OpenApiParameter(
                name='is_in',
                location=OpenApiParameter.QUERY,
                type=str,
                default='true'
            )
        ]
    ),
    partial_update=extend_schema(
        summary="Отправляет пользователю запрос дружбы.",
        request=None,
    ),
    destroy=extend_schema(
        summary="Отменяет запрос дружбы.",
    ),

    update=extend_schema(
        summary="Позволяет отклонить/принять заявку в друзья.",
        examples=[
                OpenApiExample(
                    "Acceptation example",
                    description="Test example for the answer_invitation.",
                    value={
                        "action": "accept"
                    },
                    status_codes=[str(status.HTTP_200_OK)],
                ),
            ],
    ),
    retrieve=extend_schema(
        summary="Возвращает статус дружбы - друзья, ожидает заявка, ничего."
    )
)
class InvitesView(viewsets.ModelViewSet):
    queryset = InviteList.objects.all()
    serializer_class = InvitesSerializer
    permission_classes = [IsAuthenticated]
    ACCEPT = 'accept'  # Константы для принятия и отказа от запроса дружбы
    DENY = 'deny'

    # Получает все входящие и исходящие запросы дружбы.
    def list(self, request, *args, **kwargs):
        # Если запрашиваются входящие, будет равен "true" (default тоже "true")
        is_in = request.GET.get('is_in', 'true')
        resp = dict()
        if is_in == "true":
            fr = InviteList.objects.filter(getter=request.user)
            resp['invites_in'] = InvitesSerializer(fr, many=True).data
        else:
            fr = InviteList.objects.filter(sender=request.user)
            resp['invites_out'] = InvitesSerializer(fr, many=True).data
        return Response(resp)

    # Отправляет пользователю запрос дружбы.
    def partial_update(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        sender = request.user
        if not pk:  # Неправильный запрос
            return Response({'error': 'Method POST is not allowed.'})

        try:  # Пользователь не существует
            getter = User.objects.get(pk=pk)
        except Exception:
            return Response({'error': 'Object does not exist.'})

        if sender.id == pk:  # Была отправлена заявка самому себе
            return Response({'error': 'Can\'t invite yourself.'})

        if FriendsView.are_friends(sender, getter):  # Уже есть заявка в друзья.
            return Response({'error': f'User {getter} is already your friend.'})

        # Уже есть такой же запрос.
        if InviteList.objects.filter(
                sender=sender,
                getter=getter).all().count() != 0:
            return Response({'error': 'You have already sent an invite to this user.'})

        # Уже есть входящее приглашение.
        if InviteList.objects.filter(
                sender=getter,
                getter=sender).all().count() != 0:
            InviteList.objects.get(
                sender=getter,
                getter=sender).delete()
            FriendsView.make_friends(sender, getter)
            return Response({'info': f'Friend {getter} added'})

        # Создадим заявку в друзья.
        instance = InviteList.objects.create(
            sender=sender,
            getter=getter
        )
        return Response({'post': InvitesSerializer(instance).data})

    # Отменяет запрос дружбы.
    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        sender = request.user
        if not pk:  # Неправильный запрос
            return Response({'error': 'Method DELETE is not allowed.'})

        try:  # Пользователь не существует
            getter = User.objects.get(pk=pk)
        except Exception:
            return Response({'error': 'Object does not exist.'})

        # Приглашение не существует.
        if InviteList.objects.filter(
                sender=sender,
                getter=getter).all().count() == 0:
            return Response({'error': f'Invitation to {getter} doesn\'t exist.'})

        InviteList.objects.get(
            sender=sender,
            getter=getter).delete()
        return Response({'info': f'Invitation to {getter} deleted successfully.'})

    # Позволяет отклонить/принять заявку в друзья.
    def update(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        this = request.user
        if not pk:  # Неправильный запрос
            return Response({'error': 'Method GET is not allowed.'})

        try:  # Пользователь не существует
            other = User.objects.get(pk=pk)
        except Exception:
            return Response({'error': 'Object does not exist.'})

        # Нет входящего запроса
        if InviteList.objects.filter(
                sender=other,
                getter=this).all().count() == 0:
            return Response({'error': f'No incoming invitation from {other}'})

        try:  # Узнаём, отклонил или принял запрос пользователь
            action = request.data['action']
        except Exception:
            return Response({'error': 'Query must contain \'action\' field'})

        if action not in [self.ACCEPT, self.DENY]:
            return Response({'error': f'\'action\' field must be {self.ACCEPT} or {self.DENY}.'})

        if action == self.ACCEPT:
            FriendsView.make_friends(this, other)
            out_message = f'Added {other} to your friend list.'
        else:
            out_message = f'Denied {other}\'s invitation.'

        invitation = InviteList.objects.get(sender=other, getter=this)
        invitation.delete()
        return Response({'info': out_message})

    # Возвращает статус дружбы - друзья, ожидает заявка, ничего.
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        sender = request.user
        if not pk:  # Неправильный запрос
            return Response({'error': 'Method POST is not allowed.'})

        try:  # Пользователь не существует
            getter = User.objects.get(pk=pk)
        except Exception:
            return Response({'error': 'Object does not exist.'})

        # Пользователи друзья
        if FriendsView.are_friends(sender, getter):
            return Response({'friend_status': 'friend'})

        # Ищем исходящий запросы дружбы
        if InviteList.objects.filter(
                sender=sender,
                getter=getter).all().count() != 0:
            return Response({'friend_status': 'outcoming invitation'})

        # Ищем входящий запрос дружбы
        if InviteList.objects.filter(
                sender=getter,
                getter=sender).all().count() != 0:
            return Response({'friend_status': 'incoming invitation'})

        return Response({'friend_status': 'none'})
