"""
Management command: Load initial Knowledge Base
Dùng để load dữ liệu KB ban đầu từ file JSON hoặc database khác
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from advisor.models import KnowledgeBase
from advisor.rag_system.rag_engine import RAGEngine
import json
import os


class Command(BaseCommand):
    help = 'Tải dữ liệu Knowledge Base từ file hoặc tạo mẫu'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Đường dẫn file JSON chứa KB documents',
        )
        parser.add_argument(
            '--sample',
            action='store_true',
            help='Tạo dữ liệu sample KB',
        )
    
    def handle(self, *args, **options):
        if options['sample']:
            self.create_sample_kb()
        elif options['file']:
            self.load_kb_from_file(options['file'])
        else:
            self.stdout.write(self.style.WARNING('Please provide --file or --sample'))
    
    def create_sample_kb(self):
        """Tạo Knowledge Base sample"""
        self.stdout.write("Creating sample Knowledge Base...")
        
        sample_docs = [
            {
                'title': 'MacBook Air M3 - Thông tin sản phẩm',
                'content': '''MacBook Air M3 là laptop mỏng nhẹ cao cấp của Apple.
Đặc điểm nổi bật:
- Bộ xử lý Apple M3 hiệu suất cao
- RAM: 8GB/16GB/24GB tùy chọn
- SSD: 256GB-2TB
- Màn hình Retina 13.6", độ phân giải 2560x1600
- Pin: Kéo dài 18 giờ
- Trọng lượng: 1.2kg
- Hệ điều hành: macOS Sonoma mới nhất
Giá: 28.900.000 VND

Hoàn hảo cho:
- Designer, video editor
- Lập trình viên
- Sinh viên
- Dân văn phòng

Bảo hành: 12 tháng
''',
                'content_type': 'product',
                'metadata': {
                    'product_id': 1,
                    'brand': 'Apple',
                    'price_vnd': 28900000,
                    'category': 'laptop'
                }
            },
            {
                'title': 'ThinkPad X1 Carbon - Laptop doanh nhân',
                'content': '''ThinkPad X1 Carbon là laptop chuyên nghiệp cho công sở.
Thông số:
- CPU: Intel Core i5/i7 gen 13
- RAM: 16GB/32GB DDR5
- SSD: 512GB-1TB PCIe 4.0
- Màn hình: 14.2" 2.8K OLED, 100% DCI-P3
- Pin: 65Wh, 15+ giờ
- Trọng lượng: 1.18kg
- OS: Windows 11 Pro
Giá: 32.000.000 VND

Ưu điểm:
- Bàn phím tuyệt vời
- Bảo mật cao cấp (TPM 2.0, fingerprint)
- Kết nối: Thunderbolt 4, USB-C
- Hiệu năng ổn định

Bảo hành: 12 tháng
''',
                'content_type': 'product',
                'metadata': {
                    'product_id': 2,
                    'brand': 'ThinkPad',
                    'price_vnd': 32000000,
                    'category': 'laptop'
                }
            },
            {
                'title': 'iPhone 16 - Điện thoại thông minh',
                'content': '''iPhone 16 phiên bản mới của Apple.
Thông số:
- Chip: A18 Bionic
- Màn hình: 6.1" Super Retina XDR
- Camera: 48MP sau, 12MP trước
- Pin: 3,500mAh, 22h pin
- Hỗ trợ 5G
- OS: iOS 18
- Kháng nước: IP69

Giá: 25.900.000 VND

Camera:
- Ultra-wide & Tele lens
- Night mode cải tiến
- 4K video 120fps
- Tính năng AI mới

Bảo hành: 12 tháng
''',
                'content_type': 'product',
                'metadata': {
                    'product_id': 3,
                    'brand': 'Apple',
                    'price_vnd': 25900000,
                    'category': 'mobile'
                }
            },
            {
                'title': 'Chính sách bảo hành & đổi trả',
                'content': '''Chính sách bảo hành & đổi trả của cửa hàng:

BẢNG BẢO HÀNH:
- Sản phẩm: 12 tháng bảo hành từ ngày mua
- Lỗi do sản xuất: Miễn phí sửa/thay
- Hư hỏng do người dùng: Tính phí sửa chữa

ĐIỀU KIỆN ĐỔI TRẢ:
- Tối đa 30 ngày đổi sản phẩm khác
- Sản phẩm không dùng, vẫn đầy đủ hộp
- Không được cạo ngoặc ba gạch
- Không được sửa chữa bên ngoài

HOÀN TIỀN:
- 30 ngày hoàn tiền 100% nếu lỗi cửa hàng
- Phí vận chuyển không hoàn
- Sau 30 ngày có thể đổi/sửa

LIÊN HỆ:
- Email: support@ecommerce.vn
- Hotline: 1900-xxxx
- Chat: Trong giờ 8h-22h hàng ngày
''',
                'content_type': 'policy',
                'metadata': {
                    'policy_type': 'warranty',
                }
            },
            {
                'title': 'So sánh MacBook Air M3 vs ThinkPad X1',
                'content': '''So sánh chi tiết hai laptop cao cấp:

╔════════════════════╦══════════════════╦═════════════════╗
║ Tiêu chí           ║ MacBook Air M3   ║ ThinkPad X1     ║
╠════════════════════╬══════════════════╬═════════════════╣
║ CPU                ║ Apple M3         ║ Intel Core i7   ║
║ RAM                ║ 8-24GB           ║ 16-32GB         ║
║ SSD                ║ 256GB-2TB        ║ 512GB-1TB       ║
║ Màn hình           ║ Retina 13.6"     ║ OLED 14.2"      ║
║ Pin                ║ 18 giờ Longest   ║ 15+ giờ         ║
║ Trọng lượng        ║ 1.2kg            ║ 1.18kg          ║
║ Hệ điều hành       ║ macOS Sonoma     ║ Windows 11 Pro  ║
║ Giá                ║ 28,9M VND        ║ 32M VND         ║
╚════════════════════╩══════════════════╩═════════════════╝

Chọn MacBook Air M3 nếu:
- Bạn sử dụng ekosystem Apple
- Cần pin càng lâu càng tốt
- Thích thiết kế mỏng nhẹ
- Là designer/video editor

Chọn ThinkPad X1 nếu:
- Là dân văn phòng/code Windows
- Cần màn hình OLED tuyệt vời
- Thích bàn phím tốt
- Đây là máy được dùng từ lâu
''',
                'content_type': 'comparison',
                'metadata': {
                    'products': ['MacBook Air M3', 'ThinkPad X1'],
                }
            },
        ]
        
        for doc in sample_docs:
            kb, created = KnowledgeBase.objects.get_or_create(
                title=doc['title'],
                defaults={
                    'content': doc['content'],
                    'content_type': doc['content_type'],
                    'tags': list(doc['metadata'].keys()),
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Created: {doc['title']}"))
            else:
                self.stdout.write(self.style.WARNING(f"- Already exists: {doc['title']}"))
        
        # Cập nhật RAG engine
        self.stdout.write("Updating RAG engine...")
        rag_engine = RAGEngine()
        rag_engine.update_kb_from_db()
        
        self.stdout.write(self.style.SUCCESS("✓ Knowledge Base loaded successfully!"))
    
    def load_kb_from_file(self, file_path):
        """Tải KB từ file JSON"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        self.stdout.write(f"Loading {len(documents)} documents...")
        
        for doc in documents:
            kb, created = KnowledgeBase.objects.get_or_create(
                title=doc.get('title'),
                defaults={
                    'content': doc.get('content', ''),
                    'content_type': doc.get('content_type', 'other'),
                    'tags': doc.get('tags', []),
                    'is_active': doc.get('is_active', True),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Created: {doc.get('title')}"))
        
        rag_engine = RAGEngine()
        rag_engine.update_kb_from_db()
        self.stdout.write(self.style.SUCCESS("✓ KB loaded successfully!"))
