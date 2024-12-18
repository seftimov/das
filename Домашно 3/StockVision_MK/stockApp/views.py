from django.contrib.auth.models import User
from django.shortcuts import render, redirect, HttpResponse
from .forms import SignupUserForm
from .models import Symbols, StockData
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm

# Create your views here.


def home(request):
    symbols = Symbols.objects.all()
    context = {'symbols': symbols}
    return render(request, 'home.html', context)


def stock_detail(request, symbol):
    symbol_obj = Symbols.objects.get(symbol=symbol)
    stock_data = StockData.objects.filter(issuer_code=symbol)
    context = {'symbol_obj': symbol_obj,
               'stock_data': stock_data}
    return render(request, 'stock_detail.html', context)


def login_user(request):
    if request.method == 'POST':
        email = request.POST["email"]
        password = request.POST["password"]

        try:
            user = User.objects.get(email=email)
            username = user.username
            user = authenticate(request, username=username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password. Please try again.")
            return redirect('login')
    else:
        return render(request, 'authenticate/login.html', {})


def logout_user(request):
    logout(request)
    return redirect('login')


def signup_user(request):
    if request.method == 'POST':
        form = SignupUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = SignupUserForm()
    return render(request, 'authenticate/signup.html', {'form': form})


def analytics(request):
    return render(request, 'analytics.html')
