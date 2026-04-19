import os
import random
import csv
import math
import colorsys
import subprocess
import sys
from datetime import datetime, timedelta

# ติดตั้ง Library ที่จำเป็นถ้ายังไม่มี
try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
TOTAL_IMAGES_TO_GENERATE = 500

# ==========================================
# 1. SETUP PATHS
# ==========================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

# Assets Paths
ASSETS_DIR = "/project/lt200393-foullm/Yanakorn_Peach/Dataset/Driving_license/assets"
FONT_BOLD_FILE = os.path.join(ASSETS_DIR, "front", "Sarabun-Bold.ttf")
# ใช้โลโก้กรมขนส่งเป็นแม่แบบลายน้ำ (ตามโค้ด Colab)
LOGO_FILE = os.path.join(ASSETS_DIR, "logo", "dltLogo.png.webp")

# Input/Output Data Path
DATA_ROOT_DIR = "/project/lt200393-foullm/Yanakorn_Peach/Dataset/Driving_license/data"
OUTPUT_DIR = "/project/lt200393-foullm/Yanakorn_Peach/Dataset/Driving_license/output_test"
if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

# ==========================================
# 2. NAME DATABASE
# ==========================================
MALE_NAMES_TH = ["สมชาย", "วิชัย", "อาทิตย์", "ก้องภพ", "ธีรเทพ", "ณัฐพงษ์", "ศิริ", "ประวิทย์", "กล้า", "ทนง", "บวร", "ชัย", "ธนพล", "ภูผา", "วายุ"]
MALE_NAMES_EN = ["Somchai", "Wichai", "Arthit", "Kongpop", "Teerathep", "Nattapong", "Siri", "Prawit", "Kla", "Tanong", "Bowon", "Chai", "Tanapon", "Phupha", "Wayu"]
FEMALE_NAMES_TH = ["สมหญิง", "สุดา", "กนกวรรณ", "มารี", "แพรวา", "รัตนา", "นภา", "วิไล", "อารียา", "น้ำทิพย์", "กานดา", "พรทิพย์", "เมษา", "ฟ้าใส"]
FEMALE_NAMES_EN = ["Somying", "Suda", "Kanokwan", "Malee", "Praewa", "Rattana", "Napa", "Wilai", "Areeya", "Namthip", "Kanda", "Porntip", "Maysa", "Fahsai"]
SURNAMES_TH = ["ใจดี", "รักชาติ", "มีสุข", "เจริญ", "มั่นคง", "ทองดี", "สุขเกษม", "วิจิตร", "ณ บางช้าง", "สืบสกุล", "วงศ์สวัสดิ์", "เลิศล้ำ"]
SURNAMES_EN = ["Jaidee", "Rakchart", "Meesuk", "Charoen", "Mankong", "Thongdee", "Sukkasem", "Wichit", "Na Bangchang", "Suebsakul", "Wongsawat", "Lertlum"]

# ==========================================
# 3. METALLIC HOLOGRAM ENGINE (จาก Colab)
# ==========================================

def generate_metallic_texture(size):
    """ สร้าง Texture สีรุ้งแบบโลหะ ด้วยคณิตศาสตร์ (ตามโค้ด Colab) """
    w, h = size, size
    texture = Image.new('RGBA', (w, h))
    pixels = texture.load()
    frequency = 3.0 # ความถี่ของคลื่นสี
    
    for y in range(h):
        for x in range(w):
            # คำนวณตำแหน่งสีแบบทะแยงมุม (Diagonal)
            pos = (x + y) / (w + h) * frequency
            hue = pos % 1.0
            
            # คำนวณความเงา (Shine) ด้วย Sine Wave
            shine = math.sin(pos * math.pi * 2)
            
            saturation = 1.0
            value = 1.0
            
            # ถ้าเป็นช่วงเงาวาว ให้ลดความสดสีลงเพื่อให้ดูขาวขึ้น (Metallic Effect)
            if shine > 0.8:
                saturation = 1.0 - ((shine - 0.8) * 4)
                value = 1.0
            
            r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
            pixels[x, y] = (int(r * 255), int(g * 255), int(b * 255), 255)
            
    return texture

