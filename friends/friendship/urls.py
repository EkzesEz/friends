from django.urls import path, include
from django.contrib.auth import views as auth_views

from .views import *

urlpatterns = [
    path('', index),
    path('inbox/', inbox),
    path('outbox/', outbox),
    path('create-request/', create_request),
    path('send-request/<str:recipient_username>/', send_friend_request),
    path('register/', register),
    path('login/', login_view),
    path('open_status_field/', open_status_field),
    path('get_status/<str:username>', get_status),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('cancel_friend_request/<int:friend_request_id>/', cancel_friend_request, name='cancel_friend_request'),
    path('accept_friend_request/<int:friend_request_id>/', accept_friend_request, name='accept_friend_request'),
    path('reject_friend_request/<int:friend_request_id>/', reject_friend_request, name='reject_friend_request'),
    path('friends/', friend_list, name='friend_list'),

]
#
# надо создать шаблон user_profile или чем то заменить его в send_friend_request
# запросы в друзья отправляются
# надо протестить accept и reject
#