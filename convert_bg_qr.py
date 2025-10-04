import os
from PIL import Image, ImageDraw, ImageFont
import csv
import unicodedata
import re

# ================== FILE CONFIG ===================
TEMPLATE_FILE = 'NỀN QR.png'
QR_DIR = 'qr'
CARDS_DIR = 'cards'
CSV_FILE = 'DANH SACH KHACH MOI.csv'

# Font
FONT_BOLD = "UTM HELVEBOLD_2.TTF"   # dùng một font cho tất cả

# ================== STYLE CONFIG ===================
# QR
QR_SIZE = 363
QR_LEFT = 86
QR_TOP  = 428

# SỐ GHẾ – chiều cao cố định + nén ngang để không “bè”
SEAT_CENTER_X = 690
SEAT_CENTER_Y = 620
SEAT_TARGET_HEIGHT = 240
SEAT_MAX_WIDTH = 280
SEAT_CONDENSE_X = 0.90   # <-- nén ngang 90% để chữ hẹp như mẫu A9
SEAT_COLOR = (0, 166, 81)

# --- 3 DÒNG CHỮ VÀNG (khớp mẫu vẽ) ---
# vẽ theo kiểu stack: bắt đầu từ LINE_TOP_Y, sau mỗi dòng tự cộng khoảng cách
LINE_TOP_Y = 210
GAP_12 = 15
GAP_23 = 15

LINE1_FONT_SIZE = 36      # "ĐỒNG CHÍ"
LINE2_FONT_SIZE = 50      # tên (to nhất)
LINE3_FONT_SIZE = 30      # chức danh

# Giảm tỉ lệ nén để chữ thon hơn
LINE1_CONDENSE_X = 0.85
LINE2_CONDENSE_X = 0.85
LINE3_CONDENSE_X = 0.85

LINE_COLOR   = (255, 221, 79)   # vàng
STROKE_COLOR = (0, 0, 0)      # viền xanh đậm
STROKE_WIDTH = 0.7

LINE_MAX_WIDTH = 900            # bề ngang tối đa cho mỗi dòng

# --- ALIAS tương thích để không lỗi nếu còn chỗ code cũ dùng ---
LINE_CONDENSE_X   = LINE1_CONDENSE_X
SCALE_X_CONDENSED = LINE1_CONDENSE_X
# ==================================================

def draw_text_autoscale(bg, y, text, font_path, base_font_size, fill,
                        max_width, condense_x=0.92,
                        stroke_width=2, stroke_fill=(0,100,0)):
    """
    Vẽ text vàng tự co khi dài, có stroke, căn giữa, nén ngang nhẹ.
    (Giữ nguyên để tương thích, nhưng KHỐI 3 DÒNG BÊN DƯỚI sẽ dùng bản trả về đáy)
    """
    if not text:
        return

    # 1) font cơ sở
    font = ImageFont.truetype(font_path, base_font_size)

    # 2) đo rộng để autoscale nếu vượt max_width
    tmp = Image.new("RGBA", (10,10), (0,0,0,0))
    d = ImageDraw.Draw(tmp)
    l, t, r, b = d.textbbox((0,0), text, font=font)
    w = r - l

    if w > max_width:
        scale = max_width / float(w)
        new_size = max(10, int(base_font_size * scale))
        font = ImageFont.truetype(font_path, new_size)

    # 3) vẽ lên layer riêng để có stroke
    layer = Image.new("RGBA", bg.size, (0,0,0,0))
    draw = ImageDraw.Draw(layer)
    draw.text((0,0), text, font=font, fill=fill,
              stroke_width=stroke_width, stroke_fill=stroke_fill)

    bbox = layer.getbbox()
    if not bbox:
        return
    cropped = layer.crop(bbox)

    # 4) nén ngang nhẹ (condensed)
    if 0 < condense_x < 1.0:
        new_w = int(cropped.size[0] * condense_x)
        cropped = cropped.resize((new_w, cropped.size[1]), Image.Resampling.LANCZOS)

    # 5) căn giữa theo ngang tại vị trí y
    paste_x = (bg.size[0] - cropped.size[0]) // 2
    bg.paste(cropped, (paste_x, y), cropped)

def draw_text_autoscale_bottom(bg, y, text, font_path, base_font_size, fill,
                               max_width, condense_x=0.92,
                               stroke_width=2, stroke_fill=(0,100,0)):
    """
    Vẽ text (autoscale + condensed + stroke) căn giữa tại y,
    TRẢ VỀ toạ độ y đáy của dòng vừa vẽ (để xếp dòng tiếp theo).
    """
    if not text:
        return y

    # 1) Font cơ sở + autoscale theo bề ngang
    font = ImageFont.truetype(font_path, base_font_size)
    tmp = Image.new("RGBA", (10,10), (0,0,0,0))
    d = ImageDraw.Draw(tmp)
    l, t, r, b = d.textbbox((0,0), text, font=font)
    w = r - l
    if w > max_width:
        scale = max_width / float(w)
        new_size = max(10, int(base_font_size * scale))
        font = ImageFont.truetype(font_path, new_size)

    # 2) Vẽ lên layer riêng để có stroke
    layer = Image.new("RGBA", bg.size, (0,0,0,0))
    draw = ImageDraw.Draw(layer)
    draw.text((0,0), text, font=font, fill=fill,
              stroke_width=stroke_width, stroke_fill=stroke_fill)

    bbox = layer.getbbox()
    if not bbox:
        return y
    cropped = layer.crop(bbox)

    # 3) Nén ngang
    if 0 < condense_x < 1.0:
        new_w = int(cropped.size[0] * condense_x)
        cropped = cropped.resize((new_w, cropped.size[1]), Image.Resampling.LANCZOS)

    # 4) Căn giữa và paste
    paste_x = (bg.size[0] - cropped.size[0]) // 2
    bg.paste(cropped, (paste_x, y), cropped)

    # Trả về đáy của dòng
    return y + cropped.size[1]

