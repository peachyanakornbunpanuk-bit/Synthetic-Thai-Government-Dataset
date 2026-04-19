import os
import random
import re
import sys
import json
from datetime import datetime, timedelta

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps, ImageChops
except ImportError:
    print("❌ Error: Pillow library missing.")
    sys.exit(1)

# ==========================================
# ⚙️ CONFIGURATION & PATHS
# ==========================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATASET_ROOT = os.path.dirname(PROJECT_ROOT)
DRIVING_DIR = os.path.join(DATASET_ROOT, "Driving_license")

NAME_FILE = os.path.join(DRIVING_DIR, "assets", "name_surname", "gen_name.txt")
SURNAME_FILE = os.path.join(DRIVING_DIR, "assets", "name_surname", "gen_name.txt")

ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
FONT_DIR = os.path.join(ASSETS_DIR, "fonts")
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, "template")

TEMPLATE_P1 = os.path.join(TEMPLATE_DIR, "Ex_Template_Dataset_P1.jpg") 
TEMPLATE_P2 = os.path.join(TEMPLATE_DIR, "Ex_Template_Dataset_P2.jpg")

# ⭐ แก้ Path Output ตามต้องการ
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output_full_paun") 

# ⭐ จำนวนที่จะสร้างเพิ่ม (เช่น มีอยู่แล้ว 0 จะทำเพิ่ม 1000)
TOTAL_IMAGES = 125

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "images"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "labels"), exist_ok=True)

# ==========================================
# 2. HELPERS (แก้ไขใหม่)
# ==========================================
def load_names(filepath):
    data = []
    if not os.path.exists(filepath):
        print(f"⚠️ ไม่พบไฟล์: {filepath}")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                name_th = line.strip()
                # ลบวงเล็บ [xxx] ถ้ามี (เหมือนในโปรแกรมใบขับขี่)
                if '[' in name_th and ']' in name_th:
                    name_th = re.sub(r'\[.*?\]', '', name_th).strip()
                
                if name_th:
                    data.append(name_th)
    except Exception as e:
        print(f"⚠️ Error reading {filepath}: {e}")
        return None
    return data if len(data) > 0 else None

# โหลดชื่อเข้า Database (จะกลายเป็น List ของชื่อไทยล้วน)
names_db = load_names(NAME_FILE)
surnames_db = load_names(SURNAME_FILE)

def get_random_name():
    # สุ่มชื่อและนามสกุลจากไฟล์ gen_name.txt ที่โหลดมา
    n = random.choice(names_db) if names_db else "สมชาย"
    l = random.choice(surnames_db) if surnames_db else "ใจดี"
    return n, l

def random_date(start_year_ad, end_year_ad):
    start = datetime(start_year_ad, 1, 1)
    end = datetime(end_year_ad, 12, 31)
    delta = end - start
    days = random.randrange(delta.days)
    return start + timedelta(days=days)

def format_thai_date(dt):
    m = ['','ม.ค.','ก.พ.','มี.ค.','เม.ย.','พ.ค.','มิ.ย.','ก.ค.','ส.ค.','ก.ย.','ต.ค.','พ.ย.','ธ.ค.']
    return f"{dt.day} {m[dt.month]} {dt.year+543}"

def generate_house_id():
    return f"{random.randint(1000,9999)}-{random.randint(100000,999999)}-{random.randint(0,9)}"

def generate_thai_pid():
    return f"{random.randint(1,8)}-{random.randint(1000,9999)}-{random.randint(10000,99999)}-{random.randint(10,99)}-{random.randint(1,9)}"

