# core/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views 
from django.contrib.auth import views as auth_views
from .views import budget, add_to_favorites, calculation_history, dashboard_view, vote_poll,dashboard_view, budget_add, budget_edit, budget_delete
from .views import profile_view

urlpatterns = [
    path('', views.home, name='home'),  
    path('offers/', views.all_offers, name='all_offers'),
    path('search/', views.search_offers, name='search_offers'),
    path('articles/', views.articles, name='articles'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('budget/', budget, name='budget'),
    path('offers/<int:offer_id>/favorite/', add_to_favorites, name='add_favorite'),
    path('history/', calculation_history, name='history'),
    path('profile/', profile_view, name='profile'),
    path('offers/<int:offer_id>/', views.offer_detail, name='offer_detail'),
    path('auth-test/', views.auth_test, name='auth_test'),
    path('test-static/', views.test_static, name='test-static'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('poll/<int:poll_id>/vote/', vote_poll, name='vote_poll'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('budget/add/', budget_add, name='budget_add'),
    path('budget/edit/<int:pk>/', budget_edit, name='budget_edit'),
    path('budget/delete/<int:pk>/', budget_delete, name='budget_delete'),
]

