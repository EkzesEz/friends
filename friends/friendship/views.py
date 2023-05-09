from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import FriendRequest
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import HttpResponse

def index(request): # Главная страница
    return render(request, 'friendship/base.html')

@login_required
def outbox(request): # Исходящие запросы в друзья
    sent_requests = FriendRequest.objects.filter(from_user=request.user, accepted=0)

    return render(request, 'friendship/sent_friend_requests.html', {'sent_requests': sent_requests})

@login_required
def inbox(request):
    # получаем все заявки в друзья,полученные текущим пользователем
    friend_requests_received = FriendRequest.objects.filter(to_user=request.user, accepted=0)

    return render(request, 'friendship/received_friend_requests.html', {'incoming_requests': friend_requests_received})

@login_required
def cancel_friend_request(request, friend_request_id): # Отмена запроса
    friend_request = get_object_or_404(FriendRequest, id=friend_request_id)

    # проверяем, является ли пользователь отправителем запроса
    if friend_request.from_user != request.user:
        return redirect('friendship/outbox')

    friend_request.delete()

    return redirect('/friendship/outbox')

@login_required
def open_status_field(request): # Создание формы для получения статуса
    if request.method == 'POST':
        user_to_check = request.POST.get("username")
        print(request)
        return redirect(f'/friendship/get_status/{user_to_check}')
    else:
        return render(request, 'friendship/status_field.html')

@login_required
def get_status(request, username):
    # Находим пользователя по имени пользователя
    user_to_ckeck = get_object_or_404(User, username=username)

    # Получаем статус дружбы между текущим пользователем и профилем пользователя
    friendship_status = _get_friendship_status(request.user, user_to_ckeck)

    context = {
        'status': friendship_status,
        'checked_user': user_to_ckeck,
    }

    return render(request, 'friendship/status.html', context)

def register(request): # Регистрация нового пользователя
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/friendship/login')
        else:
            print(form.errors)
    else:
        form = UserCreationForm()
    return render(request, 'friendship/registration.html', {'form': form})

def login_view(request): # Авторизация пользователя
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/friendship')
    else:
        form = AuthenticationForm()
    return render(request, 'friendship/login.html', {'form': form})

@login_required
def create_request(request): # Создание формы для запроса в друзья
    if request.method == 'POST':
        recipient_username = request.POST.get("recipient_username")
        print(request)
        return redirect(f'/friendship/send-request/{recipient_username}')
    else:
        return render(request, 'friendship/request_creation.html')

@login_required
def send_friend_request(request, recipient_username): # Создание запроса в друзья
    recipient = get_object_or_404(User, username=recipient_username)

    # проверяем, существует ли уже запрос на дружбу между пользователями
    if FriendRequest.objects.filter(from_user=request.user, to_user=recipient).exists():
        messages.error(request, 'A friend request has already been sent to this user.')
        return redirect('/friendship/outbox')
    
    if FriendRequest.objects.filter(from_user=recipient, to_user=request.user).exists():
        received_request = FriendRequest.objects.get(from_user=recipient, to_user=request.user)
        received_request.accepted = True
        received_request.save()
        return redirect('/friendship/friends')

    # создаем объект FriendRequest и сохраняем его в базе данных
    friend_request = FriendRequest(from_user=request.user, to_user=recipient)
    friend_request.save()
    messages.success(request, 'Friend request sent.')
    return redirect('/friendship/outbox')

@login_required
def accept_friend_request(request, friend_request_id):
    friend_request = get_object_or_404(FriendRequest, id=friend_request_id)

    # проверяем, является ли пользователь получателем запроса
    if friend_request.to_user != request.user:
        return redirect('/friendship/inbox')

    # соглашаемся на дружбу
    friend_request.accepted = True
    friend_request.save()

    return redirect('/friendship/inbox')

@login_required
def reject_friend_request(request, friend_request_id):
    friend_request = get_object_or_404(FriendRequest, id=friend_request_id)

    # проверяем, является ли пользователь получателем запроса
    if friend_request.to_user != request.user:
        return redirect('/friendship/inbox')

    friend_request.delete()

    return redirect('/friendship/inbox')

def friend_list(request):
    # Находим всех друзей пользователя
    friends = FriendRequest.objects.filter(from_user=request.user, accepted=True) | FriendRequest.objects.filter(to_user=request.user, accepted=True)

    context = {
        'friends': friends
    }
    return render(request, 'friendship/friend_list.html', context)

def _get_friendship_status(current_user, other_user):
    """Проверяет статус дружбы между двумя пользователями"""
    friend_request_sent = FriendRequest.objects.filter(
        from_user=current_user,
        to_user=other_user
    ).exists()
    
    friend_request_received = FriendRequest.objects.filter(
        from_user=other_user,
        to_user=current_user
    ).exists()


    
    if friend_request_sent and friend_request_received:
        friendship_status = 'Друзья'
    elif friend_request_sent:
        friendship_status = 'Заявка отправлена'
    elif friend_request_received:
        friendship_status = 'Заявка получена'
    else:
        friendship_status = 'Не друзья'
    
    return friendship_status