REAL_DATA_DB = {
    "กรุงเทพมหานคร": { "districts": { "จตุจักร": ["จอมพล", "ลาดยาว"], "บางรัก": ["สีลม", "บางรัก"], "ลาดพร้าว": ["ลาดพร้าว", "จรเข้บัว"] }, "prefix": "เขต" },
    "เชียงใหม่": { "districts": { "เมืองเชียงใหม่": ["ศรีภูมิ", "สุเทพ", "หายยา"], "แม่ริม": ["ริมใต้", "แม่สา", "ดอนแก้ว"] }, "prefix": "อำเภอ" },
    "ชลบุรี": { "districts": { "บางละมุง": ["หนองปรือ", "นาเกลือ", "ห้วยใหญ่"], "เมืองชลบุรี": ["บ้านสวน", "เสม็ด", "แสนสุข"] }, "prefix": "อำเภอ" },
    "ภูเก็ต": { "districts": { "เมืองภูเก็ต": ["ตลาดใหญ่", "วิชิต"], "กะทู้": ["ป่าตอง", "กมลา"] }, "prefix": "อำเภอ" }
}

def create_red_stamp(text_top, sign_text, name_text, width):
    height = int(width * 0.4)
    stamp_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(stamp_img)
    
    ink_color = (0, 0, 0, 150) 
    pen_color = (0, 0, 0, 150)

    draw.rectangle([(5, 5), (width-5, height-5)], outline=ink_color, width=3)

    try: font_h = ImageFont.truetype(os.path.join(FONT_DIR, "Sarabun-Bold.ttf"), int(height * 0.35))
    except: font_h = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text_top, font=font_h)
    draw.text(((width - (bbox[2]-bbox[0])) / 2, height * 0.1), text_top, font=font_h, fill=ink_color)

    try: font_s = ImageFont.truetype(os.path.join(FONT_DIR, "Srisakdi-Regular.ttf"), int(height * 0.25))
    except: font_s = ImageFont.load_default()
    bbox_s = draw.textbbox((0,0), sign_text, font=font_s)
    draw.text(((width - (bbox_s[2]-bbox_s[0])) / 2, height * 0.45), sign_text, font=font_s, fill=pen_color)

    try: font_n = ImageFont.truetype(os.path.join(FONT_DIR, "Sarabun-Regular.ttf"), int(height * 0.15))
    except: font_n = ImageFont.load_default()
    bbox_n = draw.textbbox((0,0), name_text, font=font_n)
    draw.text(((width - (bbox_n[2]-bbox_n[0])) / 2, height * 0.75), name_text, font=font_n, fill=ink_color)

    noise = Image.effect_noise(stamp_img.size, 50).convert("L")
    noise = ImageOps.invert(noise)
    mask = stamp_img.split()[3]
    mask = ImageChops.multiply(mask, noise)
    stamp_img.putalpha(mask)
    
    return stamp_img.rotate(random.randint(-2, 2), resample=Image.BICUBIC, expand=True)

# ==========================================
# 3. DRAWING LOGIC
# ==========================================
def draw_page1(template_path, shared_data):
    if not os.path.exists(template_path): return None, []
    img = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    W, H = img.size
    
    try:
        font = ImageFont.truetype(os.path.join(FONT_DIR, "Sarabun-Regular.ttf"), int(W * 0.022))
        sig_font = ImageFont.truetype(os.path.join(FONT_DIR, "Srisakdi-Regular.ttf"), int(W * 0.035))
    except: font = sig_font = ImageFont.load_default()

    prov = shared_data["province"]
    dist = shared_data["district"]
    subdist = shared_data["subdistrict"]
    reg_n, reg_s = get_random_name()
    
    assign_date = random_date(2000, 2015)
    print_date = random_date(2020, 2024)

    if "กรุงเทพ" in prov: office_str = f"{shared_data['office_prefix']} {dist}"
    else: office_str = f"{shared_data['office_prefix']}{dist}"

    house_types = [("บ้านเดี่ยว", "ตึก 2 ชั้น"), ("บ้านเดี่ยว", "ตึก 1 ชั้น"), ("บ้านเดี่ยว", "ครึ่งตึกครึ่งไม้ 2 ชั้น"), 
                   ("ตึกแถว", "ตึกแถว 3 ชั้น"), ("ตึกแถว", "ตึกแถว 4 ชั้น"), ("ทาวน์เฮ้าส์", "ตึก 2 ชั้น")]
    h_type, h_charac = random.choice(house_types)

    positions = {
        "house_id": ((0.20, 0.134), shared_data["house_id"]),
        "office": ((0.60, 0.136), office_str),
        "addr1": ((0.15, 0.235), f"{random.randint(1,999)}/{random.randint(1,99)}"),
        "addr2": ((0.15, 0.325), f"แขวง/ต.{subdist} {shared_data['office_prefix']}{dist} จ.{prov}"),
        "village": ((0.15, 0.415), f"หมู่บ้าน{subdist}"),
        "house_name": ((0.55, 0.418), "-"),
        "type": ((0.15, 0.513), h_type),
        "charac": ((0.60, 0.510), h_charac),
        "assign_date": ((0.28, 0.620), format_thai_date(assign_date)),
        "registrar": ((0.55, 0.78), f"( นาย{reg_n} {reg_s} )"),
        "print_date": ((0.72, 0.85), format_thai_date(print_date))
    }

    annotations = []
    text_color = (20, 20, 20) 
    for key, (pos_pct, text) in positions.items():
        x, y = int(pos_pct[0] * W), int(pos_pct[1] * H)
        draw.text((x, y), text, font=font, fill=text_color)
        annotations.append({"field": f"p1_{key}", "text": text, "box": [x, y, x+100, y+20], "page": 1})

    sx, sy = int(0.53 * W), int(0.70 * H)
    draw.text((sx, sy), f"{reg_n} {reg_s}", font=sig_font, fill=(10, 10, 10))

    img = img.convert("L").convert("RGB")
    return img, annotations

