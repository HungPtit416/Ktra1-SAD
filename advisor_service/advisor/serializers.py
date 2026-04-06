from rest_framework import serializers
from .models import ConversationSession, Message, CustomerBehavior, KnowledgeBase, BehaviorAnalysisLog


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'context_sources', 'confidence_score', 'created_at']


class ConversationSessionSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ConversationSession
        fields = ['id', 'session_id', 'conversation_type', 'created_at', 'updated_at', 'is_closed', 'messages']


class CustomerBehaviorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBehavior
        fields = [
            'id', 'user', 'total_purchases', 'avg_spending', 'preferred_device_type',
            'preferred_budget_range', 'avg_session_duration', 'loyalty_score',
            'churn_risk', 'predicted_segment', 'last_activity_date'
        ]


class KnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBase
        fields = ['id', 'title', 'content', 'content_type', 'tags', 'is_active', 'created_at']


class BehaviorAnalysisLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BehaviorAnalysisLog
        fields = ['id', 'user', 'analysis_input', 'predicted_segment', 'probability_scores', 'recommendations', 'created_at']


class ChatRequestSerializer(serializers.Serializer):
    """Serializer cho chat request"""
    session_id = serializers.CharField(max_length=100)
    message = serializers.CharField(max_length=2000)
    user_id = serializers.IntegerField(required=False, allow_null=True)


class ChatResponseSerializer(serializers.Serializer):
    """Serializer cho chat response"""
    message = serializers.CharField()
    context_sources = serializers.ListField()
    confidence_score = serializers.FloatField()
