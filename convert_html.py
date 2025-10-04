import csv
import os
import unicodedata
import re

CSV_FILE = 'DANH SACH KHACH MOI.csv'
GUESTS_DIR = 'guests'

def to_upper_no_accent(text):
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    text = text.upper()
    text = re.sub(r'\s+', '_', text)
    return text

os.makedirs(GUESTS_DIR, exist_ok=True)

with open(CSV_FILE, encoding='utf-8-sig') as f:  # Dùng utf-8-sig để tự động bỏ BOM
    reader = csv.DictReader(f)
    for idx, row in enumerate(reader, 1):
        rank_name = row.get('rank_name', '').strip()
        position = row.get('position', '').strip()
        seat = row.get('seat', '').strip()
        safe_name = f"{str(idx).zfill(4)}_{to_upper_no_accent(rank_name)}.html"
        filepath = os.path.join(GUESTS_DIR, safe_name)
        html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Thẻ đại biểu – {rank_name}</title></head>
<body style="font-family:sans-serif;background:#fff;color:#000;padding:20px;">
<h2>THẺ ĐẠI BIỂU</h2>
<p><b>Tên:</b> {rank_name}</p>
<p><b>Chức vụ:</b> {position}</p>
<p><b>Ghế:</b> {seat}</p>
</body></html>
"""
        with open(filepath, 'w', encoding='utf-8') as out:
            out.write(html_content)