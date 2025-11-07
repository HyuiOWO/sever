🚀 Termux Web Shell Server

<div align="center">

https://img.shields.io/badge/Python-3.8+-blue.svg
https://img.shields.io/badge/Termux-✅-green.svg
https://img.shields.io/badge/Web%20Interface-✅-success.svg
https://img.shields.io/badge/Mobile%20Friendly-✅-9cf.svg

Biến điện thoại Android thành server đa năng với giao diện web chuyên nghiệp

Quản lý files, chạy commands, thực thi scripts trực tiếp từ trình duyệt

https://img.shields.io/badge/⭐-Tính_Năng-yellow
https://img.shields.io/badge/⚙️-Cài_Đặt_Nhanh-blue
https://img.shields.io/badge/🚀-Hướng_Dẫn_Sử_Dụng-orange

</div>

📖 Giới Thiệu

Termux Web Shell Server là giải pháp toàn diện biến điện thoại Android của bạn thành một web server mạnh mẽ. Với giao diện web trực quan, bạn có thể:

· 🖥️ Truy cập và điều khiển Termux từ bất kỳ thiết bị nào trong mạng LAN
· ⚡ Thực thi commands shell, Python, Node.js, PHP trực tiếp từ browser
· 📁 Quản lý files - tạo, xóa, upload, chỉnh sửa file dễ dàng
· 🔄 Chạy đa nhiệm - nhiều scripts cùng lúc không làm gián đoạn server
· 📱 Tối ưu mobile - giao diện responsive hoạt động tốt trên mọi thiết bị

Ứng dụng thực tế:

· 🎯 Phát triển và test web applications
· 🔧 Quản trị hệ thống từ xa
· 📚 Học lập trình và thực hành coding
· 🛠️ Chạy scripts tự động và monitoring

🌟 Tính Năng Nổi Bật

🖥️ Giao Diện Web Hiện Đại

· Giao diện terminal-style với theme tối
· Responsive design cho mobile & desktop
· Real-time loading animations
· Trải nghiệm người dùng mượt mà

⚡ Đa Ngôn Ngữ Lập Trình

```python
# Python
print("Hello World!")
for i in range(5):
    print(f"Count: {i}")
```

```javascript
// Node.js
console.log("JavaScript is running!");
setTimeout(() => console.log("Async works!"), 1000);
```

```php
<?php
// PHP
echo "PHP Server is ready!\n";
for($i=0; $i<3; $i++) {
    echo "Loop: $i\n";
}
?>
```

```bash
#!/bin/bash
# Shell Script
echo "Bash scripting!"
ls -la
pwd
```

📁 Quản Lý Files Toàn Diện

· Tạo file mới trực tiếp trên web
· Upload files từ thiết bị local
· Chỉnh sửa content với text editor
· Xóa files an toàn
· Tự động detect file type để chạy

🔄 Background Processing

· Chạy nhiều processes cùng lúc
· Theo dõi real-time với PID
· Start/Stop linh hoạt không ảnh hưởng server
· Auto-refresh trạng thái processes

📊 System Monitoring

· ⏰ Server Uptime theo dõi thời gian hoạt động
· 🌐 Network Ping kiểm tra kết nối internet
· 🔄 Real-time Status cập nhật tự động

🚀 Cài Đặt Nhanh

Bước 1: Cài Đặt Termux & Dependencies

```bash
# 📋 Copy để cài đặt dependencies
pkg update && pkg upgrade
pkg install python git nodejs php
```

Bước 2: Download Source Code

```bash
# 📋 Copy để clone repository
git clone https://github.com/HyuiOWO/sever.git
cd sever
```

Bước 3: Khởi Chạy Server

```bash
# 📋 Copy để chạy server
chmod +x severTermux.py
python severTermux.py
```

🎯 Kết Quả Sau Khi Chạy

```
🚀 Starting Termux Web Shell Server...
📱 Local: http://localhost:8080
🌐 Network: http://192.168.1.100:8080
⏰ Server started at: 2024-01-01 12:00:00
📂 Serving from: /data/data/com.termux/files/home
🔥 Background processes enabled
⏹️  Press Ctrl+C to stop
```

📖 Hướng Dẫn Sử Dụng Chi Tiết

1. 🖥️ Truy Cập Web Interface

Sau khi server chạy, mở browser và truy cập:

Trên cùng điện thoại:

```
http://localhost:8080
```

Từ thiết bị khác trong mạng WiFi:

```
http://[IP-TERMUX]:8080
```

Để tìm IP Termux:

```bash
# 📋 Copy để tìm IP
ifconfig
# Hoặc
ip addr show wlan0
```

2. ⚡ Sử Dụng Command Panel

Chọn Loại Command:

· 🐚 Shell Command - Lệnh hệ thống thông thường
· 🐍 Python Script - Thực thi code Python
· 🟢 Node.js - Chạy JavaScript
· 🐘 PHP - Thực thi PHP code
· 💻 Bash Script - Chạy shell scripts
· 🔄 Shell Command (Background) - Chạy ngầm không block

Ví Dụ Thực Tế:

Kiểm tra hệ thống:

```bash
# 📋 Copy để chạy trong Shell Command
uname -a
df -h
free -h
whoami
```

Python development:

```python
# 📋 Copy để chạy trong Python Script
import os
import sys

print("Python Version:", sys.version)
print("Current Directory:", os.getcwd())
print("Files in directory:", os.listdir('.'))

# Tính toán phức tạp
result = sum(i*i for i in range(1000))
print(f"Sum of squares: {result}")
```

Node.js examples:

```javascript
// 📋 Copy để chạy trong Node.js
const fs = require('fs');

console.log('Node.js is running!');
console.log('Current directory:', process.cwd());

// Đọc file list
fs.readdir('.', (err, files) => {
    if (err) throw err;
    console.log('Files:', files);
});
```

