from django.shortcuts import render, HttpResponse
from .models import Symbols, StockData

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


def login(request):
    return render(request, 'login.html')


def signup(request):
    return render(request, 'signup.html')


def analytics(request):
    return render(request, 'analytics.html')
