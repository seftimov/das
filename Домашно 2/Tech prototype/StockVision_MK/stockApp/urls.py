from django.urls import path
from . import views


urlpatterns = [
    path('home/', views.home, name='home'),
    path('stock/<str:symbol>/', views.stock_detail, name='stock_detail'),
    path('', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('analytics', views.analytics, name='analytics'),
]
