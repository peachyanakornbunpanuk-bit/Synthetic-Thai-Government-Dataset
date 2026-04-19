import os
import random
import urllib.request
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from barcode import Code128
from barcode.writer import ImageWriter
import qrcode
OUTPUT_DIR = "MEA_Custom_Names"
os.makedirs(OUTPUT_DIR, exist_ok=True)
LOGO_PATH = "/project/lt200393-foullm/Yanakorn_Peach/Dataset/Electric_bill/assets/logo"
FONT_DIR = "/project/lt200393-foullm/Yanakorn_Peach/Dataset/Electric_bill/assets/front"
NAME_FILE = "/project/lt200393-foullm/Yanakorn_Peach/Dataset/Electric_bill/assets/name_surname/thai_names_converted_TH_EN.txt"
SURNAME_FILE = "/project/lt200393-foullm/Yanakorn_Peach/Dataset/Electric_bill/assets/name_surname/thai_surnames_TH_EN.txt"

MEA_DISTRICTS = [
    "เขตลาดพร้าว", "เขตคลองเตย", "เขตสามเสน", "เขตวัดเลียบ",
    "เขตธนบุรี", "เขตยานนาวา", "เขตบางเขน", "เขตบางกะปิ",
    "เขตมีนบุรี", "เขตลาดกระบัง", "เขตบางนา", "เขตราษฎร์บูรณะ",
    "เขตบางขุนเทียน", "เขตบางใหญ่", "เขตนนทบุรี", "เขตบางบัวทอง",
    "เขตสมุทรปราการ", "เขตบางพลี"
]
if not os.path.exists(LOGO_PATH):
    print(f"ไม่พบไฟล์ {LOGO_PATH} กำลังสร้าง Placeholder...")
    img_logo = Image.new("RGBA", (150, 150), (255, 255, 255, 0))
    d_logo = ImageDraw.Draw(img_logo)
    d_logo.ellipse((10, 10, 140, 140), outline=(200, 60, 0), width=5)
    d_logo.rectangle((40, 60, 110, 120), fill=(200, 60, 0))
    img_logo.save(LOGO_PATH)

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def load_names(filepath):
    pairs = []
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.replace('|', ' ').replace(',', ' ').split()
                    if len(parts) >= 2:
                        pairs.append((parts[0], parts[-1]))
            print(f"✅ โหลดไฟล์ {os.path.basename(filepath)} สำเร็จ: {len(pairs)} รายการ")
        except Exception as e:
            print(f"❌ อ่านไฟล์ไม่ได้: {e}")
    else:
        print(f"⚠️ ไม่พบไฟล์: {filepath}")
    return pairs

names_db = load_names(NAME_FILE)
surnames_db = load_names(SURNAME_FILE)

def get_random_name_from_db():
    if names_db:
        first_name = random.choice(names_db)[0]
    else:
        first_name = "สมชาย"

    if surnames_db:
        last_name = random.choice(surnames_db)[0]
    else:
        last_name = "ใจดี"

    female_keywords = ["ศรี", "พร", "วรรณ", "ณา", "ญา", "สา", "กาญจน์", "รัตน์", "ลัย", "นภา", "มณี", "ดา", "ผกา", "สิริ", "อร", "อัม", "หญิง", "กมล", "นิ", "นา", "สุดา", "วิไล", "มาลี"]
    male_keywords = ["ศักดิ์", "ชัย", "พงศ์", "เทพ", "ยุทธ", "รักษ์", "เอก", "พล", "วิทย์", "สิทธิ์", "พัฒน์", "เดช", "ชาย", "กิตติ", "ธรรม", "วัช", "รณ", "ยศ"]

    is_female = any(k in first_name for k in female_keywords)
    is_male = any(k in first_name for k in male_keywords)

    if is_female and not is_male:
        prefix = random.choice(["นาง", "นางสาว"])
    elif is_male and not is_female:
        prefix = "นาย"
    else:
        prefix = random.choice(["นาย", "นาง", "นางสาว"])

    return f"{prefix}{first_name} {last_name}"

