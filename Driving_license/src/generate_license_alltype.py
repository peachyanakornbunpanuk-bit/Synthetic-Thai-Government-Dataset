import os 
import random
import csv
import math
import colorsys
import subprocess
import sys
import re
import json
from datetime import datetime, timedelta

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter, ImageChops
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter, ImageChops

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
TOTAL_IMAGES_TO_GENERATE = 1000  # จำนวนรูปที่จะสร้าง

# ==========================================
# 1. SETUP PATHS & LICENSE TYPES
# ==========================================
FACE_SOURCE_M = "/project/lt200393-foullm/Yanakorn_Peach/Dataset/Driving_license/data/face_M"
FACE_SOURCE_FM = "/project/lt200393-foullm/Yanakorn_Peach/Dataset/Driving_license/data/face_FM"
OUTPUT_ROOT = "/project/lt200393-foullm/Yanakorn_Peach/TestFinetune/Copy_P_Tee/ocr_proj/datasets/dataset_Syndata/Driving_license/outputfull3"

# Assets Path
ASSETS_DIR = "/project/lt200393-foullm/Yanakorn_Peach/Dataset/Driving_license/assets"
FONT_BOLD_FILE = os.path.join(ASSETS_DIR, "front", "Sarabun-Bold.ttf")
LOGO_FILE = os.path.join(ASSETS_DIR, "logo", "dltLogo.png.webp")

# Texture Paths
SCRATCH_TEX_FILE = os.path.join(ASSETS_DIR, "textures", "scratches_01.jpg")
FINGERPRINT_TEX_FILE = os.path.join(ASSETS_DIR, "textures", "fingerprints_01.jpg")

# Text Data Paths
NAME_FILE_PATH = os.path.join(ASSETS_DIR, "name_surname", "thai_names_converted_TH_EN.txt")
SURNAME_FILE_PATH = os.path.join(ASSETS_DIR, "name_surname", "thai_surnames_TH_EN.txt")

LICENSE_CONFIGS = {
    # === กลุ่ม ท. (ขนส่งสาธารณะ - แถบเหลือง) ===
    "T1": {
        "group_folder": "Output_Transport_Group",
        "color": (240, 180, 50),
        "type_th": "ทุกประเภท ชนิดที่ 1", "type_en": "Every Type One",
        "header_th": "ใบอนุญาตเป็นผู้ขับรถทุกประเภทชนิดที่ 1",
        "header_en": "Public Vehicle Driving Licence Class I",
        "min_age": 22
    },
    "T2": {
        "group_folder": "Output_Transport_Group",
        "color": (240, 180, 50),
        "type_th": "ทุกประเภท ชนิดที่ 2", "type_en": "Every Type Two",
        "header_th": "ใบอนุญาตเป็นผู้ขับรถทุกประเภทชนิดที่ 2",
        "header_en": "Public Vehicle Driving Licence Class II",
        "min_age": 22
    },
    "T3": {
        "group_folder": "Output_Transport_Group",
        "color": (240, 180, 50),
        "type_th": "ทุกประเภท ชนิดที่ 3", "type_en": "Every Type Three",
        "header_th": "ใบอนุญาตเป็นผู้ขับรถทุกประเภทชนิดที่ 3",
        "header_en": "Public Vehicle Driving Licence Class III",
        "min_age": 22
    },
    "T4": {
        "group_folder": "Output_Transport_Group",
        "color": (240, 180, 50),
        "type_th": "ทุกประเภท ชนิดที่ 4", "type_en": "Every Type Four",
        "header_th": "ใบอนุญาตเป็นผู้ขับรถทุกประเภทชนิดที่ 4",
        "header_en": "Public Vehicle Driving Licence Class IV",
        "min_age": 25
    },

    # === กลุ่ม บ. (ขนส่งส่วนบุคคล - แถบม่วง) ===
    "B1": {
        "group_folder": "Output_Private_Group",
        "color": (155, 140, 215),
        "type_th": "ส่วนบุคคล ชนิดที่ 1", "type_en": "Private Type One",
        "header_th": "ใบอนุญาตเป็นผู้ขับรถส่วนบุคคลชนิดที่ 1",
        "header_en": "Private Driving Licence Class I",
        "min_age": 18
    },
    "B2": {
        "group_folder": "Output_Private_Group",
        "color": (155, 140, 215),
        "type_th": "ส่วนบุคคล ชนิดที่ 2", "type_en": "Private Type Two",
        "header_th": "ใบอนุญาตเป็นผู้ขับรถส่วนบุคคลชนิดที่ 2",
        "header_en": "Private Driving Licence Class II",
        "min_age": 20
    },
    "B3": {
        "group_folder": "Output_Private_Group",
        "color": (155, 140, 215),
        "type_th": "ส่วนบุคคล ชนิดที่ 3", "type_en": "Private Type Three",
        "header_th": "ใบอนุญาตเป็นผู้ขับรถส่วนบุคคลชนิดที่ 3",
        "header_en": "Private Driving Licence Class III",
        "min_age": 20
    },
    "B4": {
        "group_folder": "Output_Private_Group",
        "color": (155, 140, 215),
        "type_th": "ส่วนบุคคล ชนิดที่ 4", "type_en": "Private Type Four",
        "header_th": "ใบอนุญาตเป็นผู้ขับรถส่วนบุคคลชนิดที่ 4",
        "header_en": "Private Driving Licence Class IV",
        "min_age": 25
    }
}

