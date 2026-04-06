from django.contrib import admin
from .models import ConversationSession, Message, CustomerBehavior, KnowledgeBase, BehaviorAnalysisLog


@admin.register(ConversationSession)
class ConversationSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'conversation_type', 'created_at', 'is_closed')
    list_filter = ('conversation_type', 'is_closed', 'created_at')
    search_fields = ('session_id', 'user__username')
    readonly_fields = ('session_id', 'created_at', 'updated_at')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'created_at', 'confidence_score')
    list_filter = ('role', 'created_at')
    search_fields = ('session__session_id', 'content')
    readonly_fields = ('created_at',)


@admin.register(CustomerBehavior)
class CustomerBehaviorAdmin(admin.ModelAdmin):
    list_display = ('user', 'predicted_segment', 'loyalty_score', 'churn_risk', 'updated_at')
    list_filter = ('predicted_segment', 'preferred_device_type', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('updated_at',)


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'is_active', 'created_at')
    list_filter = ('content_type', 'is_active', 'created_at')
    search_fields = ('title', 'tags')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BehaviorAnalysisLog)
class BehaviorAnalysisLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'predicted_segment', 'created_at')
    list_filter = ('predicted_segment', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)