def draw_page2(template_path, shared_data):
    if not os.path.exists(template_path): return None, []
    img = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    W, H = img.size
    
    try:
        font = ImageFont.truetype(os.path.join(FONT_DIR, "Sarabun-Regular.ttf"), int(W * 0.021))
        sig_font = ImageFont.truetype(os.path.join(FONT_DIR, "Srisakdi-Regular.ttf"), int(W * 0.035))
    except: font = sig_font = ImageFont.load_default()

    p_n, p_s = get_random_name()
    f_n, _ = get_random_name()
    m_n, _ = get_random_name()
    stamper_n, stamper_s = get_random_name()
    reg_n, reg_s = get_random_name()

    dob = random_date(1980, 2010)
    move_in = random_date(2018, 2023)

    positions = {
        "house_code": ((0.60, 0.060), shared_data["house_id"]),
        "fullname": ((0.10, 0.138), f"นาย{p_n}  {p_s}"),
        "nationality": ((0.66, 0.138), "ไทย"),
        "sex": ((0.92, 0.138), "ชาย"),
        "id_card": ((0.21, 0.247), generate_thai_pid()),
        "status": ((0.52, 0.247), "เจ้าบ้าน"),
        "dob": ((0.78, 0.243), format_thai_date(dob)),
        "mother_name": ((0.18, 0.320), f"นาง{m_n}  {p_s}"),
        "mother_id": ((0.48, 0.320), generate_thai_pid()),
        "mother_nat": ((0.75, 0.320), "ไทย"),
        "father_name": ((0.18, 0.425), f"นาย{f_n}  {p_s}"),
        "father_id": ((0.48, 0.425), generate_thai_pid()),
        "father_nat": ((0.75, 0.425), "ไทย"),
        "move_from": ((0.13, 0.533), "ฐานข้อมูลการทะเบียนราษฎร"),
        "move_date": ((0.08, 0.610), f"เข้ามาอยู่ในบ้านนี้เมื่อ {format_thai_date(move_in)}"),
        "registrar": ((0.50, 0.615), f"( นาย{reg_n} {reg_s} )")
    }

    annotations = []
    text_color = (20, 20, 20)
    for key, (pos_pct, text) in positions.items():
        x, y = int(pos_pct[0] * W), int(pos_pct[1] * H)
        draw.text((x, y), text, font=font, fill=text_color)
        annotations.append({"field": f"p2_{key}", "text": text, "box": [x, y, x+100, y+20], "page": 2})

    sx, sy = int(0.50 * W), int(0.510 * H)
    draw.text((sx, sy), f"{reg_n} {reg_s}", font=sig_font, fill=(10, 10, 10))

    img = img.convert("L").convert("RGBA")
    stamp_img = create_red_stamp("สำเนาถูกต้อง", f"{stamper_n} {stamper_s}", f"( นาย{stamper_n} {stamper_s} )", int(W * 0.25))
    img.paste(stamp_img, (int(W * 0.45), int(H * 0.65)), stamp_img)

    return img.convert("RGB"), annotations