# Fallback Data
FALLBACK_MALE_NAMES = [("สมชาย", "Somchai"), ("วิชัย", "Wichai"), ("ณัฐพงษ์", "Nattapong")]
FALLBACK_FEMALE_NAMES = [("สมหญิง", "Somying"), ("สุดา", "Suda"), ("รัตนา", "Rattana")]
FALLBACK_SURNAMES = [("ใจดี", "Jaidee"), ("มีสุข", "Meesuk")]

# ==========================================
# 2. LOGIC FIXES & UTILS
# ==========================================
def generate_thai_id():
    first_digit = random.choice([1, 3, 4, 5])
    digits = [first_digit] + [random.randint(0, 9) for _ in range(11)]
    sum_val = sum((13 - i) * d for i, d in enumerate(digits))
    check_digit = (11 - (sum_val % 11)) % 10
    digits.append(check_digit)
    s = "".join(map(str, digits))
    return f"{s[0]} {s[1:5]} {s[5:10]} {s[10:12]} {s[12]}"

def load_names_from_file(filepath):
    data = []
    if not os.path.exists(filepath): return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                
                # ลบวงเล็บ [xxx] ถ้ามี
                if '[' in line and ']' in line:
                    line = re.sub(r'\[.*?\]', '', line).strip()
                
                if not line: continue

                parts = []
                if '|' in line:
                    parts = line.split('|')
                elif ',' in line:
                    parts = line.split(',')
                else:
                    parts = line.split('\t')
                
                if len(parts) >= 2:
                    th = parts[0].strip()
                    en = parts[1].strip()
                    if th and en:
                        data.append((th, en))
    except Exception as e:
        print(f"⚠️ Error reading {filepath}: {e}")
        return None
    return data

def guess_gender_from_name(name_tuple):
    th_name, _ = name_tuple
    female_keywords = ['พร', 'วรรณ', 'ศรี', 'หญิง', 'ดา', 'นา', 'ทิพย์', 'รัตน์', 'กาญ', 'สา', 'มล', 'ลัย']
    male_keywords = ['ชาย', 'ศักดิ์', 'พงษ์', 'เทพ', 'ยุทธ', 'ชัย', 'พล', 'วิทย์', 'กิจ', 'เอก']
    score = 0
    for k in female_keywords: 
        if k in th_name: score -= 1
    for k in male_keywords:
        if k in th_name: score += 1
    if score > 0: return 'Male'
    if score < 0: return 'Female'
    return 'Neutral'

# โหลดข้อมูลจริง
RAW_NAMES = load_names_from_file(NAME_FILE_PATH)
RAW_SURNAMES = load_names_from_file(SURNAME_FILE_PATH)

if RAW_NAMES:
    print(f"โหลดชื่อได้: {len(RAW_NAMES)} รายการ")
else:
    print("โหลดชื่อไม่ได้! จะใช้ชื่อสำรองแทน")

