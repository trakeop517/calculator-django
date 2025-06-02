from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Prefetch, Sum
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import (
    CreditOffer, Article, Review, Poll,
    FavoriteOffer, BudgetItem, CalculationHistory
)
from .forms import (
    RegisterForm, LoginForm, ReviewForm,
    PollForm, BudgetItemForm
)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def dashboard_view(request):
    return render(request, 'core/dashboard.html')
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form, 'user': request.user})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form, 'user': request.user})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

def home(request):
    top_offers = CreditOffer.objects.order_by('rate')[:5]
    latest_articles = Article.objects.order_by('-published_at')[:5]
    latest_reviews = Review.objects.order_by('-created_at')[:3]
    poll = Poll.objects.prefetch_related('options').last()

    result = None
    review_form = ReviewForm()
    poll_form = PollForm(poll=poll) if poll else None

    if request.method == 'POST':
        if 'amount' in request.POST:
            try:
                amount = float(request.POST.get('amount'))
                term = int(request.POST.get('term'))
                rate = float(request.POST.get('rate'))
                monthly_rate = rate / 12 / 100
                monthly_payment = (amount * monthly_rate) / (1 - (1 + monthly_rate) ** -term)
                result = {'monthly_payment': round(monthly_payment, 2)}
            except (ValueError, ZeroDivisionError):
                result = {'monthly_payment': "Ошибка в данных"}

        elif 'choice' in request.POST and poll:
            poll_form = PollForm(request.POST, poll=poll)
            if poll_form.is_valid():
                option = poll_form.cleaned_data['choice']
                option.votes += 1
                option.save()
                return redirect('home')

        elif 'text' in request.POST:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                if request.user.is_authenticated:
                    review.user = request.user
                review.save()

    return render(request, 'core/index.html', {
        'top_offers': top_offers,
        'latest_articles': latest_articles,
        'latest_reviews': latest_reviews,
        'poll': poll,
        'poll_form': poll_form,
        'result': result,
        'review_form': review_form,
        'user': request.user
    })

def all_offers(request):
    offers = CreditOffer.objects.all()
    return render(request, 'core/all_offers.html', {'offers': offers, 'user': request.user})

