import os
import random
import re
import sys
import json  # <--- เพิ่ม json
from datetime import datetime, timedelta

# ✅ ใช้ Pillow อย่างเดียว
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageEnhance, ImageOps
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

FACE_DIR = os.path.join(DRIVING_DIR, "data", "face_M", "face_FM")

ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
FONT_DIR = os.path.join(ASSETS_DIR, "fonts")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output_PT")

TEMPLATE_FILE = os.path.join(ASSETS_DIR, "photo", "Test_bottom.jpg")
MAP_ASSET_FILE = os.path.join(ASSETS_DIR, "photo", "png-clipart-thailand-drawing-blank-map-map-of-thailand-white-text-thumbnail.png")

TOTAL_IMAGES = 125  # <--- แก้จำนวนตรงนี้

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "images"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "labels"), exist_ok=True)

# ==========================================
# 2. HELPERS
# ==========================================
def random_date(start_year, end_year):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randrange(delta.days)
    return start + timedelta(days=random_days)

def load_names(filepath):
    data = []
    if not os.path.exists(filepath): 
        print(f"⚠️ ไม่พบไฟล์: {filepath}")
        return None
    
    # พยางค์ภาษาอังกฤษสำหรับสุ่มสร้างชื่อคู่ (Synthetic English Name)
    en_prefixes = ["Siri", "Phon", "Chai", "Rattan", "Wara", "Natt", "Thit", "Kora", "Mana", "Som"]
    en_suffixes = ["chai", "phon", "sak", "nan", "rat", "porn", "dee", "kun", "jit", "wan"]

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                name_th = line.strip()
                # ลบวงเล็บ [xxx] ถ้ามี
                if '[' in name_th and ']' in name_th:
                    name_th = re.sub(r'\[.*?\]', '', name_th).strip()
                
                if name_th:
                    # 💡 สร้างชื่ออังกฤษจำลอง (เช่น Sirisak, Somwan)
                    random_en = random.choice(en_prefixes) + random.choice(en_suffixes)
                    # เก็บเป็น Tuple (ไทย, อังกฤษ)
                    data.append((name_th, random_en.upper()))
    except Exception as e:
        print(f"⚠️ Error reading {filepath}: {e}")
        return None
    return data if len(data) > 0 else None

# โหลดข้อมูลจริงจาก gen_name.txt
names_db = load_names(NAME_FILE)
surnames_db = load_names(SURNAME_FILE)
provinces = ["BANGKOK", "NONTHABURI", "CHIANG MAI", "PHUKET", "CHON BURI", "KHON KAEN", "SONGKHLA", "NAKHON RATCHASIMA", "RAYONG", "UDON THANI"]

def generate_thai_id():
    digits = [random.randint(1, 9)] + [random.randint(0, 9) for _ in range(11)]
    sum_val = sum(d * (13 - i) for i, d in enumerate(digits))
    check = (11 - (sum_val % 11)) % 10
    digits.append(check)
    raw = "".join(map(str, digits))
    fmt = f"{raw[0]} {raw[1:5]} {raw[5:10]} {raw[10:12]} {raw[12]}"
    return fmt, raw

def get_random_face(target_w, target_h):
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
    # กำหนดโฟลเดอร์แยกเพศ
    source_folders = [
        {"path": os.path.join(DRIVING_DIR, "data", "face_M"), "gender": "M"},
        {"path": os.path.join(DRIVING_DIR, "data", "face_FM"), "gender": "F"}
    ]
    
    all_faces = []
    for item in source_folders:
        if os.path.exists(item["path"]):
            files = [{"path": os.path.join(item["path"], f), "gender": item["gender"]} 
                     for f in os.listdir(item["path"]) if f.lower().endswith(valid_extensions)]
            all_faces.extend(files)

    if all_faces:
        chosen = random.choice(all_faces)
        try:
            img = Image.open(chosen["path"]).convert("RGB")
            img = ImageOps.fit(img, (target_w, target_h), method=Image.BICUBIC)
            return img, chosen["gender"] # คืนค่ารูปและเพศ
        except: pass
            
    return Image.new('RGB', (target_w, target_h), (200, 200, 200)), "M"

def enhance_template_clarity(image):
    image = ImageEnhance.Sharpness(image).enhance(2.0)
    image = ImageEnhance.Contrast(image).enhance(1.1)
    return image

