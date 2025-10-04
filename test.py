import os

GUESTS_DIR = 'guests'

# Xóa tất cả file .html trong thư mục guests
for filename in os.listdir(GUESTS_DIR):
    if filename.endswith('.html'):
        os.remove(os.path.join(GUESTS_DIR, filename))