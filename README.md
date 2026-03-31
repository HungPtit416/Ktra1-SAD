# Hệ Thống Thương Mại Điện Tử Microservices Với Django

Workspace này chứa kiến trúc microservices hoàn chỉnh, đã được Docker hóa cho một nền tảng thương mại điện tử.

## Danh sách service

- customer-service (Django + DRF + JWT + MySQL)
- staff-service (Django + DRF + JWT + MySQL)
- laptop-service (Django + DRF + PostgreSQL)
- mobile-service (Django + DRF + PostgreSQL)
- gateway (API gateway dùng Nginx)

## Frontend tập trung

- Toàn bộ giao diện đã tập trung tại gateway trong thư mục `gateway/frontend/`.
- Các trang UI được phục vụ trực tiếp bởi Nginx.
- Frontend gọi API qua gateway tới các service backend.

## Cấu trúc dự án

```text
.
├── gateway/
│   └── nginx.conf
├── customer_service/
│   ├── customer_service/
│   ├── customers/
│   ├── carts/
│   ├── templates/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env
│   └── .env.example
├── staff_service/
│   ├── staff_service/
│   ├── staffops/
│   ├── templates/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env
│   └── .env.example
├── laptop_service/
│   ├── laptop_service/
│   ├── laptops/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env
│   └── .env.example
├── mobile_service/
│   ├── mobile_service/
│   ├── mobiles/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env
│   └── .env.example
└── docker-compose.yml
```

## Tính năng đã triển khai

### customer-service
- Đăng ký và đăng nhập bằng JWT
- Tìm kiếm sản phẩm từ laptop-service và mobile-service
- Tạo giỏ hàng
- Thêm/xóa sản phẩm trong giỏ hàng
- Xem danh sách giỏ hàng
- Giao diện khách hàng đầy đủ tập trung tại gateway frontend:
	- Home (listing + pagination)
	- Login
	- Register
	- Product detail
	- Cart (update/remove/total)

### staff-service
- Đăng nhập nhân viên bằng JWT
- Dashboard API để xem danh sách sản phẩm
- Thêm sản phẩm (proxy sang laptop-service/mobile-service)
- Cập nhật sản phẩm
- Xóa sản phẩm
- Giao diện nhân viên đầy đủ tập trung tại gateway frontend:
	- Staff login
	- Dashboard (sidebar + topbar)
	- Product management table
	- Add/Edit/Delete product form

### laptop-service
- CRUD đầy đủ cho sản phẩm laptop
- Trường dữ liệu: id, name, price, brand, specs, stock

### mobile-service
- CRUD đầy đủ cho sản phẩm mobile
- Trường dữ liệu: id, name, price, brand, specs, stock

## Định tuyến API Gateway

Gateway được mở trên cổng 8100:

