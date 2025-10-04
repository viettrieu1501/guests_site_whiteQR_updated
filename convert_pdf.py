import os
from PIL import Image

CARDS_DIR = 'cards'
OUTPUT_PDF = os.path.abspath(os.path.join('.', 'cards_all.pdf'))
IMAGE_EXTS = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp')

# A4 @ DPI
DPI = 300
A4_W = int(8.27 * DPI)   # 2481 px
A4_H = int(11.69 * DPI)  # 3508 px

MARGIN = 50   # lề
HGAP = 20     # khoảng cách ngang
VGAP = 20     # khoảng cách dọc

COLS = 2
ROWS = 3

def collect_images(folder):
    files = [f for f in os.listdir(folder) if f.lower().endswith(IMAGE_EXTS)]
    files.sort()
    return [os.path.join(folder, f) for f in files]

def images_to_pdf_grid(image_paths, output_pdf, dpi=DPI):
    if not image_paths:
        print("Không có ảnh trong thư mục:", CARDS_DIR)
        return

    # kích thước 1 ô
    cell_w = (A4_W - 2*MARGIN - (COLS-1)*HGAP) // COLS
    cell_h = (A4_H - 2*MARGIN - (ROWS-1)*VGAP) // ROWS

    pages = []
    for i in range(0, len(image_paths), COLS*ROWS):
        page = Image.new('RGB', (A4_W, A4_H), 'white')
        subset = image_paths[i:i+COLS*ROWS]

        for idx, p in enumerate(subset):
            try:
                im = Image.open(p).convert('RGB')
            except Exception as e:
                print("Bỏ qua ảnh vì lỗi:", p, e)
                continue

            iw, ih = im.size
            # scale theo tỉ lệ để vừa cell
            scale = min(cell_w/iw, cell_h/ih)
            new_w = int(iw*scale)
            new_h = int(ih*scale)
            im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # tính vị trí trong grid
            row = idx // COLS
            col = idx % COLS
            x0 = MARGIN + col*(cell_w + HGAP) + (cell_w - new_w)//2
            y0 = MARGIN + row*(cell_h + VGAP) + (cell_h - new_h)//2

            page.paste(im, (x0, y0))

        pages.append(page)

    # lưu PDF
    first, rest = pages[0], pages[1:]
    first.save(output_pdf, "PDF", resolution=float(dpi), save_all=True, append_images=rest)
    print("Đã tạo PDF:", output_pdf)

if __name__ == "__main__":
    os.makedirs(CARDS_DIR, exist_ok=True)
    paths = collect_images(CARDS_DIR)
    images_to_pdf_grid(paths, OUTPUT_PDF)
