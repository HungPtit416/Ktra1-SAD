from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.contrib.auth.models import User
import uuid
import logging

from .models import ConversationSession, Message, CustomerBehavior, KnowledgeBase, BehaviorAnalysisLog
from .serializers import (
    ConversationSessionSerializer, MessageSerializer, CustomerBehaviorSerializer,
    KnowledgeBaseSerializer, BehaviorAnalysisLogSerializer, ChatRequestSerializer, ChatResponseSerializer
)
from .rag_system.rag_engine import RAGEngine
from .ml_models.behavior_classifier import BehaviorClassifier

logger = logging.getLogger(__name__)


class ChatViewSet(viewsets.ModelViewSet):
    """
    API cho chat tư vấn sử dụng RAG
    """
    queryset = ConversationSession.objects.all()
    serializer_class = ConversationSessionSerializer
    permission_classes = [AllowAny]
    rag_engine = RAGEngine()
    
    @action(detail=False, methods=['post'])
    def start_chat(self, request):
        """Bắt đầu phiên tro chuyện mới"""
        try:
            session_id = str(uuid.uuid4())[:8]
            user = request.user if request.user.is_authenticated else None
            conversation_type = request.data.get('conversation_type', 'consultation')
            
            session = ConversationSession.objects.create(
                session_id=session_id,
                user=user,
                conversation_type=conversation_type
            )
            
            serializer = self.get_serializer(session)
            return Response({
                'success': True,
                'session_id': session_id,
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error starting chat: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """Gửi tin nhắn và nhận phản hồi từ RAG"""
        try:
            serializer = ChatRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            session_id = serializer.validated_data['session_id']
            user_message = serializer.validated_data['message']
            
            # Tìm hoặc tạo session
            session, created = ConversationSession.objects.get_or_create(
                session_id=session_id,
                defaults={'conversation_type': 'consultation'}
            )
            
            # Lưu tin nhắn người dùng
            user_msg_obj = Message.objects.create(
                session=session,
                role='user',
                content=user_message
            )
            
            # Sử dụng RAG để tạo phản hồi
            rag_response = self.rag_engine.generate_response(
                query=user_message,
                session_context=self._get_session_context(session)
            )
            
            # Tạo tin nhắn phản hồi từ AI
            ai_msg_obj = Message.objects.create(
                session=session,
                role='assistant',
                content=rag_response['answer'],
                context_sources=rag_response['sources'],
                confidence_score=rag_response['confidence']
            )
            
            # Cập nhật thời gian session
            session.updated_at = timezone.now()
            session.save(update_fields=['updated_at'])
            
            response_data = {
                'success': True,
                'session_id': session_id,
                'message': {
                    'role': 'assistant',
                    'content': rag_response['answer'],
                    'context_sources': rag_response['sources'],
                    'confidence_score': rag_response['confidence']
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        except ConversationSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_session_context(self, session):
        """Lấy bối cảnh từ lịch sử phiên"""
        messages = session.messages.all().order_by('-created_at')[:10]
        context = []
        for msg in reversed(messages):
            context.append({
                'role': msg.role,
                'content': msg.content
            })
        return context
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Lấy lịch sử chat"""
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({'error': 'session_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            session = ConversationSession.objects.get(session_id=session_id)
            serializer = self.get_serializer(session)
            return Response(serializer.data)
        except ConversationSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)


class BehaviorAnalysisViewSet(viewsets.ViewSet):
    """
    API để phân tích hành vi khách hàng
    """
    permission_classes = [AllowAny]
    behavior_classifier = BehaviorClassifier()
    
    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """Phân tích hành vi khách hàng dựa trên dữ liệu"""
        try:
            user_id = request.data.get('user_id')
            behavior_data = request.data.get('behavior_data', {})
            
            user = User.objects.get(id=user_id)
            behavior_profile, _ = CustomerBehavior.objects.get_or_create(user=user)
            
            # Phân loại khách hàng sử dụng ML model
            analysis_result = self.behavior_classifier.predict(
                customer_data=behavior_data,
                behavior_profile=behavior_profile
            )
            
            # Lưu log
            analysis_log = BehaviorAnalysisLog.objects.create(
                user=user,
                analysis_input=behavior_data,
                predicted_segment=analysis_result['segment'],
                probability_scores=analysis_result['scores'],
                recommendations=analysis_result['recommendations']
            )
            
            # Cập nhật behavior profile
            behavior_profile.predicted_segment = analysis_result['segment']
            behavior_profile.churn_risk = analysis_result['scores'].get('churn_risk', 0)
            behavior_profile.loyalty_score = analysis_result['scores'].get('loyalty_score', 0)
            behavior_profile.save()
            
            return Response({
                'success': True,
                'analysis': BehaviorAnalysisLogSerializer(analysis_log).data
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error analyzing behavior: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Lấy profil hành vi khách hàng"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            behavior = CustomerBehavior.objects.get(user_id=user_id)
            serializer = CustomerBehaviorSerializer(behavior)
            return Response(serializer.data)
        except CustomerBehavior.DoesNotExist:
            return Response({'error': 'Behavior profile not found'}, status=status.HTTP_404_NOT_FOUND)