def generate_barcode(data, w, h, rotate=0, bar_height=10.0, line_width=0.35):
    writer = ImageWriter()
    ean = Code128(data, writer=writer)
    img = ean.render(writer_options={'module_width': line_width, 'module_height': bar_height, 'quiet_zone': 2, 'write_text': False, 'foreground': 'black'})
    img = img.resize((w, h), Image.Resampling.LANCZOS)
    if rotate != 0:
        img = img.rotate(rotate, expand=True)
    return img

def draw_text_centered(draw, text, box, font, fill, y_offset=0):
    x1, y1, x2, y2 = box
    cx = (x1 + x2) / 2
    w = draw.textlength(text, font=font)
    draw.text((cx - w/2, y1 + y_offset), text, font=font, fill=fill)

def generate_random_bill_data():
    year = 2024
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    read_date = datetime(year, month, day, random.randint(8, 16), random.randint(0, 59))
    due_date = read_date + timedelta(days=10)

    prev = random.randint(1000, 30000)
    units = random.randint(100, 600)
    curr = prev + units

    base_rate = 3.8
    base_cost = units * base_rate
    service = 38.22
    ft_unit = -0.1532
    ft_total = units * ft_unit

    pre_vat = base_cost + service + ft_total
    vat = pre_vat * 0.07
    total = pre_vat + vat

    hist_dates = []
    hist_units = []
    temp_date = read_date
    for _ in range(6):
        temp_date = temp_date - timedelta(days=30)
        th_year = (temp_date.year + 543) % 100
        d_str = f"{temp_date.day:02d}/{temp_date.month:02d}/{th_year:02d}"
        u_str = str(random.randint(units-50, units+50))
        hist_dates.append(d_str)
        hist_units.append(u_str)

    return {
        "district": random.choice(MEA_DISTRICTS),
        "name": get_random_name_from_db(),
        "ca_ref": f"{random.randint(0, 999999999):09d}",
        "install": f"{random.randint(10000000, 99999999)}",
        "mru": f"{random.randint(10000000, 99999999)}",
        "invoice": f"{random.randint(0, 999999999999):012d}",
        "read_date_str": read_date.strftime("%d/%m/%y %H:%M"),
        "due_date_str": due_date.strftime("%d/%m/%y"),
        "prev": str(prev),
        "curr": str(curr),
        "units": str(units),
        "base_cost": f"{base_cost:,.2f}",
        "ft_total": f"{ft_total:,.2f}",
        "pre_vat": f"{pre_vat:,.2f}",
        "vat": f"{vat:,.2f}",
        "total": f"{total:,.2f}",
        "ft_unit_str": f"{ft_unit:.4f}",
        "hist_dates": hist_dates,
        "hist_units": hist_units
    }

# ==========================================
# 4. DRAWING ENGINE
# ==========================================

