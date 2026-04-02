# Dùng môi trường Node 18 làm nền
FROM node:18-alpine

# Tạo thư mục làm việc trong container
WORKDIR /app

# Copy các file cấu hình thư viện vào trước
COPY package*.json ./

# Cài đặt thư viện (chỉ cài các thư viện cần cho môi trường production)
RUN npm install --only=production

# Copy toàn bộ mã nguồn còn lại vào
COPY . .

# Mở cổng 5001 để bên ngoài có thể truy cập
EXPOSE 5006

# Lệnh khởi động ứng dụng khi container chạy
CMD ["npm", "start"]