from datetime import date
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .forms import SignupUserForm, StockFilterForm
from .models import Symbols, StockData
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm

# Create your views here.


def home(request):
    query = request.GET.get('searched', '')
    if query:
        symbols = Symbols.objects.filter(symbol__icontains=query)
    else:
        symbols = Symbols.objects.all()

    context = {
        'symbols': symbols,
        'query': query
    }
    return render(request, 'home.html', context)


def convert_currency(value, from_currency, to_currency):
    if value is None:
        return "N/A"

    conversion_rates = {
        'MKD': {'USD': 0.017, 'EUR': 0.016, 'MKD': 1.0},
    }

    currency_symbols = {
        'USD': ('$ ', 'before'),
        'EUR': ('€ ', 'before'),
        'MKD': (' ден.', 'after'),
    }

    converted_value = value * conversion_rates[from_currency][to_currency]
    symbol, position = currency_symbols[to_currency]

    formatted_value = f"{converted_value:,.2f}"

    if position == 'before':
        return f"{symbol}{formatted_value}"
    else:
        return f"{formatted_value}{symbol}"


def stock_detail(request, symbol):
    symbol_obj = get_object_or_404(Symbols, symbol=symbol)
    stock_data = StockData.objects.filter(issuer_code=symbol)
    selected_currency = 'MKD'

    if request.method == 'POST':
        form = StockFilterForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            selected_currency = form.cleaned_data.get('currency', 'MKD') or 'MKD'

            if start_date and end_date:
                stock_data = stock_data.filter(date__range=[start_date, end_date])
            elif start_date:
                stock_data = stock_data.filter(date__gte=start_date)
            elif end_date:
                stock_data = stock_data.filter(date__lte=end_date)
    else:
        current_year = 2024
        start_date = date(current_year, 1, 1)
        end_date = date(current_year, 12, 31)
        stock_data = stock_data.filter(date__range=[start_date, end_date])
        form = StockFilterForm()

    valid_currencies = {'USD', 'EUR', 'MKD'}
    if selected_currency not in valid_currencies:
        selected_currency = 'MKD'

    for stock in stock_data:
        stock.last_trade_price = convert_currency(stock.last_trade_price, 'MKD', selected_currency)
        stock.max_price = convert_currency(stock.max_price, 'MKD', selected_currency)
        stock.min_price = convert_currency(stock.min_price, 'MKD', selected_currency)
        stock.avg_price = convert_currency(stock.avg_price, 'MKD', selected_currency)
        stock.turnover_best = convert_currency(stock.turnover_best, 'MKD', selected_currency)
        stock.total_turnover = convert_currency(stock.total_turnover, 'MKD', selected_currency)

    context = {
        'symbol_obj': symbol_obj,
        'stock_data': stock_data,
        'form': form,
    }

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
