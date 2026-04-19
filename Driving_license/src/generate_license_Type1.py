import os
import random
import csv
import math
import colorsys
import subprocess
import sys
from datetime import datetime, timedelta

# ติดตั้ง Library ที่จำเป็น
try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter, ImageChops
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter, ImageChops


TOTAL_IMAGES_TO_GENERATE = 1
ASSETS_DIR = "/project/lt200393-foullm/Yanakorn_Peach/Dataset/Driving_license/assets"
FONT_BOLD_FILE = os.path.join(ASSETS_DIR, "front", "Sarabun-Bold.ttf")
LOGO_FILE = os.path.join(ASSETS_DIR, "logo", "dltLogo.png.webp")
SCRATCH_TEX_FILE = os.path.join(ASSETS_DIR, "textures", "scratches_01.jpg") 
FINGERPRINT_TEX_FILE = os.path.join(ASSETS_DIR, "textures", "fingerprints_01.jpg")

# Text Data Paths
NAME_FILE_PATH = "/project/lt200393-foullm/Yanakorn_Peach/Dataset/Driving_license/assets/name_surname/thai_names_converted_TH_EN.txt"
SURNAME_FILE_PATH = "/project/lt200393-foullm/Yanakorn_Peach/Dataset/Driving_license/assets/name_surname/thai_surnames_TH_EN.txt"

# Input/Output Data Path
DATA_ROOT_DIR = "/project/lt200393-foullm/Yanakorn_Peach/Dataset/Driving_license/data"
OUTPUT_DIR = "/project/lt200393-foullm/Yanakorn_Peach/Dataset/Driving_license/output_t1_realistic"
if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

# Fallback Data
FALLBACK_MALE_NAMES = [("สมชาย", "Somchai"), ("วิชัย", "Wichai"), ("ณัฐพงษ์", "Nattapong")]
FALLBACK_FEMALE_NAMES = [("สมหญิง", "Somying"), ("สุดา", "Suda"), ("รัตนา", "Rattana")]
FALLBACK_SURNAMES = [("ใจดี", "Jaidee"), ("มีสุข", "Meesuk")]

# ==========================================
# 2. LOGIC FIXES & UTILS (เหมือนเดิม)
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
                parts = line.strip().split(',')
                if len(parts) < 2: parts = line.strip().split('\t')
                if len(parts) >= 2: data.append((parts[0].strip(), parts[1].strip()))
    except: return None
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

RAW_NAMES = load_names_from_file(NAME_FILE_PATH)
RAW_SURNAMES = load_names_from_file(SURNAME_FILE_PATH)

def get_smart_data_v2(gender_from_image):
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
    dob = curr - timedelta(days=365*random.randint(25, 55) + random.randint(0, 360))
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
        "dob_en": dob.strftime("%d %B %Y")
    }

# ==========================================
# 3. GRAPHIC ENGINE (Hologram & Template)
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
            if shine > 0.8:
                saturation = 1.0 - ((shine - 0.8) * 4)
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
    """ ตัดมุมภาพให้โค้งมน และคืนค่าเป็น RGBA """
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
    img_rgba = img.convert("RGBA")
    img_rgba.putalpha(mask)
    return img_rgba

