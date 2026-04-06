from django.core.management.base import BaseCommand
from django.conf import settings
import requests
from advisor.models import KnowledgeBase
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Load knowledge base from product databases (laptops & mobiles)"

    def add_arguments(self, parser):
        parser.add_argument('--fresh', action='store_true', help='Delete existing KB first')

    def handle(self, *args, **options):
        if options['fresh']:
            KnowledgeBase.objects.all().delete()
            self.stdout.write(self.style.WARNING('Deleted existing KB'))

        # Load laptops
        self.load_laptops()
        
        # Load mobiles
        self.load_mobiles()
        
        # Create price range documents
        self.create_price_guides()
        
        # Create recommendation docs
        self.create_recommendations()
        
        self.stdout.write(self.style.SUCCESS('✅ KB loaded successfully!'))

    def load_laptops(self):
        """Load laptop products to KB via API"""
        try:
            # Get laptops from laptop-service API
            url = 'http://laptop-service:8000/api/laptops/'
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            laptops = response.json()
            if isinstance(laptops, dict) and 'results' in laptops:
                laptops = laptops['results']
            
            if not isinstance(laptops, list):
                laptops = [laptops]
            
            for laptop in laptops:
                name = laptop.get('name', 'Unknown')
                brand = laptop.get('brand', 'Unknown')
                price = float(laptop.get('price', 0)) if laptop.get('price') else 0
                specs = laptop.get('specs', '')
                stock = laptop.get('stock', 0)
                
                content = f"""
Laptop: {name}
Brand: {brand}
Price: {price:,.0f}đ
Specs: {specs}
Available Stock: {stock} units

Product Details:
This {brand} laptop offers excellent value and performance.

Specifications:
{specs}

Pricing: {price:,.0f}đ

Inventory Status: {stock} units in stock

This is an excellent choice for various computing needs depending on the specifications.
"""
                
                title = f"{brand} {name}"
                
                kb, created = KnowledgeBase.objects.update_or_create(
                    title=title,
                    defaults={
                        'content': content.strip(),
                        'content_type': 'product',
                        'tags': ['laptop', brand.lower(), 'product'],
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(f'✅ Created KB: {title}')
                else:
                    self.stdout.write(f'⟳ Updated KB: {title}')
                    
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.WARNING(f'Could not load laptops from API: {str(e)}'))

    def load_mobiles(self):
        """Load mobile products to KB via API"""
        try:
            # Get mobiles from mobile-service API
            url = 'http://mobile-service:8000/api/mobiles/'
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            mobiles = response.json()
            if isinstance(mobiles, dict) and 'results' in mobiles:
                mobiles = mobiles['results']
            
            if not isinstance(mobiles, list):
                mobiles = [mobiles]
            
            for mobile in mobiles:
                name = mobile.get('name', 'Unknown')
                brand = mobile.get('brand', 'Unknown')
                price = float(mobile.get('price', 0)) if mobile.get('price') else 0
                specs = mobile.get('specs', '')
                stock = mobile.get('stock', 0)
                
                content = f"""
Mobile Phone: {name}
Brand: {brand}
Price: {price:,.0f}đ
Specs: {specs}
Available Stock: {stock} units

Product Details:
{name} by {brand} is a feature-rich mobile device.

Specifications:
{specs}

Pricing: {price:,.0f}đ

Inventory: {stock} units available

Features:
- Latest technology
- Excellent performance
- Great camera quality
- Reliable battery life
- Good for daily use and professional tasks

This is a great choice for mobile phone users looking for quality and affordability.
"""
                
                title = f"{brand} {name}"
                
                kb, created = KnowledgeBase.objects.update_or_create(
                    title=title,
                    defaults={
                        'content': content.strip(),
                        'content_type': 'product',
                        'tags': ['mobile', 'phone', brand.lower(), 'product'],
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(f'✅ Created KB: {title}')
                else:
                    self.stdout.write(f'⟳ Updated KB: {title}')
                    
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.WARNING(f'Could not load mobiles from API: {str(e)}'))

    def create_price_guides(self):
        """Create price range guides"""
        price_guides = [
            {
                'title': 'Laptop dưới 15 triệu - Phù hợp cho Students',
                'content': '''Các laptop dưới 15 triệu đồng là lựa chọn hoàn hảo cho sinh viên và người mới bắt đầu.

Các sản phẩm phổ biến:
- Acer Aspire 5
- ASUS Vivobook 15
- Realme Book Prime

Ưu điểm:
✓ Giá cả phải chăng
✓ Đủ xử lý cho công việc văn phòng
✓ Pin tốt, trọng lượng vừa phải
✓ Có hỗ trợ bảo hành

Nhược điểm:
- Hiệu suất không cao cho gaming
- RAM thường 8GB
- SSD 512GB

Phù hợp cho:
- Viết tài liệu, duyệt web, xem phim
- Học lập trình cơ bản
- Công việc văn phòng hàng ngày

Khuyến nghị: Nâng cấp lên 16GB RAM nếu có thể''',
                'tags': ['price-guide', 'budget', 'laptop', 'student']
            },
            {
                'title': 'Laptop 15-25 triệu - Hiệu suất cân bằng',
                'content': '''Dải giá 15-25 triệu là "vàng" cho hầu hết người dùng bình thường.

Các sản phẩm nổi bật:
- Lenovo IdeaPad 5 Pro
- HP Pavilion 15
- ASUS TUF Gaming A15
- Dell G15

Cấu hình thường:
✓ Intel Core i7 / AMD Ryzen 7
✓ 16GB RAM (DDR5)
✓ 512GB SSD NVMe
✓ Màn hình 15.6" 144Hz+

Ưu điểm:
- Cân bằng giữa hiệu suất và giá
- Xử lý tốt hầu hết tác vụ
- Chơi game mức vừa
- Dựng phim, edit ảnh okee

Nhược điểm:
- Nặng hơn ultrabook
- Không có GPU riêng (ngoại trừ gaming)

Phù hợp cho:
- Lập trình viên chuyên nghiệp
- Designer, content creator
- Gaming giải trí
- Công việc văn phòng heavy''',
                'tags': ['price-guide', 'mid-range', 'laptop', 'developer']
            },
            {
                'title': 'Laptop 25-40 triệu - Gaming & Performance',
                'content': '''Giá 25-40 triệu mở ra thế giới gaming và xử lý nặng.

Các sản phẩm hàng đầu:
- ASUS ROG Strix G16
- MSI Stealth GS77
- Razer Blade 15 Studio
- Dell Alienware m16

Cấu hình cao:
✓ RTX 4060/4070 trở lên
✓ Intel i7-13th hoặc i9
✓ 32GB RAM
✓ 1TB SSD
✓ Tản nhiệt cao cấp

Ưu điểm:
- Gaming trên High/Ultra
- Render, compile cực nhanh
- Video editing 4K ok
- Performance chạy max

Nhược điểm:
- Nặng (2-2.5kg)
- Pin chỉ 3-4 tiếng
- Tạo tiếng ồn khi tải nặng

Phù hợp cho:
- Gamer chuyên nghiệp
- Video/3D artist
- VFX specialist
- Lập trình AI/ML''',
                'tags': ['price-guide', 'gaming', 'laptop', 'performance']
            },
            {
                'title': 'Laptop cao cấp 40-60 triệu - Đỉnh cao công nghệ',
                'content': '''Dải giá 40-60 triệu là top tier của thị trường laptop.

Các sản phẩm xa xỉ:
- MacBook Pro M3 Max 16"
- Dell XPS 13 Plus (OLED)
- ThinkPad X1 Carbon Gen 12
- HP Spectre x360 16

Công nghệ đỉnh:
✓ Chip M3 Max hoặc Intel Core i9
✓ 32-36GB unified/LPDDR5 memory
✓ 1TB SSD
✓ Màn hình OLED/Retina
✓ Thiết kế cao cấp

Ưu điểm:
- Hiệu suất cực đỉnh
- Thiết kế siêu đẹp
- Chất lượng xây dựng tuyệt vời
- Bảo hành 3 năm+
- Giá trị bảo toàn cao

Nhược điểm:
- Giá rất cao
- Không thể nâng cấp phần cứng
- Một số bị khóa ecosystem

Phù hợp cho:
- Chuyên gia hàng đầu
- CEO/Boss chứng khoán
- Filmmaker Hollywood
- Researchers, Scientists''',
                'tags': ['price-guide', 'premium', 'laptop', 'luxury']
            },
            {
                'title': 'Điện thoại dưới 10 triệu - Đủ dùng lâu năm',
                'content': '''Smartphone dưới 10 triệu vẫn rất tốt cho người dùng bình thường.

Các sản phẩm tốt:
- vivo Y36
- Xiaomi Redmi Note 12
- Realme C35
- Nothing Phone 2a

Cấu hình cơ bản:
✓ RAM 4-6GB
✓ Storage 128GB
✓ Pin 5000+ mAh
✓ Camera 50MP+
✓ 6.5" display

Ưu điểm:
- Giá cực rẻ
- Camera vẫn ok
- Pin chạy cả ngày
- Brand uy tín
- Hỗ trợ bảo hành tốt

Nhược điểm:
- Hiệu suất không cao
- Không tập chạy game nặng
- Update OS hạn chế

Phù hợp cho:
- Người dùng thông thường
- Bố mẹ, ông bà
- Sinh viên tiết kiệm
- Dân công nhân''',
                'tags': ['price-guide', 'budget', 'mobile', 'affordable']
            },
            {
                'title': 'Điện thoại 10-15 triệu - Cách mạng chất lượng',
                'content': '''Dải 10-15 triệu mang lại bước nhảy lớn trong chất lượng camera và hiệu suất.

Các sản phẩm hot:
- Samsung Galaxy A54
- vivo V30
- Xiaomi 14
- Motorola Edge 50

Cấu hình tốt:
✓ Snapdragon 7-8 Gen
✓ 8-12GB RAM
✓ 256GB Storage
✓ Camera 48-64MP
✓ Màn hình AMOLED 120Hz

Ưu điểm:
- Camera chất lượng cao
- Hiệu suất chạy game ok
- Màn hình sắc nét
- Sạc nhanh 30W+
- Thời lượng pin tốt

Nhược điểm:
- Có thể lâu hơn update
- Warranty 1-2 năm

Phù hợp cho:
- Dân chụp ảnh
- Gamer mobile casual
- Content creator TikTok
- Người dùng nâng cấp''',
                'tags': ['price-guide', 'mid-range', 'mobile', 'camera']
            },
            {
                'title': 'Premium Mobile 20-30 triệu - Flagship thường niên',
                'content': '''Smartphone 20-30 triệu là flagship của các hãng năm nay.

Các sản phẩm hàng đầu:
- iPhone 15 / iPhone 15 Pro
- Samsung Galaxy S24 / S24+
- Xiaomi 14 Ultra
- Google Pixel 8 Pro

Công nghệ xinh đẹp:
✓ Chip flagship (A17 Pro, SD 8 Gen 3)
✓ Camera AI tiên tiến
✓ Màn hình 120Hz AMOLED
✓ Thiết kế sang trọng
✓ Sạc nhanh 65W+

Ưu điểm:
- Camera chuyên nghiệp
- Hiệu suất cực nhanh
- 3-5 năm update
- AI features nâng cao
- Giá trị bảo toàn cao

Nhược điểm:
- Investment lớn
- Thường lock ecosystem

Phù hợp cho:
- Chuyên gia công nghệ
- Photographer mobile
- Người toàn smartphone
- Business executive''',
                'tags': ['price-guide', 'flagship', 'mobile', 'premium']
            },
            {
                'title': 'Điện thoại gập - Tương lai công nghệ',
                'content': '''Smartphone gập đại diện tương lai công nghệ di động.

Các sản phẩm gập:
- Samsung Galaxy Z Flip5 (22.99M)
- Samsung Galaxy Z Fold5 (37.99M)
- Motorola Razr 40 (21.99M)

Ưu điểm gập:
✓ Thiết kế futuristic
✓ Kích thước rút gọn nhỏ
✓ Hạn chế bị rơi
✓ Selfie với hai camera
✓ Màn hình rộng khi mở

Nhược điểm:
- Giá rất cao
- Tuổi thọ màn hình hạn chế
- Phức tạp hơn khi sử dụng
- Hỏng dễ nếu không cẩn thận

Phù hợp cho:
- Tech enthusiast
- Người đặt biệt tính cách
- Business người bận
- YouTuber tech reviewer''',
                'tags': ['price-guide', 'foldable', 'mobile', 'innovation']
            },
        ]
        
        for guide in price_guides:
            kb, created = KnowledgeBase.objects.update_or_create(
                title=guide['title'],
                defaults={
                    'content': guide['content'],
                    'content_type': 'guide',
                    'tags': guide['tags'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'✅ Created guide: {guide["title"]}')


    def create_recommendations(self):
        """Create recommendation documents"""
        recommendations = [
            {
                'title': 'Laptop Recommendations by Use Case - Chi tiết',
                'content': '''HƯỚNG DẪN CHỌN LAPTOP THEO NHU CẦU THỰC TẾ:

👨‍🎓 CHO SINH VIÊN & HỌC SINH:
Budget: 14-18 triệu
Sản phẩm: Acer Aspire 5, HP 15s, ASUS Vivobook
Lý do: Đủ xử lý lập trình cơ bản, văn bản, browsing
Không cần: GPU mạnh, RAM cực cao

💼 CHO LẬP TRÌNH VIÊN:
Budget: 20-30 triệu
Sản phẩm: Lenovo IdeaPad 5, ThinkPad X1, Dell Inspiron
Lý do: CPU nhanh, RAM 16GB, bàn phím tốt
Không cần: Gaming high-end

🎨 CHO DESIGNER/VIDEO EDITOR:
Budget: 28-40 triệu
Sản phẩm: ASUS ZenBook, MacBook Air M3, Dell XPS
Lý do: Màn hình color-accurate, RAM 16GB+, SSD nhanh
Không cần: Gaming card (ngoài nếu VFX)

🎮 CHO GAMER:
Budget: 25-35 triệu
Sản phẩm: ASUS ROG, MSI Stealth, Dell G15
Lý do: RTX 4060+, CPU mạnh, 165Hz display
Cần: Tản nhiệt tốt

💎 CHO PROFESSIONAL HÀNG ĐẦU:
Budget: 40-60 triệu
Sản phẩm: MacBook Pro M3 Max, ThinkPad X1 Carbon, XPS 13 Plus
Lý do: Performance cực đỉnh, thiết kế, bảo hành
Đặc biệt: Thay nên M3 Max cho 3D/AI

🔧 CHO LẬP TRÌNH NHÚNG/IOT:
Budget: 18-25 triệu
Sản phẩm: ThinkPad, System76 Lemur, Framework
Lý do: Dễ nâng cấp, cộng đồng developer
Linux-friendly preferred

🛡️ CHO CÔNG VIỆC CỬC NHẠY:
Budget: 28-40 triệu
Sản phẩm: Purism Librem, System76, Lenovo ThinkPad
Lý do: Bảo mật cao, privacy-focused
Upgrade: Kill switch camera, TPM chip

⚡ CHO NOMAD / NGƯỜI BẬN:
Budget: 35-45 triệu
Sản phẩm: MacBook Air, Dell XPS 13, ThinkPad X1
Lý do: Nhẹ <1.4kg, pin 15h+, thiết kế sang
Ưu tiên: Cổng USB-C, sạc nhanh''',
                'tags': ['recommendation', 'laptop', 'guide', 'use-case']
            },
            {
                'title': 'Mobile Phone Selection Guide - Toàn tập',
                'content': '''HƯỚNG DẪN CHỌN SMARTPHONE THÔNG MINH:

👶 CHO BỐ MẸ & ONG BÀ:
Budget: 5-7 triệu VND
Sản phẩm: vivo Y36, Xiaomi Redmi Note 12
Tính năng: Gọi, SMS, WhatsApp, Facebook
Ưu tiên: Pin xịn, màn hình lớn, chữ lớn

🎓 CHO SINH VIÊN:
Budget: 7-12 triệu VND
Sản phẩm: Xiaomi 14, vivo V30, Nothing Phone 2a
Tính năng: Gaming casual, Instagram, TikTok
Ưu tiên: Pin tốt, camera ok, giá hợp lý

💼 CHO OFFICE/BUSINESS:
Budget: 15-20 triệu VND
Sản phẩm: Samsung Galaxy A54, Motorola Edge 50, OnePlus 12
Tính năng: Email fast, meeting zoom, productivity
Ưu tiên: Bàn phím digital, security, vân tay nhanh

📸 CHO CHUYÊN CHỤP ẢNH:
Budget: 20-30 triệu VND
Sản phẩm: iPhone 15 Pro, Samsung S24 Ultra, Xiaomi 14 Ultra
Tính năng: Camera telephoto, night mode, AI edit
Ưu tiên: Sensor lớn, pixel 1µm+, zoom optik

🎮 CHO GAMER MOBILE:
Budget: 12-20 triệu VND
Sản phẩm: ASUS ROG Phone 8, Xiaomi Black Shark, OnePlus 12
Tính năng: 120Hz+ AMOLED, CPU flagship, RGB
Ưu tiên: Cooling system, 165Hz, haptics

🎬 CHO CONTENT CREATOR:
Budget: 22-32 triệu VND
Sản phẩm: iPhone 15 Pro Max, Samsung S24 Ultra, Xiaomi 14 Ultra
Tính năng: 8K video, stereo mic, gimbal-friendly

📱 CHO APPLE ECOSYSTEM:
Budget: 21-40 triệu VND
Sản phẩm: iPhone 15 / Pro / Pro Max
Tính năng: iCloud sync, AirDrop, seamless MacBook
Ưu tiên: A17 Pro chip, ProRAW video, Spatial Video

🌟 CHO NGƯỜI THÍCH CÔNG NGHỆ MỚI:
Budget: 22-38 triệu VND
Sản phẩm: Samsung Z Flip5, Motorola Razr 40
Tính năng: Gập lại, outer screen, unique design
Ưu tiên: Độ bền, bản lề, warranty

🏆 CHO FLAGSHIP ENTHUSIAST:
Budget: 27-35 triệu VND
Sản phẩm: iPhone 15 Pro, Samsung S24 Ultra, Google Pixel 8 Pro
Tính năng: Xử lý ảnh AI, 200MP sensor, zoom 10x
Ưu tiên: Best in class everything''',
                'tags': ['recommendation', 'mobile', 'guide', 'use-case', 'selection']
            },
            {
                'title': 'So sánh Brand & Ecosystem - Chọn brand nào?',
                'content': '''PHÂN TÍCH BRAND SMARTPHONE & LAPTOP:

🍎 APPLE ECOSYSTEM:
iPhone: Premium, camera cực tốt, ecosystem đóng
MacBook: Hiệu suất M3 tuyệt vời, pin siêu dài
Ưu: Seamless sync, resale tốt, privacy
Nhược: Giá cao, không tùy chỉnh

📱 SAMSUNG GALAXY:
Điện thoại: Flagship cân bằng, foldable innovative
Máy tính: Không sản xuất laptop mainstream
Ưu: Màn hình AMOLED tốt nhất, giá diverse
Nhược: OneUI có cách lạ, upgrade hạn chế

🔴 XIAOMI (VALUE KING):
Điện thoại: Giá tốt, cấu hình cao, camera AI
Máy tính: Thêm dòng gaming laptop RedmiBook
Ưu: Giá cực rẻ, MIUI cá nhân hóa
Nhược: Privacy concerns, warranty phức tạp

🔵 INTEL & AMD (Laptop):
Intel: Phổ biến, driver tốt, power 8 Gen series
AMD Ryzen: Hiệu năng tốt, giá cân bằng
Ưu: Ecosystem lớn, tùy chỉnh cao
Nhược: Heat, battery khác nhau

💻 THINKPAD (Enterprise):
Bàn phím tốt nhất, build quality chắc, warranty tốt
Ưu: Lâu dài, dễ sửa, corporate support
Nhược: Design bảo thủ, giá premium

🎮 GAMING BRANDS:
ASUS ROG: Performance cao, RGB cực
MSI: Stealth series sang, thermal tốt
Razer: Design siêu đẹp, giá cao nhất
Alienware: Legend, brand gaming, service ok

⚡ GIẢI QUYẾT NHANH:
Muốn MacOS & iPhone đồng bộ? → Apple
Muốn Android + tự do? → Samsung hoặc Xiaomi
Muốn lập trình, Linux? → ThinkPad + Android flagship
Muốn gaming? → ROG hoặc MSI + gaming phone
Muốn tiết kiệm? → Xiaomi hoặc Realme''',
                'tags': ['comparison', 'brand', 'ecosystem', 'guide']
            },
            {
                'title': 'Trend Công Nghệ 2026 - Cái gì đang hot?',
                'content': '''TOP TREND CÔNG NGHỆ 2026:

🤖 AI CHIP EVERYWHERE:
- Apple A17 Pro tích hợp AI features
- Snapdragon 8 Gen 3 có NPU chuyên AI
- Intel Core Ultra có xPU riêng
→ Kết quả: Xử lý ảnh/video local, không cần cloud

📱 FOLDABLE MAINSTREAM:
- Samsung Flip & Fold phiên bản 6
- Motorola Razr gen 3 cắt giảm giá
- Huawei Mate X6 sắp ra
→ Kết quả: Gập từng bước trở thành standard

🔋 BATTERY MEGADAY:
- Smartphone pin 6000-7000mAh thường
- Laptop pin 100Wh chuẩn quy
→ Kết quả: Không cần sạc 2-3 ngày

⚡ FAST CHARGING 100W+:
- iPhone bắt buộc USB-C 45W
- Samsung 65W, Xiaomi 120W
→ Kết quả: Từ 0-100% chỉ 20-30 phút

📷 PERISCOPE ZOOM:
- Telescope lens 10x+ optical
- 200MP ultra resolution sensors
→ Kết quả: DSLR quality từ điện thoại

💾 SOLID STATE STORAGE:
- SSD giá rẻ, lưu trữ 2TB phổ biến
- Cloud tích hợp sẵn
→ Kết quả: Dữ liệu an toàn, sync real-time

🎮 GAMING FRAME 240Hz:
- Smartphone 240Hz AMOLED
- Laptop 360Hz mini-LED
→ Kết quả: Trơn tượt tuyệt đối

🔐 PRIVACY BY DEFAULT:
- End-to-end encryption standard
- On-device AI (không upload cloud)
→ Kết quả: Privacy là tính năng premium

✅ KHI MUA HÔM NAY LƯU Ý:
1. Chọn chip mới gen (A17, SD 8 Gen 3, Ultra 7)
2. Min 128GB SSD, 8GB RAM smartphone, 16GB laptop
3. Xem warranty của brand, hỗ trợ bao lâu
4. Kiểm tra giá hàng chính hãng vs gray market
5. Nên chờ Q2 để có sale hoặc mẫu mới''',
                'tags': ['trend', 'technology', '2026', 'innovation']
            },
        ]
        
        for rec in recommendations:
            kb, created = KnowledgeBase.objects.update_or_create(
                title=rec['title'],
                defaults={
                    'content': rec['content'],
                    'content_type': 'recommendation',
                    'tags': rec['tags'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'✅ Created recommendation: {rec["title"]}')
