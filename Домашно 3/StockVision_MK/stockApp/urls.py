from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('home/', views.home, name='home'),
    path('stock/<str:symbol>/', views.stock_detail, name='stock_detail'),
    path('login_user/', views.login_user, name='login'),
    path('logout_user/', views.logout_user, name='logout'),
    path('signup_user/', views.signup_user, name='signup'),
    path('analytics/', views.analytics, name='analytics'),
]