def apply_texture_overlay(base_img, texture_path, opacity=0.15, blend_mode='overlay'):
    """ ซ้อนทับ Texture (รอยขีดข่วน/นิ้วมือ) จากไฟล์ภายนอก """
    if not os.path.exists(texture_path):
        return base_img
        
    try:
        # โหลด Texture และปรับขนาด
        texture = Image.open(texture_path).convert("L")
        texture = ImageOps.fit(texture, base_img.size, method=Image.Resampling.LANCZOS)
        
        # สร้าง Layer สำหรับ Overlay
        overlay = Image.new('RGBA', base_img.size, (0,0,0,0))
        
        if blend_mode == 'multiply':
            # สำหรับรอยขีดข่วนมืดๆ (Dark scratches)
            inverted_tex = ImageOps.invert(texture)
            final_alpha = inverted_tex.point(lambda p: int(p * opacity))
            overlay.putalpha(final_alpha)
            
        elif blend_mode == 'screen' or blend_mode == 'overlay':
            # สำหรับรอยนิ้วมือ/รอยขีดข่วนขาวๆ (Light scratches/prints)
            # ใช้สีขาวเป็นหลัก แล้วเอาความสว่างของ texture มาเป็น alpha
            draw = ImageDraw.Draw(overlay)
            draw.rectangle([(0,0), base_img.size], fill=(255,255,255))
            final_alpha = texture.point(lambda p: int(p * opacity)) # ปรับความจาง
            overlay.putalpha(final_alpha)
            
        # รวม Layer
        return Image.alpha_composite(base_img.convert("RGBA"), overlay)
        
    except Exception as e:
        print(f"❌ Error applying texture: {e}")
        return base_img

def add_procedural_noise(img, opacity=0.04):
    """ เพิ่ม Noise/Grain แบบสร้างเอง (ไม่ต้องใช้ไฟล์) """
    W, H = img.size
    noise_img = Image.new("RGBA", (W, H))
    pixels = noise_img.load()
    for y in range(H):
        for x in range(W):
            # สร้างเม็ดสีเทาแบบสุ่ม
            grain = random.randint(100, 150) 
            # ความโปร่งใสแบบสุ่ม
            alpha = int(opacity * 255 * (random.random() * 0.5 + 0.5))
            pixels[x, y] = (grain, grain, grain, alpha)
            
    return Image.alpha_composite(img.convert("RGBA"), noise_img)


