# searchapp/urls.py
from django.urls import path
from . import views

app_name = 'searchapp'

urlpatterns = [
    path('', views.search_view, name='search'),
    path('suggest/', views.search_suggest, name='suggest'),
]