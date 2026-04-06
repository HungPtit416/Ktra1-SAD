"""
Behavior Classifier - Mô hình phân loại hành vi khách hàng
Sử dụng Deep Learning (Neural Network - TensorFlow/Keras) để dự đoán segment khách hàng
"""

import os
import pickle
import logging
from typing import Dict, Any
import numpy as np
from sklearn.preprocessing import StandardScaler
import json

# Deep Learning imports
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, Sequential
    from tensorflow.keras.optimizers import Adam
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False
    print("⚠️ Warning: TensorFlow not installed. Install with: pip install tensorflow")

logger = logging.getLogger(__name__)


class BehaviorClassifier:
    """
    Mô hình phân loại hành vi khách hàng sử dụng DEEP Learning (7 Hidden Layers)
    
    Architecture (True Deep Artificial Neural Network):
    - Input Layer: 7 features (standard scaled)
    - Hidden Layer 1: 128 neurons + ReLU + BatchNorm + Dropout(35%)
    - Hidden Layer 2: 96 neurons + ReLU + BatchNorm + Dropout(35%)
    - Hidden Layer 3: 64 neurons + ReLU + BatchNorm + Dropout(30%)
    - Hidden Layer 4: 48 neurons + ReLU + BatchNorm + Dropout(30%)
    - Hidden Layer 5: 32 neurons + ReLU + BatchNorm + Dropout(25%)
    - Hidden Layer 6: 16 neurons + ReLU + BatchNorm + Dropout(20%)
    - Hidden Layer 7: 8 neurons + ReLU + Dropout(15%)
    - Output Layer: 5 neurons + Softmax (one for each segment)
    
    Total Network Depth: 9 layers
    Segments: High-Value, At-Risk, New, Regular, VIP
    """
    
    def __init__(self):
        """Khởi tạo Behavior Classifier với Deep Learning"""
        self.model_path = os.path.join(os.path.dirname(__file__), 'models')
        os.makedirs(self.model_path, exist_ok=True)
        
        self.model = None
        self.scaler = None
        self.feature_names = [
            'total_purchases',
            'avg_spending',
            'avg_session_duration',
            'product_view_count',
            'days_since_last_purchase',
            'purchase_frequency',
            'product_variety_score',
        ]
        self.segments = ['High-Value', 'At-Risk', 'New', 'Regular', 'VIP']
        
        self._load_or_init_model()
    
    def _load_or_init_model(self):
        """Load hoặc tạo mô hình Deep Learning mới"""
        model_file = os.path.join(self.model_path, 'behavior_model.h5')
        scaler_file = os.path.join(self.model_path, 'scaler.pkl')
        
        if os.path.exists(model_file) and os.path.exists(scaler_file) and HAS_TENSORFLOW:
            try:
                self.model = keras.models.load_model(model_file)
                with open(scaler_file, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info("✅ Loaded pre-trained Deep Learning behavior model")
            except Exception as e:
                logger.warning(f"⚠️ Could not load model: {str(e)}, creating new one")
                self._create_neural_network()
        else:
            self._create_neural_network()
    
    def _create_neural_network(self):
        """Tạo DEEP Learning Neural Network Model - 7 Hidden Layers (True Deep Learning)"""
        if not HAS_TENSORFLOW:
            logger.error("❌ TensorFlow not available. Using fallback heuristic.")
            self.model = None
            self.scaler = StandardScaler()
            return
        
        logger.info("🔨 Building DEEP Neural Network with 7 Hidden Layers...")
        
        # Tạo Sequential model với 7 hidden layers
        self.model = Sequential([
            # Input layer: 7 features
            layers.Input(shape=(7,), name='input'),
            
            # Hidden layer 1: 128 neurons
            layers.Dense(128, name='dense_1'),
            layers.BatchNormalization(name='batch_norm_1'),
            layers.Activation('relu', name='relu_1'),
            layers.Dropout(0.35, name='dropout_1'),
            
            # Hidden layer 2: 96 neurons
            layers.Dense(96, name='dense_2'),
            layers.BatchNormalization(name='batch_norm_2'),
            layers.Activation('relu', name='relu_2'),
            layers.Dropout(0.35, name='dropout_2'),
            
            # Hidden layer 3: 64 neurons
            layers.Dense(64, name='dense_3'),
            layers.BatchNormalization(name='batch_norm_3'),
            layers.Activation('relu', name='relu_3'),
            layers.Dropout(0.3, name='dropout_3'),
            
            # Hidden layer 4: 48 neurons
            layers.Dense(48, name='dense_4'),
            layers.BatchNormalization(name='batch_norm_4'),
            layers.Activation('relu', name='relu_4'),
            layers.Dropout(0.3, name='dropout_4'),
            
            # Hidden layer 5: 32 neurons
            layers.Dense(32, name='dense_5'),
            layers.BatchNormalization(name='batch_norm_5'),
            layers.Activation('relu', name='relu_5'),
            layers.Dropout(0.25, name='dropout_5'),
            
            # Hidden layer 6: 16 neurons
            layers.Dense(16, name='dense_6'),
            layers.BatchNormalization(name='batch_norm_6'),
            layers.Activation('relu', name='relu_6'),
            layers.Dropout(0.2, name='dropout_6'),
            
            # Hidden layer 7: 8 neurons
            layers.Dense(8, name='dense_7'),
            layers.Activation('relu', name='relu_7'),
            layers.Dropout(0.15, name='dropout_7'),
            
            # Output layer: 5 segments (Softmax)
            layers.Dense(5, activation='softmax', name='output')
        ], name='BehaviorClassifier_DeepDNN')
        
        # Compile model
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Initialize scaler
        self.scaler = StandardScaler()
        
        logger.info("✅ Created DEEP Neural Network with 7 Hidden Layers")
        logger.info("   Architecture: 7 -> 128 -> 96 -> 64 -> 48 -> 32 -> 16 -> 8 -> 5")
        logger.info("   Total Layers: 9 (1 input + 7 hidden + 1 output)")
        logger.info("   Activation: ReLU (hidden) + Softmax (output)")
        logger.info("   Regularization: BatchNormalization + Dropout (0.15-0.35)")
        self.model.summary()
    
    def extract_features(self, customer_data: Dict[str, Any], behavior_profile=None) -> np.ndarray:
        """
        Trích xuất features từ dữ liệu khách hàng
        
        Args:
            customer_data: Dict containing customer behavior data
            behavior_profile: Django model instance (optional)
        
        Returns:
            Feature vector (1, 7)
        """
        features = {}
        
        # Total purchases
        features['total_purchases'] = customer_data.get('total_purchases', 
                                                       behavior_profile.total_purchases if behavior_profile else 0)
        
        # Average spending
        features['avg_spending'] = customer_data.get('avg_spending', 
                                                     behavior_profile.avg_spending if behavior_profile else 0)
        
        # Average session duration
        features['avg_session_duration'] = customer_data.get('avg_session_duration', 
                                                             behavior_profile.avg_session_duration if behavior_profile else 0)
        
        # Product view count
        features['product_view_count'] = customer_data.get('product_view_count', 
                                                           behavior_profile.product_view_count if behavior_profile else 0)
        
        # Days since last purchase
        from datetime import datetime, timedelta
        last_purchase = customer_data.get('last_purchase_date')
        if last_purchase:
            days_since = (datetime.now() - last_purchase).days
        else:
            days_since = 999  # Chưa mua
        features['days_since_last_purchase'] = days_since
        
        # Purchase frequency (purchases per month)
        purchase_frequency = features['total_purchases'] / max(days_since / 30, 1)
        features['purchase_frequency'] = purchase_frequency
        
        # Product variety score (0-1)
        product_categories = customer_data.get('product_categories', [])
        variety_score = len(set(product_categories)) / max(len(product_categories), 1)
        features['product_variety_score'] = variety_score
        
        # Tạo feature vector theo thứ tự
        feature_vector = np.array([
            features[name] for name in self.feature_names
        ]).reshape(1, -1)
        
        return feature_vector
    
    def predict(self, customer_data: Dict[str, Any], behavior_profile=None) -> Dict[str, Any]:
        """
        Dự đoán segment khách hàng sử dụng Deep Learning
        
        Args:
            customer_data: Customer behavior data
            behavior_profile: Optional Django model
        
        Returns:
            {
                'segment': 'High-Value',
                'scores': {
                    'churn_risk': 0.2,
                    'loyalty_score': 0.85,
                    'confidence': 0.95
                },
                'recommendations': [...]
            }
        """
        try:
            # Trích xuất features
            feature_vector = self.extract_features(customer_data, behavior_profile)
            
            # Scale features
            if self.scaler:
                feature_vector = self.scaler.transform(feature_vector)
            
            # Dự đoán segment using Deep Learning Neural Network
            if self.model and HAS_TENSORFLOW:
                # Predict probabilities for each segment
                segment_probs = self.model.predict(feature_vector, verbose=0)[0]
                segment_idx = np.argmax(segment_probs)
                segment = self.segments[segment_idx]
                confidence = float(segment_probs[segment_idx])
            else:
                # Fallback to heuristic if model not available
                segment = self._heuristic_segment(customer_data)
                confidence = 0.6
            
            # Tính chỉ số churn risk
            churn_risk = self._calculate_churn_risk(customer_data)
            
            # Tính chỉ số loyalty
            loyalty_score = self._calculate_loyalty_score(customer_data)
            
            # Tạo recommendations
            recommendations = self._generate_recommendations(segment, customer_data)
            
            return {
                'segment': segment,
                'scores': {
                    'churn_risk': float(churn_risk),
                    'loyalty_score': float(loyalty_score),
                    'confidence': float(confidence)
                },
                'recommendations': recommendations
            }
        except Exception as e:
            logger.error(f"Error in predict: {str(e)}")
            return {
                'segment': 'Regular',
                'scores': {'churn_risk': 0.5, 'loyalty_score': 0.5, 'confidence': 0.3},
                'recommendations': ['Liên hệ bộ phận hỗ trợ để được tư vấn']
            }
    
    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 50, batch_size: int = 32, validation_split: float = 0.2):
        """
        Train the Deep Learning model
        
        Args:
            X: Training features (N x 7)
            y: Training labels (N,) - segment indices (0-4)
            epochs: Number of training epochs
            batch_size: Batch size for training
            validation_split: Validation data split ratio
        """
        if not HAS_TENSORFLOW:
            logger.error("❌ TensorFlow not available for training")
            return False
        
        try:
            logger.info(f"🚀 Training Deep Learning model with {len(X)} samples...")
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            history = self.model.fit(
                X_scaled, y,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=validation_split,
                verbose=1
            )
            
            # Save model
            model_file = os.path.join(self.model_path, 'behavior_model.h5')
            scaler_file = os.path.join(self.model_path, 'scaler.pkl')
            
            self.model.save(model_file)
            with open(scaler_file, 'wb') as f:
                pickle.dump(self.scaler, f)
            
            final_acc = history.history['accuracy'][-1]
            logger.info(f"✅ Model trained successfully! Final accuracy: {final_acc:.4f}")
            return True
        except Exception as e:
            logger.error(f"❌ Error training model: {str(e)}")
            return False
    
    def _heuristic_segment(self, customer_data: Dict[str, Any]) -> str:
        """Phân loại dựa trên heuristics nếu model chưa train"""
        total_purchases = customer_data.get('total_purchases', 0)
        avg_spending = float(customer_data.get('avg_spending', 0))
        
        if total_purchases == 0:
            return 'New'
        elif total_purchases > 10 and avg_spending > 15000000:
            return 'VIP'
        elif total_purchases > 5 and avg_spending > 10000000:
            return 'High-Value'
        elif customer_data.get('days_since_last_purchase', 999) > 90:
            return 'At-Risk'
        else:
            return 'Regular'
    
    def _calculate_churn_risk(self, customer_data: Dict[str, Any]) -> float:
        """Tính toán chỉ số rủi ro mất khách (0-1)"""
        days_since = customer_data.get('days_since_last_purchase', 0)
        total_purchases = customer_data.get('total_purchases', 0)
        
        if total_purchases <= 1 and days_since > 180:
            return 0.9
        elif days_since > 90:
            return 0.6
        elif days_since < 30:
            return 0.1
        else:
            return 0.3
    
    def _calculate_loyalty_score(self, customer_data: Dict[str, Any]) -> float:
        """Tính toán chỉ số loyalty (0-1)"""
        total_purchases = customer_data.get('total_purchases', 0)
        avg_spending = float(customer_data.get('avg_spending', 0))
        purchase_frequency = customer_data.get('purchase_frequency', 0)
        
        purchase_score = min(total_purchases / 10, 1.0)
        spending_score = min(avg_spending / 30000000, 1.0)
        frequency_score = min(purchase_frequency / 2, 1.0)
        
        loyalty = (purchase_score + spending_score + frequency_score) / 3
        return min(loyalty, 1.0)
    
    def _generate_recommendations(self, segment: str, customer_data: Dict[str, Any]) -> list:
        """Tạo recommendations dựa trên segment"""
        recommendations = {
            'VIP': [
                'Cung cấp sản phẩm exclusive và bản giới hạn',
                'Ưu đãi đặc biệt: discount 20-30% + free shipping',
                'Tư vấn cá nhân hóa từ chuyên gia',
                'Hỗ trợ ưu tiên 24/7 và sự kiện VIP riêng'
            ],
            'High-Value': [
                'Tư vấn các sản phẩm cao cấp mới',
                'Chương trình loyalty và reward hấp dẫn',
                'Discount 10-15% khi mua nhiều sản phẩm',
                'Hỗ trợ chuyên nghiệp qua call/email'
            ],
            'Regular': [
                'Thường xuyên cập nhật sản phẩm mới',
                'Khuyến mãi theo mùa và sự kiện',
                'Tư vấn sản phẩm phù hợp nhu cầu',
                'Chương trình referral: mời bạn nhận bonus'
            ],
            'At-Risk': [
                'Khuyến mãi đặc biệt để quay lại mua hàng',
                'Email/SMS nhắc nhở về sản phẩm yêu thích',
                'Bonus voucher: discount 15% + free shipping',
                'Survey để hiểu tại sao khách không mua'
            ],
            'New': [
                'Welcome bonus: discount 10% cho đơn hàng đầu',
                'Hướng dẫn chi tiết về cách mua sắm',
                'Giới thiệu sản phẩm đặc trưng phù hợp',
                'Newsletter để cập nhật khuyến mãi mới'
            ]
        }
        
        return recommendations.get(segment, ['Liên hệ bộ phận hỗ trợ để được tư vấn'])
