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
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

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
from django.db.models import Avg, Count
def home(request):
    top_offers = CreditOffer.objects.order_by('rate')[:5]
    latest_articles = Article.objects.order_by('-published_at')[:5]
    latest_reviews = Review.objects.order_by('-created_at')[:3]
    poll = Poll.objects.prefetch_related('options').last()

    result = None
    review_form = ReviewForm()
    poll_form = PollForm(poll=poll) if poll else None
    avg_top_rate = top_offers.aggregate(avg_rate=Avg('rate'))['avg_rate'] or 0
    total_articles = Article.objects.count()
    editing_review_id = None
    if 'edit_review' in request.GET:
        editing_review_id = request.GET['edit_review']
    if request.method == 'POST':
        if 'review_id' in request.POST:
            review_id = request.POST['review_id']
            try:
                review = Review.objects.get(id=review_id, user=request.user)
                review.text = request.POST.get('text', '')
                review.save()
                return HttpResponseRedirect(reverse('home'))  
            except Review.DoesNotExist:
                pass
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
        'user': request.user,
        'avg_top_rate': round(avg_top_rate, 2),
        'total_articles': total_articles,
        'editing_review_id': editing_review_id,
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

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileForm

@login_required
def profile_view(request):
    user = request.user

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')  
    else:
        form = ProfileForm(instance=user)

    return render(request, 'core/profile.html', {
        'form': form,
        'user': user,
    })


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
def compare_offers(request):
    offers = CreditOffer.objects.all().select_related('bank', 'credit_type')
    return render(request, 'core/compare.html', {'offers': offers})
def save_calculation(request):
    if request.method == 'POST':
        try:
            CalculationHistory.objects.create(
                user=request.user,
                amount=request.POST.get('amount'),
                term=request.POST.get('term'),
                rate=request.POST.get('rate'),
                result=request.POST.get('result')
            )
            messages.success(request, 'Расчет успешно сохранен в историю')
        except Exception as e:
            messages.error(request, f'Ошибка при сохранении: {str(e)}')
        return redirect('offer_detail', offer_id=request.POST.get('offer_id'))
from django.shortcuts import render, get_object_or_404
from .models import CreditOffer

def compare_offers(request):
    offers = CreditOffer.objects.all().select_related('bank', 'credit_type')
    return render(request, 'core/compare.html', {'offers': offers})

def compare_detail(request, offer1_id, offer2_id):
    offer1 = get_object_or_404(CreditOffer, id=offer1_id)
    offer2 = get_object_or_404(CreditOffer, id=offer2_id)
    def calculate_payment(offer, amount=100000, term=12):
        monthly_rate = offer.rate / 12 / 100
        return (amount * monthly_rate) / (1 - (1 + monthly_rate) ** -term)
    
    context = {
        'offer1': offer1,
        'offer2': offer2,
        'payment1': round(calculate_payment(offer1), 2),
        'payment2': round(calculate_payment(offer2), 2),
    }
    return render(request, 'core/compare_detail.html', context)
@login_required
def favorites(request):
    favorites = FavoriteOffer.objects.filter(user=request.user).select_related('offer__bank', 'offer__credit_type')
    return render(request, 'core/favorites.html', {'favorites': favorites})
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
    reviews = Review.objects.filter(offer=offer).order_by('-created_at')
    review_form = ReviewForm()
    if request.method == 'POST':
        if 'review_id' in request.POST:
            review_id = request.POST.get('review_id')
            try:
                review = Review.objects.get(id=review_id, user=request.user)
                review.text = request.POST.get('text')
                review.save()
                return JsonResponse({
                    'success': True,
                    'text': review.text
                })
            except Review.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Отзыв не найден'
                })

    if request.method == 'POST' and 'text' in request.POST:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.offer = offer
            review.user = request.user
            review.save()
            return redirect('offer_detail', offer_id=offer_id)
    else:
        form = ReviewForm()

    return render(request, 'core/offer_detail.html', {
        'offer': offer,
        'reviews': reviews,
        'review_form': review_form,
        'user': request.user
    })

def auth_test(request):
    return render(request, 'core/auth_test.html', {
        'user': request.user,
        'session': request.session
    })

def test_static(request):
    return render(request, 'test_static.html')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.utils import timezone
import json
from .models import (
    BudgetItem, 
    FavoriteOffer, 
    CalculationHistory, 
    ActionLog, 
    Poll
)