def create_shiny_foil_stamp(emblem_path, size):
    """ สร้างลายน้ำโฮโลแกรม โดยใช้รูปทรงจากไฟล์ Logo """
    # ถ้าไม่มีไฟล์ Logo ให้สร้างวงกลมแทน (เผื่อกรณีหาไฟล์ไม่เจอ)
    if not os.path.exists(emblem_path):
        mask_img = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask_img)
        draw.ellipse((10, 10, size-10, size-10), fill=255)
        alpha_mask = mask_img
    else:
        try:
            # โหลด Logo มาทำเป็นหน้ากาก (Mask)
            original = Image.open(emblem_path).convert("RGBA")
            mask_img = ImageOps.fit(original, (size, size), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            alpha_mask = mask_img.split()[3] # เอาเฉพาะ Alpha channel
        except:
            return None

    # สร้างเนื้อสีรุ้ง
    foil_texture = generate_metallic_texture(size)
    
    # ตัดเนื้อสีรุ้งให้เป็นรูปร่างตาม Mask
    shiny_stamp = Image.new("RGBA", (size, size), (0,0,0,0))
    shiny_stamp.paste(foil_texture, (0,0), alpha_mask)
    
    # ปรับความโปร่งแสง (Opacity) ตรงนี้
    r, g, b, a = shiny_stamp.split()
    a = a.point(lambda i: int(i * 0.35)) # 0.35 คือความเข้ม (ปรับตาม Colab)
    shiny_stamp.putalpha(a)
    
    return shiny_stamp

def apply_holo_foil_pattern(base_img, emblem_path):
    """ ปูพรมลายน้ำทั่วภาพ (Tiling) """
    W, H = base_img.size
    overlay_layer = Image.new("RGBA", (W, H), (0,0,0,0))
    
    # ตั้งค่าระยะห่างและขนาดตาม Colab
    stamp_size = 140
    spacing_x = 240
    spacing_y = 220
    
    stamp = create_shiny_foil_stamp(emblem_path, stamp_size)
    if not stamp: return base_img
    
    row_count = 0
    # Loop ปูพื้นลายน้ำ
    for y in range(-50, H, spacing_y):
        # ขยับแถวคู่/คี่ให้สลับฟันปลา
        offset_x = (spacing_x // 2) if (row_count % 2 == 1) else 0
        for x in range(-50 - offset_x, W, spacing_x):
            overlay_layer.paste(stamp, (x, y), stamp)
        row_count += 1
        
    # รวมภาพแบบ Alpha Composite
    final_comp = Image.alpha_composite(base_img.convert("RGBA"), overlay_layer)
    
    # เร่งสีให้สดขึ้นนิดนึง (ตาม Colab)
    enhancer = ImageEnhance.Color(final_comp)
    final_comp = enhancer.enhance(1.2)
    
    return final_comp.convert("RGB")

def create_sunset_texture(width, height):
    base = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(base)
    for y in range(height):
        r = y / height
        if r < 0.35: ratio = r/0.35; c=(int(140+(60*ratio)), int(150+(40*ratio)), int(230-(20*ratio)))
        elif r < 0.75: ratio = (r-0.35)/0.4; c=(int(200+(55*ratio)), int(190+(40*ratio)), int(210-(30*ratio)))
        else: ratio = (r-0.75)/0.25; c=(255, int(230+(25*ratio)), int(180+(20*ratio)))
        draw.line([(0, y), (width, y)], fill=c)
    return base

# ==========================================
# 4. CARD GENERATOR MAIN
# ==========================================

def generate_card(output_path, person_data, photo_path, logo_path):
    W, H = 1012, 638
    img = Image.new('RGB', (W, H), 'white')
    draw = ImageDraw.Draw(img) # เตรียมวาด (แต่ยังไม่วาด Text)

    # --- LAYOUT CONSTANTS ---
    HEADER_H = 105
    FOOTER_H = 65
    Y_FOOTER_START = H - FOOTER_H
    DATA_BOX_X = 300
    DATA_BOX_W = W - 300 - 20
    Y_PURPLE_START = HEADER_H + 20
    Y_PURPLE_END = Y_PURPLE_START + 80
    Y_DATA_START = Y_PURPLE_END + 12
    Y_DATA_END = Y_FOOTER_START - 12
    DATA_H = Y_DATA_END - Y_DATA_START

    # 1. วาดพื้นหลัง Sunset
    bg_texture = create_sunset_texture(DATA_BOX_W, DATA_H)
    full_bg = Image.new('RGB', (W, H), 'white')
    full_bg.paste(bg_texture, (DATA_BOX_X, Y_DATA_START))
    img.paste(full_bg, (0,0))

    # =========================================================
    # 🔥 จุดเปลี่ยนสำคัญ: ใส่ลายน้ำโฮโลแกรมตรงนี้ (ก่อนวาดแถบสีทับ) 🔥
    # =========================================================
    img = apply_holo_foil_pattern(img, logo_path)
    # =========================================================

    draw = ImageDraw.Draw(img) # Re-init draw เพื่อวาดทับ

    # 2. วาดแถบสีและกรอบ (จะทับลายน้ำไปบางส่วน ตามสไตล์บัตรจริง)
    C_BLUE = (16, 45, 115)
    C_PURPLE = (155, 140, 215)
    draw.rectangle([(0, 0), (W, HEADER_H)], fill=C_BLUE)
    draw.rectangle([(0, Y_FOOTER_START), (W, H)], fill=C_BLUE)
    draw.rectangle([(DATA_BOX_X, Y_PURPLE_START), (DATA_BOX_X + DATA_BOX_W, Y_PURPLE_END)], fill=C_PURPLE)
    draw.rectangle([(DATA_BOX_X, Y_DATA_START), (DATA_BOX_X + DATA_BOX_W, Y_DATA_END)], outline='gray', width=1)

    # 3. ใส่ธงชาติ
    draw.rectangle([(30, 20), (120, 80)], fill='white')
    draw.rectangle([(30, 20), (120, 30)], fill=(200,0,0))
    draw.rectangle([(30, 70), (120, 80)], fill=(200,0,0))
    draw.rectangle([(30, 40), (120, 60)], fill=(0,0,140))

    # --- FONTS SETUP ---
    try:
        f_h_th = ImageFont.truetype(FONT_BOLD_FILE, 36)
        f_h_en = ImageFont.truetype(FONT_BOLD_FILE, 22)
        f_label = ImageFont.truetype(FONT_BOLD_FILE, 22)
        f_val_th = ImageFont.truetype(FONT_BOLD_FILE, 24)
        f_val_en = ImageFont.truetype(FONT_BOLD_FILE, 20)
        f_name_th = ImageFont.truetype(FONT_BOLD_FILE, 32)
        f_id = ImageFont.truetype(FONT_BOLD_FILE, 26)
        f_footer = ImageFont.truetype(FONT_BOLD_FILE, 26)
        
        f_purple_label_th = ImageFont.truetype(FONT_BOLD_FILE, 28)
        f_purple_label_en = ImageFont.truetype(FONT_BOLD_FILE, 18)
        f_purple_val_num = ImageFont.truetype(FONT_BOLD_FILE, 36)
        f_purple_val_th = ImageFont.truetype(FONT_BOLD_FILE, 28)
        f_purple_val_en = ImageFont.truetype(FONT_BOLD_FILE, 22)
    except:
        print(f"❌ Font Error: เช็ค Path {FONT_BOLD_FILE}")
        return

    # --- TEXT HEADER ---
    draw.text((140, 18), "ประเทศไทย", font=f_h_th, fill='white')
    draw.text((140, 60), "Kingdom of Thailand", font=f_h_en, fill='white')
    txt_th = "ใบอนุญาตขับรถส่วนบุคคล"
    txt_en = "Private Car Driving Licence"
    w_th = draw.textlength(txt_th, font=f_h_th)
    w_en = draw.textlength(txt_en, font=f_h_en)
    draw.text((W - w_th - 30, 18), txt_th, font=f_h_th, fill='white')
    draw.text((W - w_en - 30, 60), txt_en, font=f_h_en, fill='white')

    # --- PHOTO ---
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

    # Emblem (Logo จริงมุมซ้ายบนรูป)
    EMBLEM_SIZE = 130
    E_X = PH_X + (PHOTO_W - EMBLEM_SIZE) // 2
    E_Y = PH_Y_START - EMBLEM_SIZE - 10
    if os.path.exists(logo_path):
        try:
            emblem = Image.open(logo_path).convert("RGBA")
            emblem = ImageOps.fit(emblem, (EMBLEM_SIZE, EMBLEM_SIZE), method=Image.Resampling.LANCZOS)
            img.paste(emblem, (E_X, E_Y), emblem)
        except: pass

    # --- DETAILS ---
    Y_ROW1 = Y_PURPLE_START + 8
    Y_ROW2 = Y_PURPLE_START + 42
    draw.text((DATA_BOX_X + 20, Y_ROW1), "ฉบับที่", font=f_purple_label_th, fill='white')
    draw.text((DATA_BOX_X + 20, Y_ROW2), "No.", font=f_purple_label_en, fill='white')
    draw.text((DATA_BOX_X + 130, Y_ROW1 - 2), person_data['license_no'], font=f_purple_val_num, fill='white')

    X_TYPE_LABEL = DATA_BOX_X + 380
    X_TYPE_VAL = DATA_BOX_X + 470
    draw.text((X_TYPE_LABEL, Y_ROW1), "ชนิด", font=f_purple_label_th, fill='white')
    draw.text((X_TYPE_LABEL, Y_ROW2), "Type", font=f_purple_label_en, fill='white')
    draw.text((X_TYPE_VAL, Y_ROW1), "รถยนต์ส่วนบุคคล", font=f_purple_val_th, fill='white')
    draw.text((X_TYPE_VAL, Y_ROW2), "Private Car", font=f_purple_val_en, fill='white')

    L_X, R_X = DATA_BOX_X + 25, DATA_BOX_X + 350
    OFF_TH, OFF_EN = 160, 120
    Y1 = Y_DATA_START + 15
    LH = 45
    C_RED = (200, 20, 20)
    C_BLACK = (10, 10, 10)

    # Thai Info
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

    # Eng Info
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

    img.save(output_path, quality=95)
    print(f"✅ Generated: {output_path}")

# ==========================================
# 5. DATA HELPER
# ==========================================
def convert_date_th(dt_obj):
    th_m = ['','ม.ค.','ก.พ.','มี.ค.','เม.ย.','พ.ค.','มิ.ย.','ก.ค.','ส.ค.','ก.ย.','ต.ค.','พ.ย.','ธ.ค.']
    return f"{dt_obj.day} {th_m[dt_obj.month]} {dt_obj.year+543}"

def get_smart_data(gender):
    idx_sur = random.randint(0, len(SURNAMES_TH)-1)
    if gender == 'Man':
        idx_n = random.randint(0, len(MALE_NAMES_TH)-1)
        title_th, title_en = "นาย", "Mr."
        fname_th, fname_en = MALE_NAMES_TH[idx_n], MALE_NAMES_EN[idx_n]
    else:
        idx_n = random.randint(0, len(FEMALE_NAMES_TH)-1)
        title_th, title_en = "น.ส.", "Ms."
        fname_th, fname_en = FEMALE_NAMES_TH[idx_n], FEMALE_NAMES_EN[idx_n]
        
    curr = datetime.now()
    issue = curr - timedelta(days=random.randint(0, 365))
    expire = issue + timedelta(days=365*5)
    dob = curr - timedelta(days=365*random.randint(20, 40))

    return {
        "fullname_th": f"{title_th} {fname_th}  {SURNAMES_TH[idx_sur]}",
        "fullname_en": f"{title_en} {fname_en}  {SURNAMES_EN[idx_sur]}",
        "license_no": f"{random.randint(10,99)} {random.randint(10000,99999)}",
        "id_card": f"{random.randint(1,9)} {random.randint(1000,9999)} {random.randint(10000,99999)} {random.randint(10,99)} {random.randint(0,9)}",
        "issue_date_th": convert_date_th(issue),
        "issue_date_en": issue.strftime("%d %B %Y"),
        "expire_date_th": convert_date_th(expire),
        "expire_date_en": expire.strftime("%d %B %Y"),
        "dob_th": convert_date_th(dob),
        "dob_en": dob.strftime("%d %B %Y")
    }

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

# ==========================================
# 6. MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print(f"🚀 เริ่มสร้างใบขับขี่ (Colab Metallic Hologram Style)...")
    
    image_pool = collect_all_images()
    
    if len(image_pool) == 0:
        print("❌ Error: ไม่เจอรูปเลยสักใบ! เช็ค Path โฟลเดอร์ data อีกทีนะครับ")
        exit()
        
    print(f"📦 เจอรูปต้นฉบับ: {len(image_pool)} รูป | เป้าหมาย: {TOTAL_IMAGES_TO_GENERATE} ใบ")
    
    count = 0
    for i in range(TOTAL_IMAGES_TO_GENERATE):
        selected_img = random.choice(image_pool) 
        p_data = get_smart_data(selected_img['gender'])
        
        root_name, ext = os.path.splitext(selected_img['filename'])
        new_filename = f"Lic_ColabHolo_{i+1:04d}_{selected_img['gender']}_{root_name}{ext}"
        out_path = os.path.join(OUTPUT_DIR, new_filename)
        
        generate_card(out_path, p_data, selected_img['path'], LOGO_FILE)
        
        count += 1
        if count % 10 == 0: print(f"⏳ สร้างไปแล้ว {count}...")

    print(f"✨ เสร็จสมบูรณ์! เช็คผลลัพธ์ที่: {OUTPUT_DIR}")