# sever
# Cập nhật package manager
pkg update && pkg upgrade

# Cài Python và các tools cơ bản
pkg install python

# Cài các ngôn ngữ lập trình (tuỳ chọn)
pkg install nodejs
pkg install php
pkg install clang  # Để compile một số package Python

# Cài git để clone repository (nếu cần)
pkg install git

# Cài các tool network
pkg install net-tools

# Download trực tiếp file Python
curl -O https://raw.githubusercontent.com/HyuiOWO/sever/main/severTermux.py

# Hoặc dùng wget
wget https://raw.githubusercontent.com/HyuiOWO/sever/main/severTermux.py

# Cấp quyền thực thi
chmod +x severTermux.py

# Chạy server
python severTermux.py