# ==========================================
# 4. CARD GENERATOR MAIN (To.1 Style)
# ==========================================
def generate_card(output_path, person_data, photo_path, logo_path):
    W, H = 1012, 638
    img = Image.new('RGB', (W, H), 'white')
    
    # ... (ส่วนการวาดพื้นฐาน เหมือนเดิมทุกประการ) ...
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
    C_YELLOW_T1 = (240, 180, 50)
    draw.rectangle([(0, 0), (W, HEADER_H)], fill=C_BLUE)
    draw.rectangle([(0, Y_FOOTER_START), (W, H)], fill=C_BLUE)
    draw.rectangle([(DATA_BOX_X, Y_STRIPE_START), (DATA_BOX_X + DATA_BOX_W, Y_STRIPE_END)], fill=C_YELLOW_T1) 
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
        print(f"Font Error: {FONT_BOLD_FILE}"); return

    draw.text((140, 18), "ประเทศไทย", font=f_h_th, fill='white')
    draw.text((140, 60), "Kingdom of Thailand", font=f_h_en, fill='white')
    txt_th = "ใบอนุญาตเป็นผู้ขับรถ" 
    txt_en = "Driver's License" 
    w_th = draw.textlength(txt_th, font=f_h_th)
    w_en = draw.textlength(txt_en, font=f_h_en)
    draw.text((W - w_th - 30, 18), txt_th, font=f_h_th, fill='white')
    draw.text((W - w_en - 30, 60), txt_en, font=f_h_en, fill='white')

    PH_X, PH_H_SIZE = 35, 310
    PH_Y_START = Y_DATA_END - PH_H_SIZE
    PHOTO_W = 250
    if os.path.exists(photo_path):
        try:
            user_img = Image.open(photo_path).convert("RGB")
            user_img = ImageOps.fit(user_img, (PHOTO_W, PH_H_SIZE), method=Image.Resampling.LANCZOS)
            img.paste(user_img, (PH_X, PH_Y_START))
        except: pass
    else:
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

    Y_ROW1 = Y_STRIPE_START + 8
    Y_ROW2 = Y_STRIPE_START + 42
    C_TEXT_ON_YELLOW = (10, 10, 10)
    draw.text((DATA_BOX_X + 20, Y_ROW1), "ฉบับที่", font=f_stripe_label_th, fill=C_TEXT_ON_YELLOW)
    draw.text((DATA_BOX_X + 20, Y_ROW2), "No.", font=f_stripe_label_en, fill=C_TEXT_ON_YELLOW)
    draw.text((DATA_BOX_X + 130, Y_ROW1 - 2), person_data['license_no'], font=f_stripe_val_num, fill=C_TEXT_ON_YELLOW)
    X_TYPE_LABEL = DATA_BOX_X + 380
    X_TYPE_VAL = DATA_BOX_X + 470
    draw.text((X_TYPE_LABEL, Y_ROW1), "ชนิด", font=f_stripe_label_th, fill=C_TEXT_ON_YELLOW)
    draw.text((X_TYPE_LABEL, Y_ROW2), "Type", font=f_stripe_label_en, fill=C_TEXT_ON_YELLOW)
    draw.text((X_TYPE_VAL, Y_ROW1), "ทุกประเภท ชนิดที่ 1", font=f_stripe_val_th, fill=C_TEXT_ON_YELLOW)
    draw.text((X_TYPE_VAL, Y_ROW2), "Every Type One", font=f_stripe_val_en, fill=C_TEXT_ON_YELLOW)

    L_X, R_X = DATA_BOX_X + 25, DATA_BOX_X + 350
    OFF_TH, OFF_EN = 160, 120
    Y1 = Y_DATA_START + 15
    LH = 45
    C_RED = (200, 20, 20)
    C_BLACK = (10, 10, 10)
    draw.text((L_X, Y1), "วันอนุญาต", font=f_label, fill=C_RED)
    draw.text((L_X+OFF_TH, Y1), person_data['issue_date_th'], font=f_val_th, fill=C_BLACK)
    draw.text((R_X, Y1), "วันหมดอายุ", font=f_label, fill=C_RED)
    draw.text((R_X+110, Y1), person_data['expire_date_th'], font=f_val_th, fill=C_BLACK)
    draw.text((L_X, Y1+LH), "ชื่อ", font=f_label, fill=C_RED)
    draw.text((L_X+OFF_TH, Y1+LH-5), person_data['fullname_th'], font=f_name_th, fill=C_BLACK)
    draw.text((L_X, Y1+LH*2), "เกิดวันที่", font=f_label, fill=C_RED)
    draw.text((L_X+OFF_TH, Y1+LH*2), person_data['dob_th'], font=f_val_th, fill=C_BLACK)
    draw.text((L_X, Y1+LH*3), "เลขประจำตัวฯ", font=f_label, fill=C_RED)
    draw.text((L_X+OFF_TH+80, Y1+LH*3), person_data['id_card'], font=f_id, fill=C_BLACK)
    DIV_Y = Y1+LH*3 + 40
    draw.line([(DATA_BOX_X, DIV_Y), (DATA_BOX_X + DATA_BOX_W, DIV_Y)], fill='gray', width=1)
    Y_EN = DIV_Y + 15
    draw.text((L_X, Y_EN), "Issue Date", font=f_label, fill=C_RED)
    draw.text((L_X+OFF_EN, Y_EN), person_data['issue_date_en'], font=f_val_en, fill=C_BLACK)
    draw.text((R_X, Y_EN), "Expiry Date", font=f_label, fill=C_RED)
    draw.text((R_X+120, Y_EN), person_data['expire_date_en'], font=f_val_en, fill=C_BLACK)
    draw.text((L_X, Y_EN+LH), "Name", font=f_label, fill=C_RED)
    draw.text((L_X+80, Y_EN+LH), person_data['fullname_en'], font=f_val_en, fill=C_BLACK)
    draw.text((L_X, Y_EN+LH*2), "Birth Date", font=f_label, fill=C_RED)
    draw.text((L_X+OFF_EN, Y_EN+LH*2), person_data['dob_en'], font=f_val_en, fill=C_BLACK)
    draw.text((R_X, Y_EN+LH*2), "ID No.", font=f_label, fill=C_RED)
    draw.text((R_X+80, Y_EN+LH*2), person_data['id_card'], font=f_val_en, fill=C_BLACK)
    txt_ft = "นายทะเบียนจังหวัด กรุงเทพมหานคร Bangkok Registrar"
    w_ft = draw.textlength(txt_ft, font=f_footer)
    draw.text(((W-w_ft)/2, Y_FOOTER_START+18), txt_ft, font=f_footer, fill='white')
    # 1. เพิ่ม Noise/Grain บางๆ (สร้างเอง ไม่ต้องใช้ไฟล์)
    img = add_procedural_noise(img, opacity=0.05)

    # 2. เพิ่ม Micro-scratches (ต้องการไฟล์ Texture, ถ้าไม่มีจะข้าม)
    # ใช้ blend_mode='screen' หรือ 'overlay' สำหรับรอยขาวๆ บนพื้นเข้ม
    img = apply_texture_overlay(img, SCRATCH_TEX_FILE, opacity=0.15, blend_mode='screen')

    # 3. เพิ่ม Fingerprints (ต้องการไฟล์ Texture, ถ้าไม่มีจะข้าม)
    img = apply_texture_overlay(img, FINGERPRINT_TEX_FILE, opacity=0.10, blend_mode='screen')

    # 4. ตัดมุมโค้งมน (Rounded Corners) เป็นขั้นตอนสุดท้าย
    final_img = add_rounded_corners(img, radius=10)

    output_path_png = os.path.splitext(output_path)[0] + ".png"
    final_img.save(output_path_png, "PNG")
    print(f"✅ Generated Realistic To.1: {output_path_png}")

