from django.shortcuts import render, get_object_or_404, redirect
from .models import CreditOffer, Article, Review, Poll, Poll
from django.db.models import Prefetch
from .forms import ReviewForm, PollForm

from django.shortcuts import render, get_object_or_404, redirect
from .models import CreditOffer, Article, Review, Poll
from django.db.models import Prefetch
from .forms import ReviewForm, PollForm

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
            # отзыв
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review_form.save()
                return redirect('home')

    return render(request, 'core/index.html', {
        'top_offers': top_offers,
        'latest_articles': latest_articles,
        'latest_reviews': latest_reviews,
        'poll': poll,
        'poll_form': poll_form, 
        'result': result,
        'review_form': review_form,
    })

def all_offers(request):
    offers = CreditOffer.objects.all()
    return render(request, 'core/all_offers.html', {'offers': offers})

def search_offers(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = CreditOffer.objects.filter(bank__name__icontains=query)
    return render(request, 'core/search_results.html', {'results': results})

def articles(request):
    articles = Article.objects.all().order_by('-published_at')
    return render(request, 'core/articles.html', {'articles': articles})

def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    return render(request, 'core/article_detail.html', {'article': article})
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

    return render(request, 'core/poll.html', {'poll': poll, 'form': form})