@login_required
def dashboard_view(request):
    user = request.user
    totals = BudgetItem.objects.filter(user=user).aggregate(
        income=Sum('amount', filter=Q(item_type='income')),
        expense=Sum('amount', filter=Q(item_type='expense'))
    )
    
    income = float(totals['income'] or 0)
    expense = float(totals['expense'] or 0)
    balance = income - expense

    chart_data = {
        'income': income,
        'expense': expense,
        'balance': balance
    }
    calculation_form = CalculationForm()
    calculation_result = None
    favorites_count = FavoriteOffer.objects.filter(user=user).count()
    total_payments = CalculationHistory.objects.filter(user=user).aggregate(total=Sum('result'))['total'] or 0
    if request.method == 'POST' and 'calculate' in request.POST:
        calculation_form = CalculationForm(request.POST)
        if calculation_form.is_valid():
            amount = calculation_form.cleaned_data['amount']
            term = calculation_form.cleaned_data['term']
            rate = calculation_form.cleaned_data['rate']
            monthly_rate = rate / 12 / 100
            monthly_payment = (amount * monthly_rate) / (1 - (1 + monthly_rate) ** -term)
            CalculationHistory.objects.create(
                user=user,
                amount=amount,
                term=term,
                rate=rate,
                result=round(monthly_payment, 2)
            )
            
            calculation_result = {
                'monthly': round(monthly_payment, 2),
                'total': round(monthly_payment * term, 2),
                'overpayment': round(monthly_payment * term - amount, 2)
            }
            totals = BudgetItem.objects.filter(user=user).aggregate(
                income=Sum('amount', filter=Q(item_type='income')),
                expense=Sum('amount', filter=Q(item_type='expense'))
            )
            
            result = {
                'monthly_payment': round(monthly_payment, 2),
                'total_payment': round(monthly_payment * term, 2),
                'overpayment': round(monthly_payment * term - amount, 2)
            }
    context = {
        'budget_items': BudgetItem.objects.filter(user=request.user).order_by('-date')[:5],
        'income_total': income,
        'expense_total': expense,
        'balance': balance,
        'chart_data_json': json.dumps(chart_data),
        
        'favorites': FavoriteOffer.objects.filter(user=user)
                       .select_related('offer__bank', 'offer__credit_type')[:5],

        'calculations': CalculationHistory.objects.filter(user=user)
                       .order_by('-created_at')[:5],
        
        'actions': ActionLog.objects.filter(user=user)
                   .order_by('-timestamp')[:5],
        
        'active_poll': Poll.objects.order_by('-created_at').first(),
        
        'user': user,
        'now': timezone.now(),
        'calculation_form': calculation_form,
        'calculation_result': calculation_result,
        'favorites_count': favorites_count,
        'total_payments': total_payments
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

from django import forms

class CalculationForm(forms.Form):
    amount = forms.FloatField(
        label='Сумма кредита',
        min_value=1000,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '10 000 ₽'})
    )
    term = forms.IntegerField(
        label='Срок',
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '12 мес.'})
    )
    rate = forms.FloatField(
        label='Ставка',
        min_value=0.1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '15%'})
    )


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt  

@require_POST
def calculate_credit_ajax(request):
    try:
        amount = float(request.POST.get('amount'))
        term = int(request.POST.get('term'))
        rate = float(request.POST.get('rate'))

        monthly_rate = rate / 12 / 100
        monthly_payment = (amount * monthly_rate) / (1 - (1 + monthly_rate) ** -term)
        total_payment = monthly_payment * term
        overpayment = total_payment - amount

        return JsonResponse({
            'monthly': round(monthly_payment, 2),
            'total': round(total_payment, 2),
            'overpayment': round(overpayment, 2),
        })
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Неверные данные'}, status=400)
    

from django.shortcuts import render
from .models import CalculationHistory

def calculation_history(request):
    calculations = CalculationHistory.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/calculation_history.html', {'calculations': calculations})

from django.shortcuts import redirect, get_object_or_404, render
from .models import Review, CreditOffer
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required
def repeat_calculation(request, calc_id):
    calculation = get_object_or_404(CalculationHistory, id=calc_id, user=request.user)
    return redirect('calculator')  
@login_required
def add_offer(request):
    if request.method == 'POST':
        form = CreditOfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.user = request.user
            offer.save()
            return redirect('index')
    else:
        form = CreditOfferForm()
    return render(request, 'core/offer_form.html', {'form': form})

@login_required
def add_review(request, offer_id):
    offer = get_object_or_404(CreditOffer, id=offer_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.offer = offer
            review.user = request.user
            review.save()

    return redirect('index')
from django.urls import reverse
@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            url = reverse('edit_review', kwargs={'review_id': review.id})
            return redirect(f"{url}?saved=1")
    else:
        form = ReviewForm(instance=review)

    saved = request.GET.get('saved')
    return render(request, 'edit_review.html', {'form': form, 'saved': saved})


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    if request.method == 'POST':
        review.delete()
    return redirect('index')

@login_required
def update_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    if request.method == 'POST':
        review.text = request.POST['text']
        review.save()
    return redirect('home')