- /customer/* -> customer-service
- /staff/* -> staff-service
- /laptops -> danh sách laptop-service
- /mobiles -> danh sách mobile-service

Ví dụ:

- Frontend Home: http://localhost:8100/
- Customer UI: http://localhost:8100/customer-ui/
- Customer Login: http://localhost:8100/customer-ui/login/
- Customer Register: http://localhost:8100/customer-ui/register/
- Customer Cart: http://localhost:8100/customer-ui/cart/
- Staff Login: http://localhost:8100/staff-ui/login/
- Staff Dashboard: http://localhost:8100/staff-ui/
- Staff Product Form: http://localhost:8100/staff-ui/products/form/

UI routes chi tiết:

- Customer Home: http://localhost:8100/customer-ui/
- Customer Login: http://localhost:8100/customer-ui/login/
- Customer Register: http://localhost:8100/customer-ui/register/
- Customer Cart: http://localhost:8100/customer-ui/cart/
- Staff Login: http://localhost:8100/staff-ui/login/
- Staff Dashboard: http://localhost:8100/staff-ui/
- Staff Product Form: http://localhost:8100/staff-ui/products/form/

## Ví dụ giao tiếp giữa các service

### Customer -> Product services (tìm kiếm)

Customer service gọi:

- GET http://laptop-service:8000/api/laptops/?search=<query>
- GET http://mobile-service:8000/api/mobiles/?search=<query>

Phần tổng hợp dữ liệu này được triển khai tại:
- customer_service/customers/views.py (ProductSearchView)

### Staff -> Product services (ghi dữ liệu)

Staff service proxy thao tác tạo/cập nhật/xóa bằng internal service key:

- POST http://laptop-service:8000/api/laptops/
- PUT http://laptop-service:8000/api/laptops/<id>/
- DELETE http://laptop-service:8000/api/laptops/<id>/
- POST/PUT/DELETE cho các endpoint tương ứng của mobile-service

Internal key được gửi trong:
- Header X-Internal-API-Key

Được triển khai tại:
- staff_service/staffops/views.py
- laptop_service/laptops/permissions.py
- mobile_service/mobiles/permissions.py

## File môi trường

Mỗi service đều có:
- .env.example
- .env

Bạn có thể chỉnh các file .env theo cấu hình máy của bạn trước khi chạy.

## Hướng dẫn chạy

1. Build và khởi động toàn bộ services:

```bash
docker compose up --build
```

2. Mở giao diện khách hàng (frontend tập trung tại gateway):

- http://localhost:8100/customer-ui/

3. Mở giao diện nhân viên (frontend tập trung tại gateway):

- http://localhost:8100/staff-ui/

4. Tạo tài khoản staff (lần chạy đầu):

```bash
docker compose exec staff-service python manage.py createsuperuser
```

Sau đó gán quyền staff cho user vừa tạo nếu cần:

```bash
docker compose exec staff-service python manage.py shell
```

Trong shell:

```python
from django.contrib.auth.models import User
u = User.objects.get(username="<your-username>")
u.is_staff = True
u.save()
```

5. Kiểm thử API trực tiếp:

- Customer register: POST http://localhost:8101/api/auth/register/
- Customer login: POST http://localhost:8101/api/auth/login/
- Customer search: GET http://localhost:8101/api/products/search/?q=pro
- Staff login: POST http://localhost:8102/api/auth/login/
- Laptop CRUD: http://localhost:8103/api/laptops/
- Mobile CRUD: http://localhost:8104/api/mobiles/

## Seed dữ liệu test

Chạy một lệnh để nạp dữ liệu mẫu cho toàn bộ hệ thống:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\seed_all_data.ps1
```

Dữ liệu seed gồm:

- 8 laptop mẫu
- 8 mobile mẫu
- 3 tài khoản customer + cart mẫu
- 2 tài khoản staff (đã bật `is_staff=True`)

Tài khoản test:

- customer01 / Customer@123
- customer02 / Customer@123
- customer03 / Customer@123
- staff01 / Staff@123
- staff02 / Staff@123

## Ghi chú

### Kiến trúc & Công nghệ
- Tất cả services là các dự án Django độc lập.
- Mỗi service có cơ sở dữ liệu riêng.
- JWT được triển khai trong customer-service và staff-service.
- Các product service được bảo vệ thao tác ghi bằng internal API key cho giao tiếp nội bộ giữa services.

### Cải tiến gần đây
- ✅ **Dark theme (Modern Dark Professional)**: Giao diện tối ưu với color palette tối/sáng, gradient blue accent.
- ✅ **Product customization**: Tên sản phẩm tùy chỉnh (MacBook Pro 16", iPhone 15 Pro, Galaxy S24, v.v.).
- ✅ **Placeholder images**: Sản phẩm hiển thị placeholder gradient thay vì load ảnh từ URL.
- ✅ **Form field spacing**: Tất cả form (login, register, product form) có spacing đều đặn.
- ✅ **Authentication fix**: Enhanced login handler với console logging, token dual-check, better error extraction.
- ✅ **Product detail page tối ưu**: Tự tải cart của user, chọn cart từ dropdown, tạo cart nhanh, xử lý trùng sản phẩm bằng auto-increment quantity.
- ✅ **Giao diện mới**: Phong cách ecommerce hiện đại, giá định dạng VND, responsive design.
- ✅ **Dữ liệu test**: Tự động seed 8 laptop, 8 mobile, 3 customer, 2 staff qua một lệnh.

### Frontend structure
- gateway/frontend/index.html
- gateway/frontend/customer-home.html
- gateway/frontend/customer-login.html
- gateway/frontend/customer-register.html
- gateway/frontend/customer-detail.html
- gateway/frontend/customer-cart.html
- gateway/frontend/staff-login.html
- gateway/frontend/staff-dashboard.html
- gateway/frontend/staff-product-form.html
- gateway/frontend/assets/main.css
- gateway/frontend/assets/app.js