def to_upper_no_accent(text: str) -> str:
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    text = text.upper()
    text = re.sub(r'\s+', '_', text)
    return text

def draw_text_condensed(bg: Image.Image, y: int, text: str,
                        font: ImageFont.FreeTypeFont, fill,
                        scale_x=SCALE_X_CONDENSED,
                        stroke_width=STROKE_WIDTH, stroke_fill=STROKE_COLOR):
    if not text:
        return
    layer = Image.new("RGBA", bg.size, (0,0,0,0))
    d = ImageDraw.Draw(layer)
    d.text((0,0), text, font=font, fill=fill,
           stroke_width=stroke_width, stroke_fill=stroke_fill)
    bbox = layer.getbbox()
    if not bbox:
        return
    cropped = layer.crop(bbox)

    # nén ngang
    new_w = int(cropped.size[0] * scale_x)
    cropped = cropped.resize((new_w, cropped.size[1]), Image.Resampling.LANCZOS)

    paste_x = (bg.size[0] - new_w) // 2
    bg.paste(cropped, (paste_x, y), cropped)

# ===== Helpers cho SỐ GHẾ =====
# ...existing code...
def draw_seat_center(img: Image.Image, text: str, font_path: str,
                     fill, center_xy, max_w: int, target_h: int,
                     condense_x: float):
    """
    Vẽ số ghế căn giữa tại center_xy, chiều cao cố định = target_h,
    có viền trắng (stroke) độ dày 1px, nén ngang theo condense_x và giới hạn max_w.
    font_path: đường dẫn file TTF (ví dụ FONT_BOLD).
    """
    if not text:
        return

    W, H = img.size

    # tìm kích thước font lớn nhất sao cho chiều cao bbox <= target_h
    def measure_height(size):
        try:
            f = ImageFont.truetype(font_path, size)
        except Exception:
            return None
        tmp = Image.new("RGBA", (2000, 2000), (0,0,0,0))
        d = ImageDraw.Draw(tmp)
        # vẽ với stroke để đo chính xác
        d.text((0,0), text, font=f, fill=fill, stroke_width=1, stroke_fill=(255,255,255))
        bbox = tmp.getbbox()
        if not bbox:
            return 0, 0
        l,t,r,b = bbox
        return r-l, b-t

    low, high = 8, 1500
    best = low
    while low <= high:
        mid = (low + high) // 2
        res = measure_height(mid)
        if res is None:
            high = mid - 1
            continue
        w,h = res
        if h <= target_h:
            best = mid
            low = mid + 1
        else:
            high = mid - 1

    # render ở kích thước best với stroke trắng (1px)
    font = ImageFont.truetype(font_path, best)
    layer = Image.new("RGBA", (W, H), (0,0,0,0))
    d = ImageDraw.Draw(layer)
    d.text((0,0), text, font=font, fill=fill, stroke_width=1, stroke_fill=(255,255,255))
    bbox = layer.getbbox()
    if not bbox:
        return
    cropped = layer.crop(bbox)
    w, h = cropped.size

    # scale theo chiều cao target_h (nếu cần)
    if h != target_h:
        scale_h = target_h / float(h)
        new_w = max(1, int(w * scale_h))
        new_h = max(1, int(target_h))
        cropped = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # nén ngang để chữ thon hơn
    if 0 < condense_x < 1.0:
        new_w = max(1, int(cropped.size[0] * condense_x))
        cropped = cropped.resize((new_w, cropped.size[1]), Image.Resampling.LANCZOS)

    # chặn bề ngang tối đa
    if cropped.size[0] > max_w:
        cropped = cropped.resize((max_w, cropped.size[1]), Image.Resampling.LANCZOS)

    # căn giữa tại center_xy (và nâng nhẹ nếu cần)
    cx, cy = center_xy
    paste_x = int(cx - cropped.size[0] / 2)
    vertical_adjust = -15
    paste_y = int(cy - cropped.size[1] / 2) + vertical_adjust

    # đảm bảo không quá sát mép phải
    right_margin = 40
    paste_x = min(paste_x, W - right_margin - cropped.size[0])

    img.paste(cropped, (paste_x, paste_y), cropped)
# ...existing code...
# ================== MAIN ===================
os.makedirs(CARDS_DIR, exist_ok=True)

