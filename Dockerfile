# Sử dụng môi trường Python 3.9 siêu nhẹ
FROM python:3.13-slim

# Chuyển thư mục làm việc vào /app
WORKDIR /app

# Copy file danh sách thư viện vào và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code của bạn vào trong máy ảo Docker
COPY . .

# Mở cổng 8000 cho FastAPI
EXPOSE 8000