import csv
import unicodedata
import re

CSV_FILE = 'DANH SACH KHACH MOI.csv'

def to_upper_no_accent(text):
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    text = text.upper()
    text = re.sub(r'\s+', '_', text)
    return text

rows = []
with open(CSV_FILE, encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for idx, row in enumerate(reader, 1):
        rank_name = row.get('rank_name', '').strip()
        position = row.get('position', '').strip()
        seat = row.get('seat', '').strip()
        uid = str(idx).zfill(4)
        safe_name = f"{uid}_{to_upper_no_accent(rank_name)}"
        html_file = f"guests/{safe_name}.html"
        qr_file = f"qr/{safe_name}.png"
        rows.append(f'''  <tr>
    <td class="uid">{uid}</td>
    <td class="name">{rank_name}</td>
    <td class="title">{position}</td>
    <td class="seat">{seat}</td>
    <td class="qr"><img src="{qr_file}" alt="QR {uid}"></td>
    <td class="link"><a href="{html_file}">Mở</a></td>
  </tr>''')

tbody_content = '\n'.join(rows)

# Đọc file index.html gốc
with open('index.html', encoding='utf-8') as f:
    html = f.read()

# Thay thế nội dung trong <tbody>...</tbody>
import re
html = re.sub(
    r'(<tbody>)(.*?)(</tbody>)',
    f'\\1\n{tbody_content}\n\\3',
    html,
    flags=re.DOTALL
)

# Ghi lại file index.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)