def get_smart_data_v2(gender_from_image, license_code):
    spec = LICENSE_CONFIGS[license_code]
    
    if gender_from_image == 'Man':
        title_th, title_en = "นาย", "Mr."
        if RAW_NAMES:
             candidates = [n for n in RAW_NAMES if guess_gender_from_name(n) != 'Female']
             name_pair = random.choice(candidates if candidates else RAW_NAMES)
        else: name_pair = random.choice(FALLBACK_MALE_NAMES)
    else:
        title_th, title_en = "นางสาว", "Ms."
        if RAW_NAMES:
             candidates = [n for n in RAW_NAMES if guess_gender_from_name(n) != 'Male']
             name_pair = random.choice(candidates if candidates else RAW_NAMES)
        else: name_pair = random.choice(FALLBACK_FEMALE_NAMES)

    if RAW_SURNAMES: sur_pair = random.choice(RAW_SURNAMES)
    else: sur_pair = random.choice(FALLBACK_SURNAMES)

    curr = datetime.now()
    min_age = spec['min_age']
    age = random.randint(min_age, 60)
    dob = curr - timedelta(days=365*age + random.randint(0, 360))
    
    issue = curr - timedelta(days=random.randint(0, 300))
    expire_year = issue.year + 3
    expire = datetime(expire_year, dob.month, dob.day)
    if expire < issue: expire = expire.replace(year=expire_year + 1)

    def to_th_date(d):
        m_th = ['','ม.ค.','ก.พ.','มี.ค.','เม.ย.','พ.ค.','มิ.ย.','ก.ค.','ส.ค.','ก.ย.','ต.ค.','พ.ย.','ธ.ค.']
        return f"{d.day} {m_th[d.month]} {d.year+543}"

    return {
        "fullname_th": f"{title_th} {name_pair[0]}  {sur_pair[0]}",
        "fullname_en": f"{title_en} {name_pair[1]}  {sur_pair[1]}",
        "license_no": f"{random.randint(10,99)} {random.randint(10000,99999)}",
        "id_card": generate_thai_id(),
        "issue_date_th": to_th_date(issue),
        "issue_date_en": issue.strftime("%d %B %Y"),
        "expire_date_th": to_th_date(expire),
        "expire_date_en": expire.strftime("%d %B %Y"),
        "dob_th": to_th_date(dob),
        "dob_en": dob.strftime("%d %B %Y"),
        "stripe_color": spec['color'],
        "type_th": spec['type_th'],
        "type_en": spec['type_en'],
        "header_th": spec['header_th'],
        "header_en": spec['header_en']
    }

# ==========================================
# 3. GRAPHIC ENGINE (Helper Functions)
# ==========================================
def generate_metallic_texture(size):
    w, h = size, size
    texture = Image.new('RGBA', (w, h))
    pixels = texture.load()
    frequency = 3.0
    for y in range(h):
        for x in range(w):
            pos = (x + y) / (w + h) * frequency
            hue = pos % 1.0
            shine = math.sin(pos * math.pi * 2)
            saturation, value = 1.0, 1.0
            if shine > 0.8: saturation = 1.0 - ((shine - 0.8) * 4)
            r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
            pixels[x, y] = (int(r * 255), int(g * 255), int(b * 255), 255)
    return texture

