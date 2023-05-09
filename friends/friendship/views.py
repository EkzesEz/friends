from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import FriendRequest
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import HttpResponse

def index(request):
    return render(request, 'friendship/base.html')

def inbox(request):
    return HttpResponse("syka blyat nahui in")

def outbox(request):
    return HttpResponse("syka blyat nahui out")

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        print("1")
        if form.is_valid():
            print("2")
            form.save()
            print("3")
            return redirect('/friendship/login')
        else:
            print(form.errors)
    else:
        form = UserCreationForm()
    return render(request, 'friendship/registration.html', {'form': form})

def login_view(request):
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
def friend_requests(request):
    # получаем все заявки в друзья, отправленные или полученные текущим пользователем
    friend_requests_sent = request.user.friend_requests_sent.all()
    friend_requests_received = request.user.friend_requests_received.all()

    context = {
        'sent': friend_requests_sent,
        'received': friend_requests_received,
    }
    return render(request, 'friendship/friend_requests.html', context)

@login_required
def create_request(request):
    if request.method == 'POST':
        recipient_username = request.POST.get("recipient_username")
        print(request)
        return redirect(f'/friendship/send-request/{recipient_username}')
    else:
        return render(request, 'friendship/request_creation.html')

@login_required
def send_friend_request(request, recipient_username):
    recipient = get_object_or_404(User, username=recipient_username)

    # проверяем, существует ли уже запрос на дружбу между пользователями
    if FriendRequest.objects.filter(from_user=request.user, to_user=recipient).exists():
        messages.error(request, 'A friend request has already been sent to this user.')
        return redirect('user_profile', username=recipient_username)

    # создаем объект FriendRequest и сохраняем его в базе данных
    friend_request = FriendRequest(from_user=request.user, to_user=recipient)
    friend_request.save()
    messages.success(request, 'Friend request sent.')
    return redirect('user_profile', username=recipient_username)

@login_required
def accept_friend_request(request, pk):
    friend_request = get_object_or_404(FriendRequest, pk=pk, to_user=request.user)
    friend_request.accepted = True
    friend_request.save()
    messages.success(request, 'Friend request accepted.')
    return redirect('friend_requests')

@login_required
def reject_friend_request(request, pk):
    friend_request = get_object_or_404(FriendRequest, pk=pk, to_user=request.user)
    friend_request.delete()
    messages.success(request, 'Friend request rejected.')
    return redirect('friend_requests')