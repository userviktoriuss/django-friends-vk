from django.forms import model_to_dict
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render
from .models import FriendList, InviteList
from .serializers import *
from django.contrib.auth.models import User


# Create your views here.
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


    def retrieve(self, request, *args, **kwargs):
        # TODO: убрать себя из вывода (два сериалайзера, тупая лямбда, ...)
        fr1 = FriendList.objects.filter(user1=request.user)
        fr2 = FriendList.objects.filter(user2=request.user)
        fr1 = fr1.union(fr2)

        return Response({'friends': FriendsSerializer(fr1, many=True).data})

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        sender = request.user
        if not pk:  # Неправильный запрос
            return Response({'error': 'Method DELETE is not allowed.'})

        try:  # Пользователь не существует
            getter = User.objects.get(pk=pk)
        except:
            return Response({'error': 'Object does not exist.'})


        if not self.are_friends(sender, getter):
            return Response({'error': f'User {getter} is not in your friend list.'})

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

    @classmethod
    def are_friends(cls, sender, getter):
        # TODO: проверить на работоспособность
        fr1 = FriendList.objects.filter(user1=sender, user2=getter)
        fr2 = FriendList.objects.filter(user1=getter, user2=sender)
        fr = fr1.union(fr2)

        return fr.count() != 0

    @classmethod
    def make_friends(cls, sender, getter):
        FriendList.objects.create(
            user1 = sender,
            user2 = getter
        )

@extend_schema(tags=["InvitesView"])
@extend_schema_view(
    # get_invites=extend_schema(
    #     summary="Получает все входящие и исходящие запросы дружбы.",
    #     #TODO: Нормальный пример и описание мува с ?is_in
    # ),
    # invite=extend_schema(
    #     summary="Отправляет пользователю запрос дружбы.",
    # ),
    destroy=extend_schema(
        summary="Отменяет запрос дружбы.",
    ),

    # answer_invitation=extend_schema(
    #     summary="Позволяет отклонить/принять заявку в друзья.",
    #     examples=[
    #             OpenApiExample(
    #                 "Acception example",
    #                 description="Test example for the answer_invitation.",
    #                 value=
    #                 {
    #                     "action": "accept"
    #                 },
    #                 status_codes=[str(status.HTTP_200_OK)],
    #             ),
    #         ],
    # ),
    # get_status=extend_schema(
    #     summary="Возвращает статус дружбы - друзья, ожидает заявка, ничего."
    # )
)
class InvitesView(viewsets.ModelViewSet):
    queryset = InviteList.objects.all()
    serializer_class = InvitesSerializer
    permission_classes = [IsAuthenticated]
    ACCEPT = 'accept'
    DENY = 'deny'

    def get_invites(self, request, *args, **kwargs):
        is_in = request.GET.get('is_in', 'true')
        resp = dict()
        if is_in == "true":
            fr = InviteList.objects.filter(getter=request.user)
            resp['invites_in'] = InvitesSerializer(fr, many=True).data
        else:
            fr = InviteList.objects.filter(sender=request.user)
            resp['invites_out'] = InvitesSerializer(fr, many=True).data
        return Response(resp)

    def invite(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        sender = request.user
        if not pk:  # Неправильный запрос
            return Response({'error': 'Method POST is not allowed.'})

        try:  # Пользователь не существует
            getter=User.objects.get(pk=pk)
        except:
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

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        sender = request.user
        if not pk:  # Неправильный запрос
            return Response({'error': 'Method DELETE is not allowed.'})

        try:  # Пользователь не существует
            getter = User.objects.get(pk=pk)
        except:
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

    def answer_invitation(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        this = request.user
        if not pk:  # Неправильный запрос
            return Response({'error': 'Method GET is not allowed.'})

        try:  # Пользователь не существует
            other = User.objects.get(pk=pk)
        except:
            return Response({'error': 'Object does not exist.'})

        if InviteList.objects.filter(
                sender=other,
                getter=this).all().count() == 0:
            return Response({'error': f'No incoming invitation from {other}'})

        try:
            action = request.data['action']
        except:
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

    def get_status(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        sender = request.user
        if not pk:  # Неправильный запрос
            return Response({'error': 'Method POST is not allowed.'})

        try:  # Пользователь не существует
            getter = User.objects.get(pk=pk)
        except:
            return Response({'error': 'Object does not exist.'})

        if FriendsView.are_friends(sender, getter):
            return Response({'friend_status': 'friend'})

        if InviteList.objects.filter(
                sender=sender,
                getter=getter).all().count() != 0:
            return Response({'friend_status': 'outcoming invitation'})

        if InviteList.objects.filter(
                sender=getter,
                getter=sender).all().count() != 0:
            return Response({'friend_status': 'incoming invitation'})

        return Response({'friend_status': 'none'})