3. 📁 Quản Lý Files Chuyên Nghiệp

Tạo File Mới:

1. Nhập tên file (ví dụ: my_script.py)
2. Nhập nội dung vào textarea
3. Click "Create File"

Upload Files:

1. Click "Choose File"
2. Chọn file từ thiết bị
3. Click "Upload File"

Thao Tác Với Files:

· Click tên file để xem và chỉnh sửa nội dung
· Nút "Run" → chạy file (tự động detect loại file)
· Nút "Delete" → xóa file (có xác nhận)

File Types Hỗ Trợ:

Extension Command Ví Dụ
.py python3 file.py Python scripts
.js node file.js Node.js applications
.php php file.php PHP scripts
.sh bash file.sh Shell scripts
Others ./file Executable binaries

4. 🔄 Background Processes Management

Khi File Đang Chạy:

· ✅ Nút "Run" chuyển thành "Stop" (màu đỏ)
· ✅ Hiển thị PID trong status panel
· ✅ Có thể dừng bất kỳ lúc nào

Theo Dõi Processes:

· Real-time monitoring trong status panel
· Auto-refresh mỗi 3 giây
· Hiển thị PID và filename
· Stop individual processes hoặc tất cả

5. 📊 System Status & Monitoring

Thông Tin Hiển Thị:

· ⏰ Server Uptime: Thời gian server đã chạy liên tục
· 🌐 Network Ping: Kiểm tra kết nối internet đến Google

Test Ping:

1. Click "Test Ping Google"
2. Xem kết quả:
   · ✅ Thành công: hiển thị ping time
   · ❌ Thất bại: thông báo lỗi

🛠️ Cài Đặt Nâng Cao

Chạy Server Background

```bash
# 📋 Copy để chạy background
nohup python severTermux.py > server.log 2>&1 &

# Theo dõi log
tail -f server.log
```

Tự Động Khởi Động

Tạo file start_server.sh:

```bash
#!/bin/bash
# 📋 Copy để tạo startup script
cd /data/data/com.termux/files/home/sever
python severTermux.py
```

Cấp quyền thực thi:

```bash
chmod +x start_server.sh
```

Custom Port

Sửa file severTermux.py:

```python
# Tìm dòng này và thay đổi port
PORT = 8080  # Đổi thành 8081, 8888, etc.
```

🔧 API Documentation

Endpoints Available:

Method Endpoint Mô Tả
GET / Giao diện web chính
GET /api/files Danh sách files trong thư mục
GET /api/file/{filename} Lấy nội dung file
GET /api/status Thông tin system status
GET /api/running Processes đang chạy
POST /api/run Thực thi command
POST /api/file Tạo file mới
POST /api/upload Upload file
POST /api/delete Xóa file
POST /api/stop Dừng process
POST /api/ping Test network ping

Ví Dụ Sử Dụng API:

```bash
# Lấy danh sách files
curl http://localhost:8080/api/files

# Chạy command
curl -X POST http://localhost:8080/api/run \
  -H "Content-Type: application/json" \
  -d '{"command": "ls -la"}'
```

❓ Câu Hỏi Thường Gặp

❔ Làm sao truy cập từ điện thoại khác?

1. Đảm bảo cả 2 điện thoại cùng WiFi
2. Tìm IP của Termux bằng ifconfig
3. Truy cập http://[IP-TERMUX]:8080 từ browser

❔ Lỗi "Address already in use"?

```bash
# 📋 Copy để fix lỗi port
pkill -f "python.*severTermux"
# Hoặc đổi port trong code
```

❔ Không chạy được file .sh?

```bash
# 📋 Copy để cấp quyền execute
chmod +x script.sh
```

❔ Làm sao chạy file với arguments?

```python
# Trong Python script
import sys
print("Arguments:", sys.argv[1:])
```

```bash
# Trong command panel
python3 script.py arg1 arg2
```

❔ Server không nhận upload file?

· Kiểm tra quyền storage của Termux
· Chạy termux-setup-storage
· Đảm bảo có đủ dung lượng

🐛 Troubleshooting

Vấn Đề Thường Gặp & Giải Pháp

Vấn Đề Giải Pháp
Không kết nối được Kiểm tra WiFi, IP, firewall
Permission denied chmod +x severTermux.py
Python not found pkg install python
Port blocked Đổi port hoặc pkill -f python
Upload failed termux-setup-storage
Script không chạy Kiểm tra shebang và permissions

Debug Steps:

1. Kiểm tra server status:
   ```bash
   ps aux | grep python
   netstat -tulpn | grep 8080
   ```
2. Kiểm tra logs:
   ```bash
   tail -f server.log
   ```
3. Test kết nối:
   ```bash
   curl http://localhost:8080/api/status
   ```

📞 Hỗ Trợ & Đóng Góp

Tìm Help:

· 📖 Đọc kỹ documentation trước
· 🔍 Kiểm tra FAQ section
· 🐛 Tạo issue trên GitHub với thông tin chi tiết

Đóng Góp:

· 🌟 Star repository nếu thấy hữu ích
· 🔧 Fork và submit PR để cải thiện
· 💡 Đề xuất tính năng mới

📜 License

MIT License - Xem file LICENSE để biết thêm chi tiết.

---

<div align="center">

🎯 Bắt Đầu Ngay!

```bash
# Bạn đã sẵn sàng? Chạy ngay!
git clone https://github.com/HyuiOWO/sever.git
cd sever
python severTermux.py
```

Biến điện thoại thành cỗ máy lập trình di động ngay hôm nay!

Cre: Nguyen Gia Huy

⭐ Đừng quên star repository nếu bạn thấy hữu ích!

</div>
```