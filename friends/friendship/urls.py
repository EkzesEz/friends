from django.urls import path, include

from .views import *

urlpatterns = [
    path('', index),
    path('inbox/', inbox),
    path('outbox/', outbox),
    path('create-request/', create_request),
    path('send-request/<str:recipient_username>/', send_friend_request),
    path('register/', register),
    path('login/', login_view),
]
#
# надо создать шаблон user_profile или чем то заменить его в send_friend_request
# запросы в друзья отправляются
# надо протестить accept и reject
#