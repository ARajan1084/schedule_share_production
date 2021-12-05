"""schedule_share URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from student import views

urlpatterns = [
    path('login/', views.login, name="login"),
    path('account/create/', views.create_account, name='create_account'),
    path('class/management/add/', views.add_class, name='add_class'),
    path('class/management/remove/', views.remove_class, name='remove_class'),
    path('class/management/removeclass/<str:klass_id>/', views.remove_a_class, name='remove_a_class'),
    path('', views.home, name='home')
]