def create_shiny_foil_stamp(emblem_path, size):
    if not os.path.exists(emblem_path):
        mask_img = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask_img)
        draw.ellipse((10, 10, size-10, size-10), fill=255)
        alpha_mask = mask_img
    else:
        try:
            original = Image.open(emblem_path).convert("RGBA")
            mask_img = ImageOps.fit(original, (size, size), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            alpha_mask = mask_img.split()[3]
        except: return None
    foil_texture = generate_metallic_texture(size)
    shiny_stamp = Image.new("RGBA", (size, size), (0,0,0,0))
    shiny_stamp.paste(foil_texture, (0,0), alpha_mask)
    r, g, b, a = shiny_stamp.split()
    a = a.point(lambda i: int(i * 0.35))
    shiny_stamp.putalpha(a)
    return shiny_stamp

def apply_holo_foil_pattern(base_img, emblem_path):
    W, H = base_img.size
    overlay_layer = Image.new("RGBA", (W, H), (0,0,0,0))
    stamp_size, spacing_x, spacing_y = 140, 240, 220
    stamp = create_shiny_foil_stamp(emblem_path, stamp_size)
    if not stamp: return base_img
    row_count = 0
    for y in range(-50, H, spacing_y):
        offset_x = (spacing_x // 2) if (row_count % 2 == 1) else 0
        for x in range(-50 - offset_x, W, spacing_x):
            overlay_layer.paste(stamp, (x, y), stamp)
        row_count += 1
    final_comp = Image.alpha_composite(base_img.convert("RGBA"), overlay_layer)
    enhancer = ImageEnhance.Color(final_comp)
    return enhancer.enhance(1.2).convert("RGB")

def create_sunset_texture(width, height):
    base = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(base)
    for y in range(height):
        r = y / height
        if r < 0.35: ratio = r/0.35; c=(int(255), int(220+(20*ratio)), int(180))
        elif r < 0.75: ratio = (r-0.35)/0.4; c=(int(255), int(200-(50*ratio)), int(150))
        else: ratio = (r-0.75)/0.25; c=(int(255), int(150+(50*ratio)), int(200))
        draw.line([(0, y), (width, y)], fill=c)
    return base

def add_rounded_corners(img, radius=90):
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
    img_rgba = img.convert("RGBA")
    img_rgba.putalpha(mask)
    return img_rgba

def apply_texture_overlay(base_img, texture_path, opacity=0.15, blend_mode='overlay'):
    if not os.path.exists(texture_path): return base_img
    try:
        texture = Image.open(texture_path).convert("L")
        texture = ImageOps.fit(texture, base_img.size, method=Image.Resampling.LANCZOS)
        overlay = Image.new('RGBA', base_img.size, (0,0,0,0))
        if blend_mode == 'screen':
            draw = ImageDraw.Draw(overlay)
            draw.rectangle([(0,0), base_img.size], fill=(255,255,255))
            final_alpha = texture.point(lambda p: int(p * opacity))
            overlay.putalpha(final_alpha)
        return Image.alpha_composite(base_img.convert("RGBA"), overlay)
    except: return base_img

def add_procedural_noise(img, opacity=0.04):
    W, H = img.size
    noise_img = Image.new("RGBA", (W, H))
    pixels = noise_img.load()
    for y in range(H):
        for x in range(W):
            grain = random.randint(100, 150) 
            alpha = int(opacity * 255 * (random.random() * 0.5 + 0.5))
            pixels[x, y] = (grain, grain, grain, alpha)
    return Image.alpha_composite(img.convert("RGBA"), noise_img)

# ==========================================
# 4. CARD GENERATOR MAIN (WITH JSON LABEL & FIXES)
# ==========================================
def generate_card(output_path, person_data, photo_path, logo_path, output_json_path):
    W, H = 1012, 638
    img = Image.new('RGB', (W, H), 'white')
    
    #List สำหรับเก็บข้อมูล Label
    annotations = []

    HEADER_H = 105
    FOOTER_H = 65
    Y_FOOTER_START = H - FOOTER_H
    DATA_BOX_X = 300
    DATA_BOX_W = W - 300 - 20
    Y_STRIPE_START = HEADER_H + 20
    Y_STRIPE_END = Y_STRIPE_START + 80
    Y_DATA_START = Y_STRIPE_END + 12
    Y_DATA_END = Y_FOOTER_START - 12
    DATA_H = Y_DATA_END - Y_DATA_START

    bg_texture = create_sunset_texture(DATA_BOX_W, DATA_H)
    full_bg = Image.new('RGB', (W, H), 'white')
    full_bg.paste(bg_texture, (DATA_BOX_X, Y_DATA_START))
    img.paste(full_bg, (0,0))

    img = apply_holo_foil_pattern(img, logo_path)
    draw = ImageDraw.Draw(img)

    C_BLUE = (16, 45, 115)
    C_STRIPE = person_data['stripe_color']

    draw.rectangle([(0, 0), (W, HEADER_H)], fill=C_BLUE)
    draw.rectangle([(0, Y_FOOTER_START), (W, H)], fill=C_BLUE)
    draw.rectangle([(DATA_BOX_X, Y_STRIPE_START), (DATA_BOX_X + DATA_BOX_W, Y_STRIPE_END)], fill=C_STRIPE) 
    draw.rectangle([(DATA_BOX_X, Y_DATA_START), (DATA_BOX_X + DATA_BOX_W, Y_DATA_END)], outline='gray', width=1)

    draw.rectangle([(30, 20), (120, 80)], fill='white')
    draw.rectangle([(30, 20), (120, 30)], fill=(200,0,0))
    draw.rectangle([(30, 70), (120, 80)], fill=(200,0,0))
    draw.rectangle([(30, 40), (120, 60)], fill=(0,0,140))

    try:
        f_h_th = ImageFont.truetype(FONT_BOLD_FILE, 36)
        f_h_en = ImageFont.truetype(FONT_BOLD_FILE, 24)
        f_label = ImageFont.truetype(FONT_BOLD_FILE, 22)
        f_val_th = ImageFont.truetype(FONT_BOLD_FILE, 24)
        f_val_en = ImageFont.truetype(FONT_BOLD_FILE, 20)
        f_name_th = ImageFont.truetype(FONT_BOLD_FILE, 32)
        f_id = ImageFont.truetype(FONT_BOLD_FILE, 26)
        f_footer = ImageFont.truetype(FONT_BOLD_FILE, 26)
        f_stripe_label_th = ImageFont.truetype(FONT_BOLD_FILE, 28)
        f_stripe_label_en = ImageFont.truetype(FONT_BOLD_FILE, 18)
        f_stripe_val_num = ImageFont.truetype(FONT_BOLD_FILE, 36)
        f_stripe_val_th = ImageFont.truetype(FONT_BOLD_FILE, 26)
        f_stripe_val_en = ImageFont.truetype(FONT_BOLD_FILE, 20)
    except:
        print(f"❌ Font Error: {FONT_BOLD_FILE}"); return

    #Function: วาด + เก็บ Label
    def draw_and_label(xy, text, font, fill, label_key):
        draw.text(xy, text, font=font, fill=fill)
        bbox = draw.textbbox(xy, text, font=font)
        # [x1, y1, x2, y2]
        annotations.append({
            "label": label_key,
            "text": text,
            "box": list(bbox)
        })

    draw_and_label((140, 18), "ประเทศไทย", f_h_th, 'white', "country_th")
    draw_and_label((140, 60), "Kingdom of Thailand", f_h_en, 'white', "country_en")
    
    txt_th = person_data['header_th'] 
    txt_en = person_data['header_en'] 
    
    w_th = draw.textlength(txt_th, font=f_h_th)
    w_en = draw.textlength(txt_en, font=f_h_en)
    
    draw_and_label((W - w_th - 30, 18), txt_th, f_h_th, 'white', "header_th")
    draw_and_label((W - w_en - 30, 60), txt_en, f_h_en, 'white', "header_en")

    # --- Photo Placement ---
    PH_X, PH_H_SIZE = 35, 310
    PH_Y_START = Y_DATA_END - PH_H_SIZE
    PHOTO_W = 250
    if os.path.exists(photo_path):
        try:
            user_img = Image.open(photo_path).convert("RGB")
            # ใช้ Fit เพื่อ crop กลางภาพให้สวยงาม
            user_img = ImageOps.fit(user_img, (PHOTO_W, PH_H_SIZE), method=Image.Resampling.LANCZOS)
            img.paste(user_img, (PH_X, PH_Y_START))
            annotations.append({"label": "face_photo", "box": [PH_X, PH_Y_START, PH_X+PHOTO_W, PH_Y_START+PH_H_SIZE]})
        except Exception as e:
            print(f" Error opening photo {photo_path}: {e}")
            draw.rectangle([(PH_X, PH_Y_START), (PH_X+PHOTO_W, Y_DATA_END)], fill='gray')
    else:
        # ถ้ารูปไม่มา ให้ถมเทา
        draw.rectangle([(PH_X, PH_Y_START), (PH_X+PHOTO_W, Y_DATA_END)], fill='gray')
        
    draw.rectangle([(PH_X, PH_Y_START), (PH_X+PHOTO_W, Y_DATA_END)], outline='lightgray', width=3)

    EMBLEM_SIZE = 130
    E_X = PH_X + (PHOTO_W - EMBLEM_SIZE) // 2
    E_Y = PH_Y_START - EMBLEM_SIZE - 10
    if os.path.exists(logo_path):
        try:
            emblem = Image.open(logo_path).convert("RGBA")
            emblem = ImageOps.fit(emblem, (EMBLEM_SIZE, EMBLEM_SIZE), method=Image.Resampling.LANCZOS)
            img.paste(emblem, (E_X, E_Y), emblem)
        except: pass

    # --- Stripe Data ---
    Y_ROW1 = Y_STRIPE_START + 8
    Y_ROW2 = Y_STRIPE_START + 42
    C_TEXT_ON_STRIPE = (10, 10, 10)
    
    draw.text((DATA_BOX_X + 20, Y_ROW1), "ฉบับที่", font=f_stripe_label_th, fill=C_TEXT_ON_STRIPE)
    draw.text((DATA_BOX_X + 20, Y_ROW2), "No.", font=f_stripe_label_en, fill=C_TEXT_ON_STRIPE)
    
    draw_and_label((DATA_BOX_X + 130, Y_ROW1 - 2), person_data['license_no'], f_stripe_val_num, C_TEXT_ON_STRIPE, "license_no")

    X_TYPE_LABEL = DATA_BOX_X + 380
    X_TYPE_VAL = DATA_BOX_X + 470
    draw.text((X_TYPE_LABEL, Y_ROW1), "ชนิด", font=f_stripe_label_th, fill=C_TEXT_ON_STRIPE)
    draw.text((X_TYPE_LABEL, Y_ROW2), "Type", font=f_stripe_label_en, fill=C_TEXT_ON_STRIPE)
    
    draw_and_label((X_TYPE_VAL, Y_ROW1), person_data['type_th'], f_stripe_val_th, C_TEXT_ON_STRIPE, "type_th")
    draw_and_label((X_TYPE_VAL, Y_ROW2), person_data['type_en'], f_stripe_val_en, C_TEXT_ON_STRIPE, "type_en")

    # --- Main Data ---
    L_X, R_X = DATA_BOX_X + 25, DATA_BOX_X + 350
    OFF_TH, OFF_EN = 160, 120
    Y1 = Y_DATA_START + 15
    LH = 45
    C_RED = (200, 20, 20)
    C_BLACK = (10, 10, 10)

    draw.text((L_X, Y1), "วันอนุญาต", font=f_label, fill=C_RED)
    draw_and_label((L_X+OFF_TH, Y1), person_data['issue_date_th'], f_val_th, C_BLACK, "issue_date_th")

    draw.text((R_X, Y1), "วันหมดอายุ", font=f_label, fill=C_RED)
    draw_and_label((R_X+110, Y1), person_data['expire_date_th'], f_val_th, C_BLACK, "expiry_date_th")

    draw.text((L_X, Y1+LH), "ชื่อ", font=f_label, fill=C_RED)
    draw_and_label((L_X+OFF_TH, Y1+LH-5), person_data['fullname_th'], f_name_th, C_BLACK, "name_th")

    draw.text((L_X, Y1+LH*2), "เกิดวันที่", font=f_label, fill=C_RED)
    draw_and_label((L_X+OFF_TH, Y1+LH*2), person_data['dob_th'], f_val_th, C_BLACK, "dob_th")

    draw.text((L_X, Y1+LH*3), "เลขประจำตัวฯ", font=f_label, fill=C_RED)
    draw_and_label((L_X+OFF_TH+80, Y1+LH*3), person_data['id_card'], f_id, C_BLACK, "id_card")

    DIV_Y = Y1+LH*3 + 40
    draw.line([(DATA_BOX_X, DIV_Y), (DATA_BOX_X + DATA_BOX_W, DIV_Y)], fill='gray', width=1)
    Y_EN = DIV_Y + 15

    draw.text((L_X, Y_EN), "Issue Date", font=f_label, fill=C_RED)
    draw_and_label((L_X+OFF_EN, Y_EN), person_data['issue_date_en'], f_val_en, C_BLACK, "issue_date_en")

    draw.text((R_X, Y_EN), "Expiry Date", font=f_label, fill=C_RED)
    draw_and_label((R_X+120, Y_EN), person_data['expire_date_en'], f_val_en, C_BLACK, "expiry_date_en")

    draw.text((L_X, Y_EN+LH), "Name", font=f_label, fill=C_RED)
    draw_and_label((L_X+80, Y_EN+LH), person_data['fullname_en'], f_val_en, C_BLACK, "name_en")

    draw.text((L_X, Y_EN+LH*2), "Birth Date", font=f_label, fill=C_RED)
    draw_and_label((L_X+OFF_EN, Y_EN+LH*2), person_data['dob_en'], f_val_en, C_BLACK, "dob_en")

    draw.text((R_X, Y_EN+LH*2), "ID No.", font=f_label, fill=C_RED)
    draw_and_label((R_X+80, Y_EN+LH*2), person_data['id_card'], f_val_en, C_BLACK, "id_card_en")

    txt_ft = "นายทะเบียนจังหวัด กรุงเทพมหานคร Bangkok Registrar"
    w_ft = draw.textlength(txt_ft, font=f_footer)
    draw.text(((W-w_ft)/2, Y_FOOTER_START+18), txt_ft, font=f_footer, fill='white')

    # Post-Processing
    img = add_procedural_noise(img, opacity=0.05)
    img = apply_texture_overlay(img, SCRATCH_TEX_FILE, opacity=0.15, blend_mode='screen')
    img = apply_texture_overlay(img, FINGERPRINT_TEX_FILE, opacity=0.10, blend_mode='screen')
    final_img = add_rounded_corners(img, radius=35)

    output_path_png = os.path.splitext(output_path)[0] + ".png"
    final_img.save(output_path_png, "PNG")

    #บันทึก JSON (Labels)
    json_data = {
        "filename": os.path.basename(output_path_png),
        "width": W,
        "height": H,
        "annotations": annotations
    }
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)

    print(f"✅ Generated [{person_data['type_th']}]: {output_path_png}")

# ==========================================
# 5. EXECUTION
# ==========================================
def collect_all_images():
    all_images = []
    print(f"Scanning images from:\n   1. {FACE_SOURCE_M}\n   2. {FACE_SOURCE_FM}")
    
    if os.path.exists(FACE_SOURCE_M):
        for f in os.listdir(FACE_SOURCE_M):
            if f.lower().endswith(('jpg','png','jpeg','webp')):
                all_images.append({'path':os.path.join(FACE_SOURCE_M,f), 'gender':'Man', 'filename':f})
    else:
        print(f"❌ Error: Directory not found -> {FACE_SOURCE_M}")
    
    if os.path.exists(FACE_SOURCE_FM):
        for f in os.listdir(FACE_SOURCE_FM):
            if f.lower().endswith(('jpg','png','jpeg','webp')):
                all_images.append({'path':os.path.join(FACE_SOURCE_FM,f), 'gender':'Woman', 'filename':f})
    else:
         print(f"Error: Directory not found -> {FACE_SOURCE_FM}")
         
    return all_images

if __name__ == "__main__":
    print(f"เริ่มสร้างใบขับขี่คละแบบ (Transport & Private Rules) + JSON Labels...")
    image_pool = collect_all_images()
    
    if len(image_pool) == 0:
        print("ERROR: ไม่พบรูปในโฟลเดอร์ face_M / face_FM")
        sys.exit(1)
        
    print(f"เจอรูป: {len(image_pool)} รูป | เป้าหมาย: {TOTAL_IMAGES_TO_GENERATE} ใบ")
    
    count = 0
    all_license_types = list(LICENSE_CONFIGS.keys())
    
    for i in range(TOTAL_IMAGES_TO_GENERATE):
        selected_img = random.choice(image_pool)
        
        # 1. สุ่มประเภทใบขับขี่
        l_code = random.choice(all_license_types)
        
        # 2. ดึง Config
        spec = LICENSE_CONFIGS[l_code]
        
        # 3. สร้างข้อมูลบุคคล
        p_data = get_smart_data_v2(selected_img['gender'], l_code)
        
        # 4. สร้าง Output Path
        target_group = os.path.join(OUTPUT_ROOT, spec['group_folder'])
        target_images = os.path.join(target_group, "images")
        target_labels = os.path.join(target_group, "labels")

        os.makedirs(target_images, exist_ok=True)
        os.makedirs(target_labels, exist_ok=True)
        
        root_name, ext = os.path.splitext(selected_img['filename'])
        file_id = f"Lic_{l_code}_{i+1:04d}_{selected_img['gender']}_{root_name}"
        
        out_img_path = os.path.join(target_images, f"{file_id}.png")
        out_json_path = os.path.join(target_labels, f"{file_id}.json")
        
        # 5. Generate (ส่ง json path ไปด้วย)
        generate_card(out_img_path, p_data, selected_img['path'], LOGO_FILE, out_json_path)
        
        count += 1
        if count % 10 == 0: print(f"สร้างไปแล้ว {count}/{TOTAL_IMAGES_TO_GENERATE}...")

    print(f"เสร็จสมบูรณ์! แยกไฟล์ Images/Labels ไว้ที่: {OUTPUT_ROOT}")