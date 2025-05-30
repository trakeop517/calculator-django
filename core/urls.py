# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  
    path('offers/', views.all_offers, name='all_offers'),
    path('search/', views.search_offers, name='search_offers'),
    path('articles/', views.articles, name='articles'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
]
