import os
import qrcode

GUESTS_DIR = 'guests'
QR_DIR = 'qr'
BASE_URL = 'https://viettrieu1501.github.io/whiteQR/guests/'

# Xóa tất cả file .html trong thư mục qr
for filename in os.listdir(QR_DIR):
    if filename.endswith('.html'):
        os.remove(os.path.join(QR_DIR, filename))

os.makedirs(QR_DIR, exist_ok=True)

for filename in os.listdir(GUESTS_DIR):
    if filename.endswith('.html'):
        url = BASE_URL + filename
        qr_img = qrcode.make(url)
        # Đổi đuôi file sang .png
        png_filename = os.path.splitext(filename)[0] + '.png'
        qr_path = os.path.join(QR_DIR, png_filename)
        qr_img.save(qr_path)
        print(f'Đã tạo mã QR cho {filename}: {url} -> {png_filename}')