# mở template dạng lazy (chỉ giữ file gốc 1 lần)
with Image.open(TEMPLATE_FILE) as template:
    with open(CSV_FILE, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, 1):
            rank_name = row.get('rank_name', '').strip()
            position  = row.get('position', '').strip()
            seat      = (row.get('seat', '') or '').strip()

            uid = str(idx).zfill(4)
            safe_name = f"{uid}_{to_upper_no_accent(rank_name)}"
            qr_file   = os.path.join(QR_DIR,   f"{safe_name}.png")
            card_file = os.path.join(CARDS_DIR, f"{safe_name}.png")

            # copy template cho từng vòng lặp
            bg = template.copy()

            # ---- QR ----
            if not os.path.exists(qr_file):
                print(f"Không tìm thấy file QR: {qr_file}")
                bg.close()
                continue

            with Image.open(qr_file) as qr_img:
                qr_resized = qr_img.resize((QR_SIZE, QR_SIZE), Image.Resampling.LANCZOS)
                bg.paste(qr_resized, (QR_LEFT, QR_TOP))
                qr_resized.close()

            # ---- Fonts chữ vàng ----
            font_line1 = ImageFont.truetype(FONT_BOLD, LINE1_FONT_SIZE)
            font_line2 = ImageFont.truetype(FONT_BOLD, LINE2_FONT_SIZE)
            font_line3 = ImageFont.truetype(FONT_BOLD, LINE3_FONT_SIZE)
            name_upper = (rank_name or "").upper().strip()

            # Danh sách các tiền tố thuộc nhóm "ĐẠI BIỂU"
            dai_bieu_prefixes = ["ĐẠI BIỂU LÃNH ĐẠO", "ĐẠI BIỂU", "THƯ KÝ", "BÀ"]

            matched_prefix = None
            for prefix in dai_bieu_prefixes:
                if name_upper.startswith(prefix):
                    matched_prefix = prefix
                    break

            if matched_prefix:
                # line1 chính là prefix match được
                line1 = matched_prefix
                # bỏ prefix đó đi, phần còn lại là line2
                line2 = name_upper.replace(matched_prefix, "", 1).strip()

                line1_size = LINE1_FONT_SIZE + 14
                line2_size = LINE2_FONT_SIZE
                gap_12 = 6
                line1_offset_up = 14

                y = LINE_TOP_Y - line1_offset_up
                y = draw_text_autoscale_bottom(
                        bg, y, line1, FONT_BOLD, line1_size,
                        fill=LINE_COLOR, max_width=LINE_MAX_WIDTH,
                        condense_x=LINE1_CONDENSE_X,
                        stroke_width=STROKE_WIDTH, stroke_fill=STROKE_COLOR
                    ) + gap_12

                y = draw_text_autoscale_bottom(
                        bg, y, line2, FONT_BOLD, line2_size,
                        fill=LINE_COLOR, max_width=LINE_MAX_WIDTH,
                        condense_x=LINE2_CONDENSE_X,
                        stroke_width=STROKE_WIDTH, stroke_fill=STROKE_COLOR
                    ) + GAP_23

            else:
                # Mặc định xử lý đồng chí
                line1 = "ĐỒNG CHÍ"
                line2 = re.sub(r'^(ĐỒNG\s+CHÍ|Đ\/C|DONG\s+CHI)\s+', '', name_upper).strip()
                line1_size = LINE1_FONT_SIZE
                line2_size = LINE2_FONT_SIZE
                gap_12 = GAP_12
                y = LINE_TOP_Y

                y = draw_text_autoscale_bottom(
                        bg, y, line1, FONT_BOLD, line1_size,
                        fill=LINE_COLOR, max_width=LINE_MAX_WIDTH,
                        condense_x=LINE1_CONDENSE_X,
                        stroke_width=STROKE_WIDTH, stroke_fill=STROKE_COLOR
                    ) + gap_12
                y = draw_text_autoscale_bottom(
                        bg, y, line2, FONT_BOLD, line2_size,
                        fill=LINE_COLOR, max_width=LINE_MAX_WIDTH,
                        condense_x=LINE2_CONDENSE_X,
                        stroke_width=STROKE_WIDTH, stroke_fill=STROKE_COLOR
                    ) + GAP_23

            # Line 3 giữ nguyên
            line3 = (position or "").strip()
            _ = draw_text_autoscale_bottom(
                    bg, y, line3, FONT_BOLD, LINE3_FONT_SIZE,
                    fill=LINE_COLOR, max_width=LINE_MAX_WIDTH,
                    condense_x=LINE3_CONDENSE_X,
                    stroke_width=STROKE_WIDTH, stroke_fill=STROKE_COLOR
                )

            # ---- Vẽ số ghế ----
            draw_seat_center(
                bg, seat, FONT_BOLD, SEAT_COLOR,
                (SEAT_CENTER_X, SEAT_CENTER_Y),
                SEAT_MAX_WIDTH, SEAT_TARGET_HEIGHT,
                SEAT_CONDENSE_X
            )

            # lưu + giải phóng
            bg.save(card_file)
            bg.close()
            del bg
            print(f"Đã tạo: {card_file}")