# ==========================================
# 3. GRAPHICS FUNCTIONS
# ==========================================
def create_hologram_v57_ultra_bold(base_img, photo_x, photo_y, photo_w, photo_h):
    scale_factor = 4
    temp_w, temp_h = base_img.size
    overlay = Image.new("RGBA", (temp_w * scale_factor, temp_h * scale_factor), (0,0,0,0))

    map_w = (photo_w * 0.53) * scale_factor
    map_h = (photo_h * 0.46) * scale_factor
    map_x = (photo_x + photo_w) * scale_factor - map_w - (-30 * scale_factor)
    map_y = (photo_y + photo_h) * scale_factor - map_h - (-45 * scale_factor)

    if os.path.exists(MAP_ASSET_FILE):
        try:
            raw_map = Image.open(MAP_ASSET_FILE)
            resized_map = ImageOps.fit(raw_map, (int(map_w), int(map_h)), method=Image.LANCZOS, centering=(0.5, 0.5))
            gray_map = resized_map.convert("L")
            threshold_map = gray_map.point(lambda p: 255 if p > 200 else 0)
            mask = ImageOps.invert(threshold_map)
            mask = mask.filter(ImageFilter.MaxFilter(5))
            solid_white_map = Image.new("RGBA", resized_map.size, (255, 255, 255, 180))
            overlay.paste(solid_white_map, (int(map_x), int(map_y)), mask=mask)
        except: pass

    overlay_small = overlay.resize(base_img.size, resample=Image.LANCZOS)
    noise = Image.effect_noise(overlay_small.size, 20).convert("RGBA")
    noise.putalpha(30)
    overlay_small = Image.alpha_composite(overlay_small, noise)
    base_img.alpha_composite(overlay_small)

def create_center_ghost_v26_clean(face_img, width, height):
    ghost = face_img.resize((width, height)).convert("L")
    ghost = ImageOps.invert(ghost)
    ghost = ghost.filter(ImageFilter.GaussianBlur(radius=0.5))
    ghost = ImageEnhance.Contrast(ghost).enhance(1.6)
    ghost = ImageOps.colorize(ghost, black="#222222", white="#D0D0D0")
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle([(0,0), (width, height)], radius=8, fill=255)
    return ghost, mask

def create_right_chip_v24_faint(face_img, width, height, dob):
    chip = Image.new("LA", (width, height), (240, 50))
    face_small = face_img.resize((width, height)).convert("L")
    face_small = ImageEnhance.Sharpness(face_small).enhance(2.0)
    face_rgba = face_small.convert("RGBA")
    face_rgba.putalpha(110)
    chip_rgba = chip.convert("RGBA")
    chip_rgba.paste(face_rgba, (0,0), face_rgba)
    draw = ImageDraw.Draw(chip_rgba)
    try: font = ImageFont.truetype(os.path.join(FONT_DIR, "OCRA.ttf"), 9)
    except: font = ImageFont.load_default()
    text_color = (10, 10, 10, 60)
    lines = ["THA", dob.strftime("%d"), dob.strftime("%b").upper(), str(dob.year)]
    line_height = height / 4
    for i, line in enumerate(lines):
        y_pos = (i * line_height) + (line_height / 2)
        draw.text((width/2, y_pos), line, font=font, fill=text_color, anchor="mm")
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle([(0,0), (width, height)], radius=6, fill=255)
    return chip_rgba, mask

# ==========================================
# 4. CORE LOGIC
# ==========================================

