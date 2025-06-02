from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Телефон')
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name=_('Аватар'),
        help_text=_('Загрузите изображение для аватара')
    )
    
    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
    
    def __str__(self):
        return self.username

class Bank(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Название'))
    logo_url = models.URLField(verbose_name=_('URL логотипа'))
    license_no = models.CharField(max_length=50, verbose_name=_('Регистрационный номер'))
    contact_info = models.TextField(verbose_name=_('Контактная информация'))

    class Meta:
        verbose_name = _('Банк')
        verbose_name_plural = _('Банки')

    def __str__(self):
        return self.name

class CreditType(models.Model):
    name = models.CharField(max_length=50, verbose_name=_('Тип кредита'))

    class Meta:
        verbose_name = _('Тип кредита')
        verbose_name_plural = _('Типы кредитов')

    def __str__(self):
        return self.name

class CreditOffer(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='offers', verbose_name=_('Банк'))
    credit_type = models.ForeignKey(CreditType, on_delete=models.CASCADE, related_name='offers', verbose_name=_('Тип кредита'))
    rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('Процентная ставка'))
    term_min = models.PositiveIntegerField(verbose_name=_('Минимальный срок (мес.)'))
    term_max = models.PositiveIntegerField(verbose_name=_('Максимальный срок (мес.)'))
    amount_min = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Минимальная сумма'))
    amount_max = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Максимальная сумма'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))

    class Meta:
        verbose_name = _('Кредитное предложение')
        verbose_name_plural = _('Кредитные предложения')
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.bank} - {self.credit_type} ({self.rate}%)'

class Article(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Заголовок'))
    content = models.TextField(verbose_name=_('Содержание'))
    image_url = models.URLField(verbose_name=_('URL изображения'))
    published_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата публикации'))

    class Meta:
        verbose_name = _('Статья')
        verbose_name_plural = _('Статьи')
        ordering = ['-published_at']

    def __str__(self):
        return self.title

class Review(models.Model):
    RATING_CHOICES = [
        (1, '★ Очень плохо'),
        (2, '★★ Плохо'),
        (3, '★★★ Удовлетворительно'),
        (4, '★★★★ Хорошо'),
        (5, '★★★★★ Отлично'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Пользователь'),
        related_name='reviews'
    )
    offer = models.ForeignKey(
        CreditOffer,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Кредитное предложение'),
        null=True,
        blank=True
    )
    text = models.TextField(verbose_name=_('Текст отзыва'))
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        default=5,
        verbose_name=_('Оценка')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))

    class Meta:
        verbose_name = _('Отзыв')
        verbose_name_plural = _('Отзывы')
        ordering = ['-created_at']
        unique_together = ['user', 'offer']

    def __str__(self):
        return f'Отзыв от {self.user} на {self.offer}'

class FavoriteOffer(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_offers',
        verbose_name=_('Пользователь')
    )
    offer = models.ForeignKey(
        CreditOffer,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name=_('Кредитное предложение')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата добавления'))

    class Meta:
        verbose_name = _('Избранное предложение')
        verbose_name_plural = _('Избранные предложения')
        unique_together = ['user', 'offer']

    def __str__(self):
        return f'{self.user} → {self.offer}'

class CreditComparison(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comparisons',
        verbose_name=_('Пользователь')
    )
    offers = models.ManyToManyField(
        CreditOffer,
        related_name='compared_in',
        verbose_name=_('Предложения для сравнения')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))

    class Meta:
        verbose_name = _('Сравнение кредитов')
        verbose_name_plural = _('Сравнения кредитов')

    def __str__(self):
        return f'Сравнение {self.user} от {self.created_at}'

class BudgetItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('income', _('Доход')),
        ('expense', _('Расход')),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='budget_items',
        verbose_name=_('Пользователь')
    )
    name = models.CharField(max_length=100, verbose_name=_('Наименование'))
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Сумма'))
    item_type = models.CharField(
        max_length=7,
        choices=ITEM_TYPE_CHOICES,
        verbose_name=_('Тип операции')
    )
    date = models.DateField(verbose_name=_('Дата операции'))

    class Meta:
        verbose_name = _('Статья бюджета')
        verbose_name_plural = _('Статьи бюджета')
        ordering = ['-date']

    def __str__(self):
        return f'{self.get_item_type_display()}: {self.name} ({self.amount})'

class CalculationHistory(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='calculations',
        verbose_name=_('Пользователь')
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Сумма кредита'))
    term = models.PositiveIntegerField(verbose_name=_('Срок (мес.)'))
    rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('Процентная ставка'))
    result = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Ежемесячный платеж'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата расчета'))

    class Meta:
        verbose_name = _('История расчетов')
        verbose_name_plural = _('История расчетов')
        ordering = ['-created_at']

    def __str__(self):
        return f'Расчет {self.user} от {self.created_at}'

class Poll(models.Model):
    question = models.CharField(max_length=255, verbose_name=_('Вопрос'))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_('Дата создания'))

    class Meta:
        verbose_name = _('Опрос')
        verbose_name_plural = _('Опросы')
        ordering = ['-created_at']

    def __str__(self):
        return self.question

    @property
    def total_votes(self):
        return sum(option.votes for option in self.options.all())

class PollOption(models.Model):
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name=_('Опрос')
    )
    text = models.CharField(max_length=255, verbose_name=_('Текст варианта'))
    votes = models.IntegerField(default=0, verbose_name=_('Количество голосов'))

    class Meta:
        verbose_name = _('Вариант ответа')
        verbose_name_plural = _('Варианты ответов')

    def __str__(self):
        return self.text

class ActionLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='actions',
        verbose_name=_('Пользователь')
    )
    action_type = models.CharField(max_length=100, verbose_name=_('Тип действия'))
    object_id = models.PositiveIntegerField(verbose_name=_('ID объекта'))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('Время'))

    class Meta:
        verbose_name = _('Лог действия')
        verbose_name_plural = _('Логи действий')
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.user} - {self.action_type}'