# 🤖 AI Advisor Service

Dịch vụ tư vấn thông minh sử dụng Deep Learning, RAG (Retrieval-Augmented Generation) và Knowledge Base để cung cấp tư vấn 24/7 cho khách hàng e-commerce.

## 🎯 Tính năng

### 1. **RAG Chatbot (Retrieval-Augmented Generation)**
- Truy xuất thông tin từ Knowledge Base sử dụng semantic search
- Tạo sinh phản hồi tư vấn chính xác dựa trên context
- Hỗ trợ hoàn toàn tiếng Việt
- Lưu lịch sử cuộc trò chuyện

### 2. **Customer Behavior Analysis**
- Phân loại khách hàng (High-Value, At-Risk, VIP, Regular, New)
- Dự đoán chỉ số churn risk (rủi ro mất khách)
- Tính loyalty score (chỉ số trung thành)
- Tạo recommendations tư vấn cá nhân hóa

### 3. **Knowledge Base Management**
- Quản lý tài liệu sản phẩm
- Tài liệu hướng dẫn sử dụng
- Chính sách bảo hành, đổi trả
- Vector embedding tự động

### 4. **Batch Processing (Celery + Redis)**
- Xử lý phân tích hành vi hàng loạt
- Cập nhật KB từ database
- Background tasks không chặn API

## 📐 Architecture

```
┌─ Frontend (ai-advisor.html)
│  └─ JavaScript WebSocket/HTTP Client
│
├─ Gateway (Nginx)
│  └─ /api/advisor/ → Advisor Service
│
├─ Advisor Service (Django + DRF)
│  ├─ Chat API (/sessions/send_message/)
│  ├─ Behavior Analysis API (/analysis/analyze/)
│  └─ KB Management
│
├─ RAG System
│  ├─ Embedding Model (sentence-transformers)
│  ├─ Vector DB (ChromaDB)
│  └─ LLM (OpenAI/Ollama)
│
├─ ML Models
│  ├─ Behavior Classifier (Random Forest)
│  ├─ Feature Scaler (StandardScaler)
│  └─ Models Storage
│
└─ Data Layer
   ├─ PostgreSQL (advisor_db)
   ├─ Redis (Cache + Celery Broker)
   └─ ChromaDB (Vector Storage)
```

## 🚀 Cách chạy

### Cách 1: Docker (Khuyến nghị)

```bash
# Từ thư mục gốc project
docker-compose up -d advisor-service advisor-db redis

# Chạy migration
docker-compose exec advisor-service python manage.py migrate

# Tải Knowledge Base sample
docker-compose exec advisor-service python manage.py load_kb --sample

# Xem logs
docker-compose logs -f advisor-service
```

### Cách 2: Development (Local)

```bash
# Tạo virtual environment
python -m venv venv

# Activate
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt

# Cấu hình environment
cp .env.example .env
# Chỉnh sửa .env với database config

# Migration
python manage.py migrate

# Tải KB sample
python manage.py load_kb --sample

# Chạy server
python manage.py runserver 0.0.0.0:8003

# Celery (Terminal khác)
celery -A advisor_service worker -l info
```

## 📚 Knowledge Base

### Tải dữ liệu mẫu

```bash
python manage.py load_kb --sample
```

### Tải từ file JSON

```bash
python manage.py load_kb --file kb_data.json
```

### Cấu trúc file kb_data.json

```json
[
  {
    "title": "MacBook Air M3",
    "content": "Mô tả chi tiết sản phẩm...",
    "content_type": "product",
    "tags": ["apple", "laptop"],
    "is_active": true
  },
  {
    "title": "Chính sách bảo hành",
    "content": "Nội dung chính sách...",
    "content_type": "policy",
    "tags": ["warranty"],
    "is_active": true
  }
]
```

## 🔌 API Endpoints

### Chat API

#### Bắt đầu session
```bash
POST /api/advisor/sessions/start_chat/
Content-Type: application/json

{
  "conversation_type": "consultation"
}

Response:
{
  "success": true,
  "session_id": "abc123",
  "data": {...}
}
```

#### Gửi tin nhắn
```bash
POST /api/advisor/sessions/send_message/
Content-Type: application/json

{
  "session_id": "abc123",
  "message": "Laptop nào tốt cho lập trình?"
}

Response:
{
  "success": true,
  "session_id": "abc123",
  "message": {
    "role": "assistant",
    "content": "Phản hồi tư vấn...",
    "context_sources": [
      {
        "title": "ThinkPad X1",
        "similarity": 0.92
      }
    ],
    "confidence_score": 0.85
  }
}
```

#### Lấy lịch sử chat
```bash
GET /api/advisor/sessions/history/?session_id=abc123

Response:
{
  "id": 1,
  "session_id": "abc123",
  "messages": [
    {
      "role": "user",
      "content": "..."
    },
    {
      "role": "assistant",
      "content": "..."
    }
  ]
}
```

### Behavior Analysis API

#### Phân tích hành vi
```bash
POST /api/advisor/analysis/analyze/
Content-Type: application/json

{
  "user_id": 1,
  "behavior_data": {
    "total_purchases": 5,
    "avg_spending": 15000000,
    "avg_session_duration": 30,
    "product_view_count": 50,
    "days_since_last_purchase": 10
  }
}

Response:
{
  "success": true,
  "analysis": {
    "predicted_segment": "High-Value",
    "probability_scores": {
      "churn_risk": 0.2,
      "loyalty_score": 0.85
    },
    "recommendations": [
      "Tư vấn sản phẩm cao cấp",
      "Chương trình loyalty"
    ]
  }
}
```