def create_bill_with_custom_names(idx):
    W, H = 1000, 1600
    PAPER_COLOR = (250, 250, 245)
    img = Image.new("RGB", (W, H), PAPER_COLOR)
    draw = ImageDraw.Draw(img)

    data = generate_random_bill_data()
    C_TEXT = (5, 5, 5)
    C_HEADER = (180, 40, 20)
    C_LINE = (0, 0, 0)
    C_HIGHLIGHT = (250, 215, 160)
    C_GRAY_BG = (230, 230, 230)

    try:
        f_org = ImageFont.truetype("Sarabun-Bold.ttf", 46)
        f_bill = ImageFont.truetype("Sarabun-Bold.ttf", 42)
        f_district = ImageFont.truetype("Sarabun-Bold.ttf", 34)
        f_sub = ImageFont.truetype("Sarabun-Regular.ttf", 20)
        f_lbl_b = ImageFont.truetype("Sarabun-Bold.ttf", 22)
        f_lbl_s = ImageFont.truetype("Sarabun-Regular.ttf", 16)
        f_val_lg = ImageFont.truetype("Sarabun-Bold.ttf", 32)
        f_val_md = ImageFont.truetype("Sarabun-Bold.ttf", 28)
        f_val_sm = ImageFont.truetype("Sarabun-Bold.ttf", 24)
        f_body = ImageFont.truetype("Sarabun-Regular.ttf", 24)
        f_total = ImageFont.truetype("Sarabun-Bold.ttf", 40)
        f_hist_head = ImageFont.truetype("Sarabun-Bold.ttf", 18)
        f_small = ImageFont.truetype("Sarabun-Regular.ttf", 18)
    except:
        f_org = ImageFont.load_default()

    # HEADER
    try:
        real_logo = Image.open(LOGO_PATH).convert("RGBA")
        aspect = real_logo.width / real_logo.height
        new_h = 100
        new_w = int(new_h * aspect)
        real_logo = real_logo.resize((new_w, new_h), Image.Resampling.LANCZOS)
        img.paste(real_logo, (30, 10), real_logo)
    except: pass

    draw.text((140, 25), "การไฟฟ้านครหลวง", font=f_org, fill=C_TEXT)
    draw.text((140, 80), "Metropolitan Electricity Authority", font=f_sub, fill=C_TEXT)
    draw.text((520, 40), data["district"], font=f_district, fill=C_TEXT)
    draw.text((720, 35), "ใบแจ้งค่าไฟฟ้า", font=f_bill, fill=C_HEADER)
    draw.text((460, 85), "http://www.mea.or.th   MEA Call Center 1130", font=f_sub, fill=(139, 69, 19))
    draw.line((30, 120, 970, 120), fill=C_LINE, width=2)

    # USER INFO
    y_name = 135
    draw.text((20, y_name), "ชื่อผู้ใช้ไฟฟ้า (Name)", font=f_lbl_b, fill=C_HEADER)
    draw.text((230, y_name-4), data["name"], font=f_val_md, fill=C_TEXT)
    draw.line((30, 175, 970, 175), fill=C_LINE, width=1)

    y_prom = 185
    draw.text((30, y_prom), "ลูกรอยใบไฟฟ้า (Promise)", font=f_lbl_b, fill=C_HEADER)
    draw.line((30, 220, 970, 220), fill=C_LINE, width=2)

    # TABLE 1
    cols_1 = [30, 240, 430, 580, 860, 970]
    y_t1_top, y_t1_mid, y_t1_btm = 220, 275, 325
    for x in cols_1: draw.line((x, y_t1_top, x, y_t1_btm), fill=C_LINE, width=1)
    draw.line((30, y_t1_mid, 970, y_t1_mid), fill=C_LINE, width=1)
    draw.line((30, y_t1_btm, 970, y_t1_btm), fill=C_LINE, width=2)

    h1 = [("บัญชีแสดงสัญญา", "(CA/Ref No.1)"), ("รหัสเครื่องวัดฯ", "(Installation)"), ("MRU", ""), ("เลขที่ใบแจ้งฯ", "(Invoice No./Ref No.2)"), ("ประเภท", "(Type)")]
    v1 = [data["ca_ref"], data["install"], data["mru"], data["invoice"], "1.1"]
    for i in range(5):
        cx = (cols_1[i] + cols_1[i+1]) / 2
        w = draw.textlength(h1[i][0], font=f_lbl_b)
        draw.text((cx - w/2, y_t1_top+5), h1[i][0], font=f_lbl_b, fill=C_HEADER)
        w = draw.textlength(h1[i][1], font=f_lbl_s)
        draw.text((cx - w/2, y_t1_top+30), h1[i][1], font=f_lbl_s, fill=C_HEADER)
        draw_text_centered(draw, v1[i], (cols_1[i], y_t1_mid, cols_1[i+1], y_t1_btm), f_val_lg, C_TEXT, 7)

    # TABLE 2
    cols_2 = [30, 240, 440, 640, 840, 970]
    y_t2_top, y_t2_mid, y_t2_btm = 325, 380, 430
    for x in cols_2: draw.line((x, y_t2_top, x, y_t2_btm), fill=C_LINE, width=1)
    draw.line((30, y_t2_mid, 970, y_t2_mid), fill=C_LINE, width=1)
    draw.line((30, y_t2_btm, 970, y_t2_btm), fill=C_LINE, width=2)
    h2 = [("จดเลขอ่าน", "(Meter Reading Date)"), ("เลขอ่านครั้งหลัง", "(Last Matin Reading)"), ("เลขอ่านครั้งก่อน", "(Previous Meter Reading)"), ("จำนวนหน่วย", "(kWh)"), ("ตัวคูณ", "(Multiplier)")]
    v2 = [data["read_date_str"], data["curr"], data["prev"], data["units"], ""]
    for i in range(5):
        cx = (cols_2[i] + cols_2[i+1]) / 2
        w = draw.textlength(h2[i][0], font=f_lbl_b)
        draw.text((cx - w/2, y_t2_top+5), h2[i][0], font=f_lbl_b, fill=C_HEADER)
        w = draw.textlength(h2[i][1], font=f_lbl_s)
        draw.text((cx - w/2, y_t2_top+30), h2[i][1], font=f_lbl_s, fill=C_HEADER)
        draw_text_centered(draw, v2[i], (cols_2[i], y_t2_mid, cols_2[i+1], y_t2_btm), f_val_sm, C_TEXT, 7)

    # DETAILS
    y_det = 455
    draw.text((30, y_det), "รวมละเอียดค่าไฟฟ้า (Description)", font=f_val_sm, fill=C_TEXT)
    items = [("ค่าพลังงานไฟฟ้า", data["base_cost"]), ("ค่าบริการ", "38.22"), ("FT_LINE", data["ft_total"]), ("ส่วนลด", "0.00")]
    cy = y_det + 45
    for label, price in items:
        if label == "FT_LINE":
            draw.text((50, cy), "ค่าไฟฟ้าผันแปร (Ft)", font=f_body, fill=C_TEXT)
            draw.text((275, cy-3), data["ft_unit_str"], font=f_val_sm, fill=C_TEXT)
            draw.text((370, cy), "บาท/หน่วย   คือ", font=f_body, fill=C_TEXT)
        else:
            draw.text((50, cy), label, font=f_body, fill=C_TEXT)
        w = draw.textlength(price, font=f_val_sm)
        draw.text((720 - w, cy), price, font=f_val_sm, fill=C_TEXT)
        cy += 40
    draw.line((560, cy, 720, cy), fill=C_LINE, width=1)
    cy += 10
    draw.text((50, cy), "รวมค่าไฟฟ้าก่อนภาษีมูลค่าเพิ่ม", font=f_body, fill=C_TEXT)
    w = draw.textlength(data["pre_vat"], font=f_val_sm)
    draw.text((720 - w, cy), data["pre_vat"], font=f_val_sm, fill=C_TEXT)
    cy += 40
    draw.text((50, cy), "ภาษีมูลค่าเพิ่ม     7 %", font=f_body, fill=C_TEXT)
    w = draw.textlength(data["vat"], font=f_val_sm)
    draw.text((720 - w, cy), data["vat"], font=f_val_sm, fill=C_TEXT)
    cy += 40
    draw.line((560, cy, 720, cy), fill=C_LINE, width=1)
    cy += 10
    draw.text((50, cy), "รวมค่าไฟฟ้าเดือนปัจจุบัน", font=f_val_sm, fill=C_TEXT)
    w = draw.textlength(data["total"], font=f_val_sm)
    draw.text((720 - w, cy), data["total"], font=f_val_sm, fill=C_TEXT)

    # BARCODES
    bar_v = generate_barcode(data["ca_ref"], 280, 60, rotate=90, bar_height=4.0, line_width=0.5)
    img.paste(bar_v, (820, 475))
    txt_v = Image.new('RGBA', (200, 30), (255,255,255,0))
    d_v = ImageDraw.Draw(txt_v)
    d_v.text((0,0), data["ca_ref"], font=f_sub, fill="black")
    txt_v = txt_v.rotate(90, expand=True)
    img.paste(txt_v, (880, 525), txt_v)
    qr = qrcode.make(f"{data['ca_ref']}|{data['total']}").resize((130, 130))
    img.paste(qr, (790, 795))

    # TOTAL BOX
    y_box = 975
    draw.rectangle((520, y_box, 750, y_box+55), fill=C_HIGHLIGHT)
    draw.text((50, y_box+10), "รวมเงินที่ต้องชำระทั้งสิ้น (Amount)", font=f_lbl_b, fill=C_HEADER)
    draw.line((45, y_box+55, 750, y_box+55), fill=C_HEADER, width=3)
    w = draw.textlength(data["total"], font=f_total)
    draw.text((635 - w/2, y_box+5), data["total"], font=f_total, fill=C_TEXT)
    draw.text((45, y_box+80), "โปรดชำระเงินตั้งแต่วันที่ (Due Date)", font=f_lbl_b, fill=C_TEXT)
    draw.text((470, y_box+80), f"{data['due_date_str']} - {data['due_date_str']}", font=f_val_sm, fill=C_TEXT)
    draw.text((800, y_box+85), "v3.4.3 r015700", font=f_sub, fill=C_TEXT)
    draw.text((20, y_box+120), "* กรณีใช้ไฟฟ้าข้างชำระเดือนก่อน โปรดชำระทันที... (ข้อความตัดทอน) ...", font=ImageFont.truetype("Sarabun-Regular.ttf", 14), fill=C_TEXT)

    # FOOTER HISTORY
    y_h = 1175
    draw.text((40, y_h), "ประวัติการใช้ไฟฟ้า", font=f_lbl_b, fill=C_TEXT)
    cols_h = [20, 180, 300, 420, 540, 660, 780, 900]
    y_ht, y_hm, y_hb = 1205, 1235, 1265
    draw.rectangle((20, y_ht, 900, y_hm), fill=C_GRAY_BG)
    draw.rectangle((20, y_ht, 180, y_hb), fill=C_GRAY_BG)
    draw.line((20, y_ht, 900, y_ht), fill=C_LINE, width=1)
    draw.line((20, y_hm, 900, y_hm), fill=C_LINE, width=1)
    draw.line((20, y_hb, 900, y_hb), fill=C_LINE, width=1)
    for x in cols_h: draw.line((x, y_ht, x, y_hb), fill=C_LINE, width=1)

    draw.text((30, y_ht+5), "วันจดเลขอ่าน", font=f_hist_head, fill=C_HEADER)
    draw.text((30, y_hm+5), "จำนวนหน่วย", font=f_hist_head, fill=C_HEADER)

    d_h = data["hist_dates"]
    u_h = data["hist_units"]
    for i in range(len(d_h)):
        if i+1 < len(cols_h):
            cx = (cols_h[i+1] + cols_h[i+2]) / 2
            w = draw.textlength(d_h[i], font=f_sub)
            draw.text((cx - w/2, y_ht+5), d_h[i], font=f_sub, fill=C_TEXT)
            w = draw.textlength(u_h[i], font=f_sub)
            draw.text((cx - w/2, y_hm+5), u_h[i], font=f_sub, fill=C_TEXT)

    # BOTTOM BARCODE
    draw.text((40, 1295), "จดหน่วย-แจ้งค่าไฟฟ้าโดย บริษัท นิมิต รุ่งเรือง จำกัด โทร 0-2750-0003", font=f_val_sm, fill=C_TEXT)
    bar_long = generate_barcode(f"{data['ca_ref']}{data['total'].replace('.','')}", 650, 50, bar_height=5.0, line_width=0.5)
    img.paste(bar_long, (175, 1335))
    code_txt = f"|{data['invoice']} {data['ca_ref']} {data['total'].replace('.','')}"
    w = draw.textlength(code_txt, font=f_small)
    draw.text((500 - w/2, 1395), code_txt, font=f_small, fill=C_TEXT)
    # 1. Texture (Noise แบบ Multiply)
    noise_gray = Image.effect_noise(img.size, 35).convert("RGB")
    img_grainy = ImageChops.multiply(img, noise_gray)
    img = Image.blend(img, img_grainy, 0.20) # Blend 20%

    # 2. Tilt (สุ่มเอียงซ้ายขวา)
    angle = random.uniform(-2.0, 2.0)
    # ใช้ PAPER_COLOR เป็นสีขอบเพื่อไม่ให้ดำ
    img = img.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=PAPER_COLOR)

    # 3. Blur (เบลอเล็กน้อยให้เหมือนสแกน)
    img = img.filter(ImageFilter.GaussianBlur(0.5))

    filename = f"{OUTPUT_DIR}/mea_custom_name_{idx}.jpg"
    img.save(filename, quality=100)
    print(f"บันทึกไฟล์สำเร็จ: {filename} -> {data['name']} ({data['district']}) [เอียง {angle:.1f}°]")

# --- RUN LOOP ---
print("สร้างบิล (Realistic + Tilt) ---")
for i in range(1, 501):
    create_bill_with_custom_names(i)