# ==========================================
# 5. EXECUTION
# ==========================================
def collect_all_images():
    all_images = []
    path_m = os.path.join(DATA_ROOT_DIR, "face_M")
    if os.path.exists(path_m):
        for f in os.listdir(path_m):
            if f.lower().endswith(('jpg','png','jpeg','webp')):
                all_images.append({'path':os.path.join(path_m,f), 'gender':'Man', 'filename':f})
    
    path_fm = os.path.join(DATA_ROOT_DIR, "face_FM")
    if os.path.exists(path_fm):
        for f in os.listdir(path_fm):
            if f.lower().endswith(('jpg','png','jpeg','webp')):
                all_images.append({'path':os.path.join(path_fm,f), 'gender':'Woman', 'filename':f})
    return all_images

if __name__ == "__main__":
    print(f"🚀 เริ่มสร้างใบขับขี่ ท.1 (Realistic Style)...")
    image_pool = collect_all_images()
    if len(image_pool) == 0:
        print("❌ Error: ไม่เจอรูป face_M / face_FM เลยครับ")
        exit()
        
    print(f"เจอรูปต้นฉบับ: {len(image_pool)} รูป | เป้าหมาย: {TOTAL_IMAGES_TO_GENERATE} ใบ")
    
    count = 0
    for i in range(TOTAL_IMAGES_TO_GENERATE):
        selected_img = random.choice(image_pool) 
        p_data = get_smart_data_v2(selected_img['gender'])
        root_name, ext = os.path.splitext(selected_img['filename'])
        # ตั้งชื่อไฟล์เป็น .png (แต่ตัวฟังก์ชันจะแก้ให้อีกที)
        new_filename = f"Lic_T1_Real_{i+1:04d}_{selected_img['gender']}_{root_name}.png"
        out_path = os.path.join(OUTPUT_DIR, new_filename)
        
        generate_card(out_path, p_data, selected_img['path'], LOGO_FILE)
        
        count += 1
        if count % 1 == 0: print(f"⏳ สร้างไปแล้ว {count}...")

    print(f"✨ เสร็จสมบูรณ์! เช็คผลลัพธ์ (.png) ที่: {OUTPUT_DIR}")