from django import forms
from .models import PollOption, Review  # Добавляем импорт модели Review

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

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['user', 'text']  # Укажите поля, которые должны быть в форме
        
        # Опционально: добавьте виджеты для кастомизации полей
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'user': forms.TextInput(attrs={'class': 'form-control'})
        }