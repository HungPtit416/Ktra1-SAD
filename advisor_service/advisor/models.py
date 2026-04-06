from django.db import models
from django.contrib.auth.models import User

class ConversationSession(models.Model):
    """Lưu trữ phiên trò chuyện giữa khách hàng và AI Advisor"""
    CONVERSATION_TYPES = (
        ('consultation', 'Tư vấn sản phẩm'),
        ('product_info', 'Thông tin sản phẩm'),
        ('policy', 'Chính sách'),
        ('complaint', 'Khiếu nại'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    conversation_type = models.CharField(max_length=20, choices=CONVERSATION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_closed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"Session {self.session_id} - {self.conversation_type}"


class Message(models.Model):
    """Lưu trữ tin nhắn trong phiên trò chuyện"""
    MESSAGE_ROLES = (
        ('user', 'User'),
        ('assistant', 'AI Advisor'),
    )
    
    session = models.ForeignKey(ConversationSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=MESSAGE_ROLES)
    content = models.TextField()
    context_sources = models.JSONField(default=list, blank=True, help_text="Danh sách KB sources được dùng để trả lời")
    confidence_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.session.session_id} - {self.role}: {self.content[:50]}"


class CustomerBehavior(models.Model):
    """Đặc trưng hành vi khách hàng - được dùng để phân tích khách hàng"""
    DEVICE_TYPES = (
        ('laptop', 'Laptop'),
        ('mobile', 'Mobile'),
        ('both', 'Cả hai'),
    )
    
    BUDGET_RANGES = (
        ('low', 'Dưới 10 triệu'),
        ('mid', '10-20 triệu'),
        ('high', '20-30 triệu'),
        ('premium', 'Trên 30 triệu'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='behavior_profile')
    
    # Hành vi mua sắm
    total_purchases = models.IntegerField(default=0)
    avg_spending = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    preferred_device_type = models.CharField(max_length=20, choices=DEVICE_TYPES, default='both')
    preferred_budget_range = models.CharField(max_length=20, choices=BUDGET_RANGES, default='mid')
    
    # Hành vi duyệt web
    avg_session_duration = models.IntegerField(default=0, help_text="Tính bằng phút")
    product_view_count = models.IntegerField(default=0)
    favorite_categories = models.JSONField(default=dict, blank=True)
    
    # Hành vi tương tác
    last_purchase_date = models.DateTimeField(null=True, blank=True)
    last_activity_date = models.DateTimeField(auto_now=True)
    
    # Chỉ số khách hàng
    loyalty_score = models.FloatField(default=0.0, help_text="0-1.0")
    churn_risk = models.FloatField(default=0.0, help_text="0-1.0, cao = nguy hiểm mất khách")
    predicted_segment = models.CharField(max_length=50, blank=True, help_text="VD: 'High-Value', 'At-Risk', 'New'")
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Customer Behaviors"
    
    def __str__(self):
        return f"Behavior Profile - {self.user.username}"


class KnowledgeBase(models.Model):
    """Cơ sở kiến thức cho hệ thống RAG"""
    CONTENT_TYPES = (
        ('product', 'Thông tin sản phẩm'),
        ('guide', 'Hướng dẫn sử dụng'),
        ('policy', 'Chính sách & qui định'),
        ('technical', 'Thông số kỹ thuật'),
        ('comparison', 'So sánh sản phẩm'),
    )
    
    title = models.CharField(max_length=255)
    content = models.TextField()
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    related_products = models.JSONField(default=list, blank=True)
    tags = models.JSONField(default=list, blank=True, help_text="Tags để tìm kiếm")
    embedding_vector = models.JSONField(null=True, blank=True, help_text="Vector nhúng để RAG retrieval")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.content_type})"


class BehaviorAnalysisLog(models.Model):
    """Log kết quả phân tích hành vi"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='behavior_logs')
    analysis_input = models.JSONField()
    predicted_segment = models.CharField(max_length=50)
    probability_scores = models.JSONField()
    recommendations = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Analysis {self.user.username} - {self.created_at}"
