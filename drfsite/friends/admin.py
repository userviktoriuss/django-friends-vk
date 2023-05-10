from django.contrib import admin
from .models import FriendList, InviteList

# Register your models here.
# admin.site.register(Users)
admin.site.register(FriendList)
admin.site.register(InviteList)
