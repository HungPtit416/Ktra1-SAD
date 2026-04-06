# 🚀 AI Advisor - Setup & Integration Guide

**Ngôn ngữ:** Tiếng Việt  
**Tác giả:** AI Development Team  
**Ngày cập nhật:** $(date)

---

## 📋 Mục lục

1. [Overview](#overview)
2. [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
3. [Cài đặt nhanh (Quick Start)](#cài-đặt-nhanh)
4. [Tích hợp vào website](#tích-hợp-vào-website)
5. [Cấu hình advanced](#cấu-hình-advanced)
6. [Troubleshooting](#troubleshooting)

---

## 🤖 Overview

**AI Advisor** là một hệ thống tư vấn thông minh hoàn chỉnh gồm:

✅ **RAG Chatbot** - Trò chuyện tư vấn sử dụng Knowledge Base  
✅ **Behavior Analysis** - Phân loại + dự đoán hành vi khách hàng  
✅ **Deep Learning Models** - Mô hình ML dự đoán chứng chỉ hành vi  
✅ **Knowledge Base Management** - Quản lý tài liệu tư vấn  
✅ **Admin Dashboard** - Quản lý toàn bộ hệ thống  

**Kiến trúc:**
```
Frontend (HTML/JS) 
    ↓
Gateway (Nginx)
    ↓
Advisor Service (Django)
    ├─ RAG System (sentence-transformers + ChromaDB)
    ├─ ML Models (Deep Learning)
    ├─ Chat API
    └─ Analytics API
    ↓
PostgreSQL + Redis + ChromaDB
```

---

## 🔧 Yêu cầu hệ thống

### Cách 1: Sử dụng Docker (Khuyến nghị)
- Docker Desktop 4.0+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

### Cách 2: Chạy Local
- Python 3.10+
- PostgreSQL 12+
- Redis 6+
- Node.js 16+ (nếu có frontend development)
- 8GB RAM minimum

---

## ⚡ Cài đặt nhanh

### Option A: Docker Compose (Dễ nhất)

**Bước 1: Chuẩn bị**
```bash
cd /path/to/ktra1

# Copy .env file
cp advisor_service/.env.example advisor_service/.env

# Chỉnh sửa nếu cần (thay đổi DB password, OpenAI key, etc)
nano advisor_service/.env
```

**Bước 2: Khởi động services**
```bash
# Khởi động toàn bộ hệ thống
docker-compose up -d

# Kiểm tra status
docker-compose ps

# Kiểm tra advisor-service
docker-compose logs -f advisor-service
```

**Bước 3: Migration & Load KB**
```bash
# Chạy database migration
docker-compose exec advisor-service python manage.py migrate

# Tạo superuser (admin)
docker-compose exec advisor-service python manage.py createsuperuser

# Tải Knowledge Base sample
docker-compose exec advisor-service python manage.py load_kb --sample

# Kiểm tra admin
# Đăng nhập: http://localhost:8003/admin
```

**Bước 4: Kiểm tra API hoạt động**
```bash
# Test chat API
curl -X POST http://localhost:8107/api/advisor/sessions/send_message/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session",
    "message": "Laptop nào tốt cho lập trình?"
  }'

# Nếu có response → ✓ API hoạt động
```

### Option B: Chạy Local

**Bước 1: Cài đặt dependencies**
```bash
cd advisor_service

# Tạo virtual environment
python -m venv venv

# Activate
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Hoặc với GPU support
pip install -r requirements-gpu.txt
```

**Bước 2: Setup Database**
```bash
# PostgreSQL cần chạy trước
# Windows: Services → PostgreSQL
# Mac: brew services start postgresql
# Linux: sudo systemctl start postgresql

# Cấu hình .env
cp .env.example .env
nano .env

# Cấu hình DB credentials trong .env
```

**Bước 3: Migrations & Data**
```bash
# Migration
python manage.py migrate

# Superuser
python manage.py createsuperuser

# Load KB
python manage.py load_kb --sample
```

**Bước 4: Chạy server**
```bash
# Terminal 1: Django server
python manage.py runserver 0.0.0.0:8003

# Terminal 2: Celery worker (nếu có)
celery -A advisor_service worker -l info

# Terminal 3: Redis (nếu cần)
redis-server
```

---

## 🌐 Tích hợp vào website

### Phương pháp 1: Iframe (Đơn giản nhất)

Thêm vào file HTML bất kỳ (trước `</body>`):

```html
<!-- AI Advisor Chatbot -->
<iframe 
    src="/ai-advisor.html" 
    style="position: fixed; 
           right: 20px; 
           bottom: 20px; 
           width: 430px; 
           height: 600px; 
           border: none; 
           border-radius: 12px; 
           z-index: 9999;
           box-shadow: 0 5px 40px rgba(0,0,0,0.16);">
</iframe>
```

### Phương pháp 2: Script Tag (Nâng cao)

```html
<script>
  // Tự động tạo iframe
  window.AIAdvisorConfig = {
    position: 'bottom-right',
    theme: 'light',
    apiUrl: 'http://localhost:8107/api'
  };
</script>
<script src="/ai-advisor.js"></script>
```

### Phương pháp 3: React Component

```jsx
import React, { useEffect } from 'react';

export function AIAdvisorChat() {
  useEffect(() => {
    const script = document.createElement('script');
    script.src = '/ai-advisor.js';
    document.body.appendChild(script);
  }, []);

  return <div id="ai-advisor" />;
}
```

### Bước 1: Copy file frontend

```bash
# Sao chép ai-advisor.html vào frontend
cp advisor_service/frontend/ai-advisor.html gateway/frontend/
```

### Bước 2: Cấu hình nginx

Sửa `gateway/nginx.conf`:

```nginx
server {
    listen 80;
    server_name _;

    # Proxy API tới advisor-service
    location /api/advisor/ {
        proxy_pass http://advisor-service:8003/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Frontend static files
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
}
```

### Bước 3: Tích hợp vào pages

**gateway/frontend/index.html:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>E-Commerce</title>
</head>
<body>
    <!-- Nội dung website -->
    
    <!-- AI Advisor Chatbot (thêm dòng này) -->
    <iframe src="/ai-advisor.html" 
            style="position: fixed; right: 20px; bottom: 20px; width: 430px; height: 600px; border: none; border-radius: 12px; z-index: 9999;">
    </iframe>
</body>
</html>
```

### Bước 4: Reload & Test

```bash
# Reload nginx
docker-compose exec gateway nginx -s reload

# Hoặc khởi động lại
docker-compose restart gateway

# Truy cập website
# http://localhost:8100
# → Chatbot sẽ xuất hiện ở bottom-right
```

---

## 🔧 Cấu hình advanced

### 1. Sử dụng OpenAI GPT

**Bước 1: Lấy API key**
- Đăng ký: https://platform.openai.com/account/api-keys
- Copy API key

**Bước 2: Cấu hình**
```bash
# .env
OPENAI_API_KEY=sk-your-key-here
```

**Bước 3: Kích hoạt trong code**

File: `advisor/rag_system/rag_engine.py`
```python
def _call_llm(self, prompt: str) -> str:
    import openai
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # hoặc gpt-4
        messages=[
            {"role": "system", "content": "Bạn là AI advisor..."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )
    return response['choices'][0]['message']['content']
```

### 2. Sử dụng Ollama (Local LLM)

**Bước 1: Cài Ollama**
- Download: https://ollama.ai
- Chạy: `ollama serve`

**Bước 2: Pull model**
```bash
ollama pull mistral
# hoặc
ollama pull neural-chat
```

**Bước 3: Cấu hình .env**
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

### 3. Custom Knowledge Base

**Tạo file kb_custom.json:**
```json
[
  {
    "title": "Sản phẩm X - Thông tin chi tiết",
    "content": "Mô tả chi tiết về sản phẩm X, tính năng, giá cả, etc...",
    "content_type": "product",
    "tags": ["product", "x", "laptop"],
    "is_active": true
  },
  {
    "title": "Cách sử dụng sản phẩm X",
    "content": "Hướng dẫn từng bước sử dụng sản phẩm X...",
    "content_type": "guide",
    "tags": ["guide", "x"],
    "is_active": true
  }
]
```

**Tải KB:**
```bash
python manage.py load_kb --file kb_custom.json
```

### 4. Training Behavior Model

**Chuẩn bị dữ liệu:** `training_data.csv`
```csv
total_purchases,avg_spending,segment
10,20000000,VIP
5,15000000,High-Value
2,5000000,Regular
0,0,New
```

**Training script:** `train_model.py`
```python
from advisor.ml_models.behavior_classifier import BehaviorClassifier
import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('training_data.csv')
X = df[['total_purchases', 'avg_spending']].values
y = df['segment'].values

# Train
classifier = BehaviorClassifier()
classifier.train(X, y)
print("✓ Model trained successfully!")
```

**Chạy:**
```bash
python train_model.py
```

---

## 📊 Admin Dashboard

Truy cập: http://localhost:8003/admin

**Quản lý:**
- 📝 Knowledge Base documents
- 💬 Chat sessions & messages
- 👥 Customer profiles
- 📈 Behavior analysis logs

**Tạo superuser:**
```bash
docker-compose exec advisor-service python manage.py createsuperuser
```

---

## 🐛 Troubleshooting

### ❌ Lỗi: "Connection refused"

```bash
# Kiểm tra services đang chạy
docker-compose ps

# Kiểm tra logs
docker-compose logs advisor-service

# Khởi động lại
docker-compose restart advisor-service
```

### ❌ Lỗi: "Database connection failed"

```bash
# Kiểm tra PostgreSQL
docker-compose logs advisor-db

# Reset database (cẩn thận!)
docker volume rm ktra1_advisor_db_data
docker-compose up -d advisor-db
```

### ❌ Lỗi: "ChromaDB not found"

```bash
# Xóa cache
rm -rf advisor_service/chroma_db/

# Load KB lại
docker-compose exec advisor-service python manage.py load_kb --sample
```

### ❌ Lỗi: "Embedding model not found"

```bash
# Download model (lần đầu chạy sẽ tự động)
# Hoặc cài đặt thủ công:

python -c "from sentence_transformers import SentenceTransformer; \
    SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')"
```

### ❌ Chatbot không xuất hiện trên website

```bash
# 1. Kiểm tra file ai-advisor.html có tồn tại
docker-compose exec gateway ls /usr/share/nginx/html/

# 2. Kiểm tra API endpoint hoạt động
curl http://localhost:8107/api/advisor/sessions/send_message/

# 3. Kiểm tra console (F12) trên browser có lỗi gì
```

### ❌ Lỗi CORS

**Sửa:** `advisor_service/settings.py`
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8100",  # Gateway
    "http://localhost:3000",  # Frontend dev
    "http://localhost:8000",  # Any
]
```

---

## 📈 Performance Optimization

### 1. Tăng tốc độ embedding (GPU)

```bash
# Cài PyTorch GPU version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Hoặc TensorFlow GPU
pip install tensorflow[and-cuda]
```

### 2. Tăng cache

Sửa `.env`:
```env
REDIS_URL=redis://redis:6379/0
CACHE_TIMEOUT=3600
```

### 3. Scale Celery workers

```bash
# Chạy multiple workers
celery -A advisor_service worker -c 4 -l info
```

---

## 🔐 Security Checklist

- [ ] Đổi `DJANGO_SECRET_KEY` thành key ngẫu nhiên
- [ ] Đặt `DEBUG=False` trong production
- [ ] Cấu hình HTTPS/SSL
- [ ] Cấu hình database password mạnh
- [ ] Bật CORS chỉ cho domain cần thiết
- [ ] Cấu hình firewall
- [ ] Cấu hình backup database

---

## 📞 Support

Gặp vấn đề?

1. Kiểm tra logs: `docker-compose logs advisor-service`
2. Đọc README: `advisor_service/README.md`
3. Test API: Sử dụng Postman/curl
4. Liên hệ: support@ecommerce.vn

---

## ✅ Checklist Hoàn thành

- [x] Cài đặt advisor-service
- [x] Cấu hình database
- [x] Tải Knowledge Base
- [x] Tích hợp chatbot vào website
- [x] Test API
- [x] Test chatbot on website
- [x] Cấu hình CORS
- [x] Deploy to production (optional)

**🎉 Hoàn tất! AI Advisor đã sẵn sàng sử dụng!**

---

**Phiên bản:** 1.0.0   
**Cập nhật:** 2024  
**Trạng thái:** ✅ Production Ready