# ==========================================
# 4. EXECUTION (Auto-Append Logic)
# ==========================================
def create_full_book(index):
    prov = random.choice(list(REAL_DATA_DB.keys()))
    dist = random.choice(list(REAL_DATA_DB[prov]["districts"].keys()))
    sub = random.choice(REAL_DATA_DB[prov]["districts"][dist])
    
    shared_data = {
        "house_id": generate_house_id(),
        "province": prov, "district": dist, "subdistrict": sub,
        "office_prefix": REAL_DATA_DB[prov]["prefix"]
    }

    img1, anno1 = draw_page1(TEMPLATE_P1, shared_data)
    img2, anno2 = draw_page2(TEMPLATE_P2, shared_data)

    if img1 is None or img2 is None:
        print(f"❌ Error: Templates not found. Check: {TEMPLATE_P1}")
        return

    # 1. ปรับขนาดภาพ
    if img1.width != img2.width:
        ratio = img1.width / img2.width
        img2 = img2.resize((img1.width, int(img2.height * ratio)), Image.LANCZOS)

    # 2. สร้าง Canvas
    w_total = img1.width
    h_total = img1.height + img2.height
    full_img = Image.new("RGB", (w_total, h_total), (250,250,250))
    
    full_img.paste(img1, (0, 0))
    full_img.paste(img2, (0, img1.height))

    # 3. สร้างเงาสันหนังสือ
    shadow_height = 60
    shadow = Image.new("RGBA", (w_total, shadow_height), (0,0,0,0))
    draw_shadow = ImageDraw.Draw(shadow)
    for y in range(shadow_height):
        alpha = int(shadow_height - abs(y - shadow_height/2) * 2)
        draw_shadow.line([(0, y), (w_total, y)], fill=(0,0,0, int(alpha * 0.3))) 

    shadow_y_pos = img1.height - int(shadow_height / 2)
    full_img.paste(shadow.convert("RGB"), (0, shadow_y_pos), shadow)

    # 4. รวม Labels
    final_annotations = anno1
    for item in anno2:
        b = item["box"]
        item["box"] = [b[0], b[1] + img1.height, b[2], b[3] + img1.height]
        final_annotations.append(item)

    filename = f"house_full_vertical_{index:04d}"
    
    img_path = os.path.join(OUTPUT_DIR, "images", f"{filename}.jpg")
    full_img.save(img_path, quality=95)
    
    json_path = os.path.join(OUTPUT_DIR, "labels", f"{filename}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "filename": f"{filename}.jpg",
            "width": w_total, "height": h_total,
            "annotations": final_annotations
        }, f, ensure_ascii=False, indent=2)

    print(f"✅ Generated: {filename}.jpg")

if __name__ == "__main__":
    print(f"🚀 Starting Vertical House Registration Generation...")
    
    # --- Check Existing Files ---
    img_dir = os.path.join(OUTPUT_DIR, "images")
    existing_count = 0
    if os.path.exists(img_dir):
        # นับเฉพาะไฟล์ที่ขึ้นต้นด้วย house_full_vertical_ และเป็น jpg
        files = [f for f in os.listdir(img_dir) if f.startswith("house_full_vertical_") and f.endswith(".jpg")]
        existing_count = len(files)
        
    start_index = existing_count + 1
    end_index = start_index + TOTAL_IMAGES
    
    print(f"📊 เดิมมีอยู่: {existing_count} รูป")
    print(f"➕ กำลังสร้างเพิ่มอีก: {TOTAL_IMAGES} รูป (เริ่มที่ {start_index} ถึง {end_index - 1})")
    
    for i in range(start_index, end_index):
        create_full_book(i)
        
    print(f"\n✨ Completed! รวมทั้งหมดมี {end_index - 1} รูป")