def search_offers(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = CreditOffer.objects.filter(bank__name__icontains=query)
    return render(request, 'core/search_results.html', {'results': results, 'user': request.user})

def articles(request):
    articles = Article.objects.all().order_by('-published_at')
    return render(request, 'core/articles.html', {'articles': articles, 'user': request.user})

def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    return render(request, 'core/article_detail.html', {'article': article, 'user': request.user})

def poll_view(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    if request.method == 'POST':
        form = PollForm(request.POST, poll=poll)
        if form.is_valid():
            choice = form.cleaned_data['choice']
            choice.votes += 1
            choice.save()
            return redirect('poll_result', poll_id=poll.id)
    else:
        form = PollForm(poll=poll)

    return render(request, 'core/poll.html', {'poll': poll, 'form': form, 'user': request.user})

@login_required
def profile_view(request):
    return render(request, 'core/profile.html', {'user': request.user})

@login_required
def add_to_favorites(request, offer_id):
    offer = get_object_or_404(CreditOffer, id=offer_id)
    favorite, created = FavoriteOffer.objects.get_or_create(
        user=request.user,
        offer=offer
    )
    if not created:
        favorite.delete()
    return redirect('offer_detail', offer_id=offer.id)

@login_required
def calculation_history(request):
    history = CalculationHistory.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/history.html', {'history': history, 'user': request.user})

@login_required
def budget(request):
    if request.method == 'POST':
        form = BudgetItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            return redirect('budget')
    
    items = BudgetItem.objects.filter(user=request.user).order_by('-date')
    form = BudgetItemForm()
    
    income = items.filter(item_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expenses = items.filter(item_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = income - expenses
    
    return render(request, 'core/budget.html', {
        'form': form,
        'items': items,
        'income': income,
        'expenses': expenses,
        'balance': balance,
        'user': request.user
    })

@login_required
def toggle_favorite(request, offer_id):
    offer = get_object_or_404(CreditOffer, id=offer_id)
    favorite, created = FavoriteOffer.objects.get_or_create(
        user=request.user,
        offer=offer
    )
    if not created:
        favorite.delete()
    return redirect('offer_detail', offer_id=offer.id)

@login_required
def favorites(request):
    favorites = FavoriteOffer.objects.filter(user=request.user).select_related('offer')
    return render(request, 'core/favorites.html', {'favorites': favorites, 'user': request.user})

def offer_detail(request, offer_id):
    offer = get_object_or_404(CreditOffer, id=offer_id)
    
    context = {
        'offer': offer,
        'reviews': Review.objects.filter(offer=offer).order_by('-created_at'),
        'user': request.user,  
    }
    
    if request.user.is_authenticated:
        context['is_favorite'] = FavoriteOffer.objects.filter(
            user=request.user,
            offer=offer
        ).exists()
    
    return render(request, 'core/offer_detail.html', context)

def auth_test(request):
    return render(request, 'core/auth_test.html', {
        'user': request.user,
        'session': request.session
    })

def test_static(request):
    return render(request, 'test_static.html')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import BudgetItem, FavoriteOffer, CalculationHistory, ActionLog, Poll

from django.db.models import Sum

@login_required
def dashboard_view(request):
    # Доходы и расходы
    # Получаем все записи для подсчётов
    all_budget_items = BudgetItem.objects.filter(user=request.user)

    # Берём последние 5 для отображения на странице
    budget_items = all_budget_items.order_by('-date')[:5]

    # Подсчёт доходов и расходов по всем записям
    income_total = all_budget_items.filter(item_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expense_total = all_budget_items.filter(item_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0


    # Избранные предложения
    favorites = FavoriteOffer.objects.filter(user=request.user).select_related('offer__bank', 'offer__credit_type')

    # История расчетов
    calculations = CalculationHistory.objects.filter(user=request.user).order_by('-created_at')[:5]

    # Последние действия
    actions = ActionLog.objects.filter(user=request.user).order_by('-timestamp')[:5]

    # Активный опрос
    active_poll = Poll.objects.order_by('-created_at').first()
    poll_options = active_poll.options.all() if active_poll else None

    context = {
        'budget_items': budget_items,
        'income_total': income_total,
        'expense_total': expense_total,
        'favorites': favorites,
        'calculations': calculations,
        'actions': actions,
        'active_poll': active_poll,
        'poll_options': poll_options,
    }

    return render(request, 'core/dashboard.html', context)

from django.shortcuts import get_object_or_404, redirect
from .models import PollOption
from django.contrib import messages

def vote_poll(request, poll_id):
    if request.method == 'POST':
        selected_option = request.POST.get('choice')
        if selected_option:
            option = get_object_or_404(PollOption, id=selected_option)
            option.votes += 1
            option.save()
            messages.success(request, 'Ваш голос учтён!')
        return redirect('dashboard')
    return redirect('dashboard')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import BudgetItem
from .forms import BudgetItemForm

@login_required
def budget_add(request):
    if request.method == 'POST':
        form = BudgetItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            return redirect('dashboard')
    else:
        form = BudgetItemForm()
    return render(request, 'core/budget_form.html', {'form': form})

@login_required
def budget_edit(request, pk):
    item = get_object_or_404(BudgetItem, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BudgetItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = BudgetItemForm(instance=item)
    return render(request, 'core/budget_form.html', {'form': form})

@login_required
def budget_delete(request, pk):
    item = get_object_or_404(BudgetItem, pk=pk, user=request.user)
    if request.method == 'POST':
        item.delete()
        return redirect('dashboard')
    return render(request, 'core/budget_confirm_delete.html', {'item': item})