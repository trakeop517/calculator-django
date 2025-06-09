# core/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views 
from django.contrib.auth import views as auth_views
from .views import budget, add_to_favorites, calculation_history, dashboard_view, vote_poll,dashboard_view, budget_add, budget_edit, budget_delete, delete_review
from .views import profile_view, edit_review, add_review

urlpatterns = [
    path('', views.home, name='index'),
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
    path('ajax/calculate/', views.calculate_credit_ajax, name='calculate_credit_ajax'),
    path('history/', views.calculation_history, name='calculation_history'),
    path('offer/<int:offer_id>/favorite/', views.add_to_favorites, name='add_to_favorites'),
    path('offer/<int:offer_id>/favorite/toggle/', views.add_to_favorites, name='toggle_favorite'),
    path('favorites/', views.favorites, name='favorites'),
    path('offer/<int:offer_id>/review/add/', views.add_review, name='add_review'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('review/update/<int:review_id>/', views.update_review, name='update_review'),
    path('history/', views.calculation_history, name='calculation_history'),
    path('repeat-calculation/<int:calc_id>/', views.repeat_calculation, name='repeat_calculation'),
    path('favorites/', views.favorites, name='favorites'),
    path('favorites/toggle/<int:offer_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('compare/', views.compare_offers, name='compare'),
    path('compare/<int:offer1_id>/<int:offer2_id>/', views.compare_detail, name='compare_detail'),
    path('save-calculation/', views.save_calculation, name='save_calculation'),
    path('compare/', views.compare_offers, name='compare_offers'),
    path('compare/<int:offer1_id>/<int:offer2_id>/', views.compare_detail, name='compare_detail'),

]


