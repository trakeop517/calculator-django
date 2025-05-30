# core/admin.py

from django.contrib import admin
from .models import (
    Bank, CreditType, CreditOffer, Article, User,
    Comparison, FavoriteOffer, ActionLog, BudgetPlan, Poll, PollOption
)

class CreditOfferInline(admin.TabularInline):  
    model = CreditOffer
    extra = 0
    classes = ['collapse']
    raw_id_fields = ('bank', 'credit_type')

class ComparisonInline(admin.TabularInline):
    model = Comparison
    extra = 0
    autocomplete_fields = ('offer',)

class FavoriteOfferInline(admin.TabularInline):
    model = FavoriteOffer
    extra = 0
    autocomplete_fields = ('offer',)

class ActionLogInline(admin.TabularInline):
    model = ActionLog
    extra = 0

class BudgetPlanInline(admin.TabularInline):
    model = BudgetPlan
    extra = 0

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('name', 'license_no')
    search_fields = ('name',)
    inlines = [CreditOfferInline]  
    list_display_links = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'logo_url', 'license_no', 'contact_info')
        }),
    )

@admin.register(CreditType)
class CreditTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_display_links = ('name',)

@admin.register(CreditOffer)
class CreditOfferAdmin(admin.ModelAdmin):
    list_display = ('bank', 'credit_type', 'rate', 'term_min', 'term_max', 'amount_min', 'amount_max', 'updated_at')
    list_filter = ('bank', 'credit_type')
    date_hierarchy = 'updated_at'
    raw_id_fields = ('bank', 'credit_type')
    search_fields = ('bank__name', 'credit_type__name')
    list_editable = ('rate', 'term_min', 'term_max', 'amount_min', 'amount_max')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at')
    list_display_links = ('title',)
    search_fields = ('title', 'content')
    date_hierarchy = 'published_at'
    readonly_fields = ('published_at',)
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'image_url')
        }),
        ('Даты', {
            'fields': ('published_at',)
        }),
    )

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email')
    date_hierarchy = 'created_at'
    inlines = [
        ComparisonInline,
        FavoriteOfferInline,
        ActionLogInline,
        BudgetPlanInline,
    ]
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'password')
        }),
        ('Даты', {
            'fields': ('created_at',)
        }),
    )

@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'object_id', 'timestamp')
    list_filter = ('action_type',)
    date_hierarchy = 'timestamp'
    raw_id_fields = ('user',)
    search_fields = ('action_type',)

@admin.register(BudgetPlan)
class BudgetPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'income', 'expenses', 'created_at')
    list_filter = ('user',)
    date_hierarchy = 'created_at'
    raw_id_fields = ('user',)
    search_fields = ('user__name',)

class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 1 

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    inlines = [PollOptionInline] 
    list_display = ('question', 'created_at') 

@admin.register(PollOption)
class PollOptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'votes', 'poll') 