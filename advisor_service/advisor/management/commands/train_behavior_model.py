"""
Management command: Train Deep Learning behavior classifier model
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'advisor_service.settings')

import django
django.setup()

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Avg
from datetime import datetime, timedelta
import numpy as np
from advisor.ml_models.behavior_classifier import BehaviorClassifier
from advisor.models import CustomerBehavior, BehaviorAnalysisLog
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    help = 'Train Deep Learning behavior classifier model từ dữ liệu khách hàng'
    
    def add_arguments(self, parser):
        parser.add_argument('--epochs', type=int, default=50, help='Number of training epochs')
        parser.add_argument('--batch-size', type=int, default=32, help='Batch size')
        parser.add_argument('--min-samples', type=int, default=10, help='Minimum samples required to train')
    
    def handle(self, *args, **options):
        epochs = options['epochs']
        batch_size = options['batch_size']
        min_samples = options['min_samples']
        
        self.stdout.write(self.style.SUCCESS(f"🔨 Bắt đầu training Deep Learning Behavior Model..."))
        self.stdout.write(f"   Epochs: {epochs}, Batch Size: {batch_size}")
        
        try:
            # Lấy dữ liệu training
            X, y = self._extract_training_data(min_samples)
            
            if len(X) < min_samples:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️  Chỉ có {len(X)} mẫu (cần tối thiểu {min_samples}). "
                        f"Sử dụng synthetic data..."
                    )
                )
                X, y = self._generate_synthetic_data(min_samples * 3)
            
            self.stdout.write(f"✅ Đã tải {len(X)} mẫu training data")
            
            # Khởi tạo classifier
            classifier = BehaviorClassifier()
            
            if classifier.model is None:
                self.stdout.write(self.style.ERROR("❌ TensorFlow không có hoặc model nullptr"))
                return
            
            # Train model
            self.stdout.write(f"🚀 Đang train với {len(X)} mẫu...")
            history = classifier.train(X, y, epochs=epochs, batch_size=batch_size, validation_split=0.2)
            
            # Log kết quả
            final_loss = history.history['loss'][-1]
            final_accuracy = history.history['accuracy'][-1]
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Training hoàn tất!\n"
                    f"   Final Loss: {final_loss:.4f}\n"
                    f"   Final Accuracy: {final_accuracy:.4f}"
                )
            )
            
            # Lưu log
            BehaviorAnalysisLog.objects.create(
                analysis_type='model_training',
                description=f'Trained DNN model with {len(X)} samples, {epochs} epochs',
                result_data={
                    'final_loss': float(final_loss),
                    'final_accuracy': float(final_accuracy),
                    'samples': len(X),
                    'epochs': epochs
                }
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Lỗi: {str(e)}"))
            import traceback
            traceback.print_exc()
    
    def _extract_training_data(self, min_samples=10):
        """Trích xuất dữ liệu training từ customer behavior trong database"""
        behaviors = []
        
        # Vì orders là microservice khác, sử dụng dữ liệu CustomerBehavior hiện tại
        try:
            from advisor.models import CustomerBehavior
            behavior_profiles = CustomerBehavior.objects.filter(total_purchases__gt=0).all()
            
            self.stdout.write(f"📊 Tìm thấy {len(behavior_profiles)} customer behavior profiles")
            
            for profile in behavior_profiles:
                # Tính segment dựa trên heuristic
                if profile.avg_spending > 800000:  # 800k
                    if profile.total_purchases > 30:
                        segment = 4  # VIP
                    else:
                        segment = 0  # High-Value
                elif profile.churn_risk > 0.7 and profile.loyalty_score < 0.3:
                    segment = 1  # At-Risk
                elif profile.total_purchases == 1:
                    segment = 2  # New
                else:
                    segment = 3  # Regular
                
                features = [
                    profile.total_purchases,
                    profile.avg_spending,
                    profile.avg_session_duration,
                    profile.product_view_count,
                    profile.days_since_last_purchase,
                    profile.purchase_frequency,
                    profile.product_variety_score
                ]
                behaviors.append((features, segment))
            
            if len(behaviors) >= min_samples:
                X = np.array([x[0] for x in behaviors], dtype=np.float32)
                y = np.array([x[1] for x in behaviors], dtype=np.int32)
                return X, y
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️  Could not load real data: {str(e)}"))
        
        return np.array([], dtype=np.float32), np.array([], dtype=np.int32)
    
    def _generate_synthetic_data(self, num_samples=100):
        """Tạo synthetic data nếu không đủ real data"""
        np.random.seed(42)
        X = np.random.randn(num_samples, 7).astype(np.float32)
        
        # Normalize
        X[:, 0] = np.abs(X[:, 0]) * 50  # total_purchases (0-50)
        X[:, 1] = np.abs(X[:, 1]) * 500000 + 200000  # avg_spending (200k-1.2M)
        X[:, 2] = np.abs(X[:, 2]) * 30 + 10  # session_duration (10-40 min)
        X[:, 3] = np.abs(X[:, 3]) * 100  # product_view_count
        X[:, 4] = np.abs(X[:, 4]) * 90  # days_since_last
        X[:, 5] = np.abs(X[:, 5]) * 5 + 0.1  # purchase_frequency
        X[:, 6] = np.abs(X[:, 6]) * 5  # product_variety
        
        # Generate labels based on features
        y = np.zeros(num_samples, dtype=np.int32)
        for i in range(num_samples):
            if X[i, 1] > 800000:  # High spending
                y[i] = 4 if X[i, 0] > 30 else 0  # VIP or High-Value
            elif X[i, 4] > 60:  # Long time since last purchase
                y[i] = 1  # At-Risk
            elif X[i, 0] == 1:
                y[i] = 2  # New
            else:
                y[i] = 3  # Regular
        
        self.stdout.write(f"📊 Generated {num_samples} synthetic samples")
        return X, y
