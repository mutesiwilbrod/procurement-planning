from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user, logout
from django.contrib import messages


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect("plan:index")
        else:
            messages.warning(request, f"User {username} doesn't exist!")
            return redirect("plan:login")
    else:
        if get_user(request).is_authenticated:
            return redirect('plan:index')
        testing = True
        context = {"testing": testing}
        return render(request, 'global/login.html', context)


def index(request):
    if get_user(request).is_authenticated:
        return redirect("plan:plan")
    else:
        return redirect('plan:login')


def logout_view(request):
    logout(request)
    return redirect('plan:login')
