# core/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
class Bank(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name=_('Название'))
    logo_url = models.TextField(verbose_name=_('URL логотипа'))
    license_no = models.CharField(max_length=50, verbose_name=_('Регистрационный номер'))
    contact_info = models.TextField(verbose_name=_('Контактная информация'))

    class Meta:
        verbose_name = _('Банк')
        verbose_name_plural = _('Банки')

    def __str__(self):
        return self.name

class CreditType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name=_('Тип кредита'))

    class Meta:
        verbose_name = _('Тип кредита')
        verbose_name_plural = _('Типы кредитов')

    def __str__(self):
        return self.name

class CreditOffer(models.Model):
    id = models.AutoField(primary_key=True)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='offers', verbose_name=_('Банк'))
    credit_type = models.ForeignKey(CreditType, on_delete=models.CASCADE, related_name='offers', verbose_name=_('Тип кредита'))
    rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('Процентная ставка'))
    term_min = models.IntegerField(verbose_name=_('Минимальный срок'))
    term_max = models.IntegerField(verbose_name=_('Максимальный срок'))
    amount_min = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Минимальная сумма'))
    amount_max = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Максимальная сумма'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))

    class Meta:
        verbose_name = _('Кредитное предложение')
        verbose_name_plural = _('Кредитные предложения')

    def __str__(self):
        return f'{self.bank} - {self.credit_type} ({self.rate}%)'

class Article(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, verbose_name=_('Заголовок'))
    content = models.TextField(verbose_name=_('Содержание'))
    image_url = models.TextField(verbose_name=_('URL изображения'))
    published_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата публикации'))

    class Meta:
        verbose_name = _('Статья')
        verbose_name_plural = _('Статьи')

    def __str__(self):
        return self.title

class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name=_('Имя'))
    email = models.EmailField(max_length=100, verbose_name=_('Email'))
    password = models.CharField(max_length=255, verbose_name=_('Пароль'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        return self.name

class Comparison(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comparisons', verbose_name=_('Пользователь'))
    offer = models.ForeignKey(CreditOffer, on_delete=models.CASCADE, related_name='comparisons', verbose_name=_('Предложение'))
    compared_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата сравнения'))

    class Meta:
        verbose_name = _('Сравнение')
        verbose_name_plural = _('Сравнения')

    def __str__(self):
        return f'{self.user} - {self.offer}'

class FavoriteOffer(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name=_('Пользователь'))
    offer = models.ForeignKey(CreditOffer, on_delete=models.CASCADE, related_name='favorites', verbose_name=_('Предложение'))
    added_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата добавления'))

    class Meta:
        verbose_name = _('Избранное предложение')
        verbose_name_plural = _('Избранные предложения')

    def __str__(self):
        return f'{self.user} - {self.offer}'

class ActionLog(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions', verbose_name=_('Пользователь'))
    action_type = models.CharField(max_length=100, verbose_name=_('Тип действия'))
    object_id = models.IntegerField(verbose_name=_('ID объекта'))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('Время'))

    class Meta:
        verbose_name = _('Лог действия')
        verbose_name_plural = _('Логи действий')

    def __str__(self):
        return f'{self.user} - {self.action_type}'

class BudgetPlan(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets', verbose_name=_('Пользователь'))
    income = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Доход'))
    expenses = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Расходы'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))

    class Meta:
        verbose_name = _('План бюджета')
        verbose_name_plural = _('Планы бюджета')

    def __str__(self):
        return f'{self.user} - {self.created_at}'
    
class Review(models.Model):
    user = models.CharField(max_length=100)
    text = models.TextField(verbose_name='Текст отзыва')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'{self.user.name} — отзыв'

class Poll(models.Model):
    question = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    
    @property
    def total_votes(self):
        return sum(option.votes for option in self.options.all())
    
    def __str__(self):
        return self.question

class Choice(models.Model):
    poll = models.ForeignKey(Poll, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.text

class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    votes = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'

    def __str__(self):
        return self.text