def create_passport_v57(index):
    if not os.path.exists(TEMPLATE_FILE):
        print(f"❌ Template not found: {TEMPLATE_FILE}")
        return

    try:
        raw_template = Image.open(TEMPLATE_FILE).convert("RGBA")
        base_img = enhance_template_clarity(raw_template.convert("RGB")).convert("RGBA")
    except Exception as e:
        print(f"❌ Error loading template: {e}")
        return

    # --- Draw Images ---
    photo_w, photo_h = 95, 125
    photo_x, photo_y = 22, 65
    
    # ✅ แก้ไขจุดนี้: รับค่าเพศ (gender) จากฟังก์ชัน get_random_face
    face_img, gender = get_random_face(photo_w, photo_h) 
    
    face_noise = Image.effect_noise(face_img.size, 15).convert("RGB")
    face_img = Image.blend(face_img, face_noise, alpha=0.1)
    base_img.paste(face_img, (photo_x, photo_y))

    # --- Data Gen ---
    th_n, en_n = random.choice(names_db) if names_db else ("สมชาย", "SOMCHAI")
    th_l, en_l = random.choice(surnames_db) if surnames_db else ("ใจดี", "JAIDEE")
    
    # ✅ เพิ่ม Logic ตรวจสอบเพศเพื่อกำหนดคำนำหน้าชื่อ
    if gender == "F":
        title_th = random.choice(["นาง", "นางสาว"])
        title_en = "MRS." if title_th == "นาง" else "MISS"
        sex_val = "F"
    else:
        title_th = "นาย"
        title_en = "MR."
        sex_val = "M"

    province = random.choice(provinces)
    dob = random_date(1970, 2005)
    issue = random_date(2024, 2025)
    try: future_date = issue.replace(year=issue.year + 5)
    except: future_date = issue.replace(year=issue.year + 5, month=2, day=28)
    expiry = future_date - timedelta(days=1)
    pass_no = f"AA{random.randint(1000000, 9999999)}"
    id_fmt, id_raw = generate_thai_id()
    height_val = f"1.{random.randint(65, 90)}M"

    create_hologram_v57_ultra_bold(base_img, photo_x, photo_y, photo_w, photo_h)

    g1_w, g1_h = 32, 50
    g1_x, g1_y = 235, 167
    ghost1, mask1 = create_center_ghost_v26_clean(face_img, g1_w, g1_h)
    base_img.paste(ghost1, (g1_x, g1_y), mask1)

    g2_w, g2_h = 28, 35
    g2_x, g2_y = 395, 167
    ghost2, mask2 = create_right_chip_v24_faint(face_img, g2_w, g2_h, dob)
    base_img.paste(ghost2, (g2_x, g2_y), mask2)

    # --- Draw Text & Collect Annotations ---
    text_layer = Image.new('RGBA', base_img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(text_layer)
    annotations = [] 

    # Signature
    try:
        sig_fonts = ['Srisakdi-Regular.ttf', 'Charm-Regular.ttf', 'Charm-Bold.ttf', 'Pattaya-Regular.ttf']
        sig_font_name = random.choice(sig_fonts)
        sig_font = ImageFont.truetype(os.path.join(FONT_DIR, sig_font_name), random.randint(16, 20))
    except: sig_font = ImageFont.load_default()
    
    sig_text = f"{th_n} {th_l}"
    sig_x = 292 + random.randint(-3, 3)
    sig_y = 207 + random.randint(-2, 2)
    draw.text((sig_x, sig_y), sig_text, font=sig_font, fill=(0, 0, 0))
    
    bbox = draw.textbbox((sig_x, sig_y), sig_text, font=sig_font)
    annotations.append({"field": "signature", "text": sig_text, "box": bbox})

    # Other Fields
    # ✅ ปรับใช้ title_en, title_th และ sex_val ที่คำนวณตามเพศแล้ว
    positions = {
        "type_code": (145, 42, 10, "bold", "P"),
        "country_code": (210, 42, 10, "bold", "THA"),
        "passport_no": (318, 42, 12, "bold", pass_no),
        "surname_en": (134, 62, 10, "bold", en_l.upper()),
        "title_name_en": (134, 84, 10, "bold", f"{title_en} {en_n.upper()}"),
        "name_th": (134, 105, 10, "bold", f"{title_th} {th_n} {th_l}"),
        "nationality": (134, 128, 10, "bold", "THAI"),
        "dob": (204, 128, 10, "bold", dob.strftime("%d %b %Y").upper()),
        "id_number": (291, 128, 10, "bold", id_fmt),
        "sex": (133, 150, 9, "bold", sex_val),
        "place_of_birth": (204, 150, 10, "bold", province),
        "height": (134, 170, 9, "bold", height_val),
        "date_of_issue": (134, 190, 9, "bold", issue.strftime("%d %b %Y").upper()),
        "date_of_expiry": (134, 210, 9, "bold", expiry.strftime("%d %b %Y").upper()),
        "mrz_line1": (22, 250, 16, "mrz", f"P<THA{en_l.upper()}<<{en_n.upper()}".ljust(44, '<')[:44]),
        "mrz_line2": (22, 275, 16, "mrz", f"{pass_no}4THA{dob.strftime('%y%m%d')}{sex_val}{expiry.strftime('%y%m%d')}8{id_raw}00".ljust(44, '<')[:44])
    }

    for key, (x, y, size, ftype, text) in positions.items():
        if ftype == 'mrz': font_name = "Antic-Regular.ttf"
        elif ftype == 'bold': font_name = "Sarabun-Bold.ttf"
        else: font_name = "Sarabun-Regular.ttf"
        
        try: font = ImageFont.truetype(os.path.join(FONT_DIR, font_name), size)
        except: font = ImageFont.load_default()
            
        draw.text((x, y), text, font=font, fill=(0, 0, 0))
        
        # 🔥 Save Label bbox 🔥
        bbox = draw.textbbox((x, y), text, font=font)
        annotations.append({"field": key, "text": text, "box": bbox})

    # --- Save Image ---
    final_img = Image.alpha_composite(base_img, text_layer)
    filename = f"Passport{index:03d}"

    global_noise = Image.effect_noise(final_img.size, 10).convert("RGB")
    final_img_rgb = final_img.convert("RGB")
    final_img_rgb = Image.blend(final_img_rgb, global_noise, alpha=0.05)

    img_path = os.path.join(OUTPUT_DIR, "images", f"{filename}.jpg")
    final_img_rgb.save(img_path, quality=95)
    
    # --- Save Labels (JSON) ---
    label_path = os.path.join(OUTPUT_DIR, "labels", f"{filename}.json")
    with open(label_path, "w", encoding="utf-8") as f:
        json.dump({
            "filename": f"{filename}.jpg",
            "width": final_img.width,
            "height": final_img.height,
            "annotations": annotations
        }, f, ensure_ascii=False, indent=2)

    print(f"✅ Generated: {filename}.jpg + Labels")

# ==========================================
# EXECUTE
# ==========================================
if __name__ == "__main__":
    print(f"🚀 Starting Passport Generation...")
    print(f"📂 Linking Driving License Assets: {DRIVING_DIR}")
    
    for i in range(1, TOTAL_IMAGES + 1):
        create_passport_v57(i)

    print(f"\n✨ Completed! Output in: {OUTPUT_DIR}")