#### Lấy profil hành vi
```bash
GET /api/advisor/behavior/profile/?user_id=1

Response:
{
  "user_id": 1,
  "predicted_segment": "High-Value",
  "loyalty_score": 0.85,
  "churn_risk": 0.2,
  "recommended_products": [...]
}
```

## 🛠 Management Commands

### Load Knowledge Base
```bash
# Tải sample KB
python manage.py load_kb --sample

# Tải từ file
python manage.py load_kb --file path/to/file.json
```

## 🧪 Testing

### Test API dengan curl

```bash
# Test chat
curl -X POST http://localhost:8003/api/advisor/sessions/send_message/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session",
    "message": "Laptop nào tốt cho design?"
  }'

# Test behavior analysis
curl -X POST http://localhost:8003/api/advisor/analysis/analyze/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "behavior_data": {
      "total_purchases": 3,
      "avg_spending": 10000000
    }
  }'
```

### Test Web Interface

Truy cập admin: `http://localhost:8003/admin`
- Đăng nhập bằng admin account
- Quản lý Knowledge Base
- Xem lịch sử chat
- Xem hành vi khách hàng

## 📊 Database Models

### ConversationSession
- `session_id`: Mã phiên (unique)
- `user`: Khách hàng (optional)
- `conversation_type`: Loại cuộc trò chuyện
- `created_at`: Thời gian tạo
- `is_closed`: Có đóng hay không

### Message
- `session`: Tham chiếu đến ConversationSession
- `role`: "user" hay "assistant"
- `content`: Nội dung tin nhắn
- `context_sources`: KB sources được dùng
- `confidence_score`: Độ chính xác

### CustomerBehavior
- `user`: Khách hàng
- `total_purchases`: Số lần mua
- `avg_spending`: Mức chi tiêu trung bình
- `predicted_segment`: Phân loại khách hàng
- `churn_risk`: Chỉ số rủi ro
- `loyalty_score`: Chỉ số trung thành

### KnowledgeBase
- `title`: Tiêu đề
- `content`: Nội dung
- `content_type`: Loại nội dung
- `tags`: Tags tìm kiếm
- `embedding_vector`: Vector nhúng cho RAG

## 🔧 Configuration

### .env Variables

```env
# Django
DJANGO_SECRET_KEY=your-key
DEBUG=True

# Database
DB_NAME=advisor_db
DB_USER=advisor_user
DB_PASSWORD=advisor_pass
DB_HOST=localhost
DB_PORT=5432

# OpenAI (optional)
OPENAI_API_KEY=your-key

# RAG
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-mpnet-base-v2

# Cache & Celery
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379
```

## 📈 Monitoring

### Logs
```bash
# Docker logs
docker-compose logs -f advisor-service

# Output file
tail -f logs/advisor.log
```

### Admin Dashboard
- Truy cập: `http://localhost:8003/admin`
- Xem số lượng chat sessions
- Xem behavior profiles
- Quản lý KB documents

### Redis Monitor
```bash
redis-cli monitor
```

## 🐛 Troubleshooting

### Lỗi: "Cannot connect to database"
- Kiểm tra PostgreSQL running
- Kiểm tra DB credentials trong .env

### Lỗi: "ChromaDB connection failed"
- Xóa folder: `rm -rf chroma_db/`
- Restart service

### Lỗi: "RAG Engine not initialized"
- Đảm bảo sentence-transformers đã cài
- Chạy `python manage.py load_kb --sample`

### Bộ nhớ thiếu
- Giảm batch size trong settings
- Tắt GPU nếu RAM <8GB

## 📚 Advanced Usage

### Custom LLM Integration

Sửa file `advisor/rag_system/rag_engine.py`:

```python
def _call_llm(self, prompt: str) -> str:
    # Thay thế bằng LLM của bạn (GPT, Claude, etc)
    response = your_llm.generate(prompt)
    return response
```

### Training Custom Behavior Model

```python
from advisor.ml_models.behavior_classifier import BehaviorClassifier
import numpy as np

classifier = BehaviorClassifier()
X = np.array([...])  # Features
y = np.array([...])  # Labels
classifier.train(X, y)
```

## 🚀 Deployment

### Production Checklist

- [ ] Cấu hình HTTPS/SSL
- [ ] Cấu hình CORS đúng
- [ ] Tắt DEBUG mode
- [ ] Cấu hình email notifications
- [ ] Cấu hình backup database
- [ ] Giảm log level thành WARNING
- [ ] Cấu hình monitoring & alerting

### Docker Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📝 Contributing

Hãy fork và tạo pull request nếu muốn đóng góp!

## 📄 License

MIT License - Xem file LICENSE để chi tiết

## 📞 Support

Gặp vấn đề? Liên hệ:
- Email: support@ecommerce.vn
- Chat: Trong giờ 8h-22h

---

**Phiên bản:** 1.0.0  
**Cập nhật lần cuối:** 2024  
**Trạng thái:** ✅ Production Ready
