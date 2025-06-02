from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User, Review, PollOption

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput())

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'rating': forms.Select(attrs={'class': 'form-select'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].label = 'Текст отзыва'
        self.fields['rating'].label = 'Ваша оценка'

class PollForm(forms.Form):
    choice = forms.ModelChoiceField(
        queryset=PollOption.objects.none(),
        widget=forms.RadioSelect,
        empty_label=None
    )

    def __init__(self, *args, **kwargs):
        poll = kwargs.pop('poll')
        super().__init__(*args, **kwargs)
        self.fields['choice'].queryset = poll.options.all()

from django import forms
from .models import BudgetItem

class BudgetItemForm(forms.ModelForm):
    class Meta:
        model = BudgetItem
        fields = ['name', 'amount', 'item_type', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01'})
        }