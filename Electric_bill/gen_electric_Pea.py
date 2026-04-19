import os
import random
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from barcode import Code128
from barcode.writer import ImageWriter
import qrcode

# ==========================================
# 1. กำหนด Path ต่างๆ
# ==========================================
FONT_DIR = "/project/lt200393-foullm/Yanakorn_Peach/Dataset/Electric_bill/assets/front"
TEMPLATE_FILE = "/project/lt200393-foullm/Yanakorn_Peach/Dataset/Electric_bill/assets/template/ใบเสร็จการไฟฟ้า.jpg"
NAME_FILE = "/project/lt200393-foullm/Yanakorn_Peach/Dataset/Electric_bill/assets/name_surname/thai_names_converted_TH_EN.txt"
SURNAME_FILE = "/project/lt200393-foullm/Yanakorn_Peach/Dataset/Electric_bill/assets/name_surname/thai_surnames_TH_EN.txt"
OUTPUT_DIR = "บิลการไฟฟ้า_500_รูป"

os.makedirs(f"{OUTPUT_DIR}/images", exist_ok=True)

VALID_LOCATIONS = [
    {"tam": "หนองบัวแดง", "amp": "หนองบัวแดง", "prov": "ชัยภูมิ", "zip": "36210"},
    {"tam": "ในเมือง", "amp": "เมืองขอนแก่น", "prov": "ขอนแก่น", "zip": "40000"},
    {"tam": "ปากเกร็ด", "amp": "ปากเกร็ด", "prov": "นนทบุรี", "zip": "11120"},
    {"tam": "แสนสุข", "amp": "เมืองชลบุรี", "prov": "ชลบุรี", "zip": "20130"},
    {"tam": "แม่สาย", "amp": "แม่สาย", "prov": "เชียงราย", "zip": "57130"},
    {"tam": "หาดใหญ่", "amp": "หาดใหญ่", "prov": "สงขลา", "zip": "90110"},
    {"tam": "ป่าตอง", "amp": "กะทู้", "prov": "ภูเก็ต", "zip": "83150"},
    {"tam": "หัวหิน", "amp": "หัวหิน", "prov": "ประจวบคีรีขันธ์", "zip": "77110"},
    {"tam": "เมืองเก่า", "amp": "เมืองสุโขทัย", "prov": "สุโขทัย", "zip": "64210"},
    {"tam": "นางรอง", "amp": "นางรอง", "prov": "บุรีรัมย์", "zip": "31110"}
]

# ==========================================
# 2. ฟังก์ชันโหลดไฟล์ชื่อ-นามสกุล
# ==========================================
def load_names_from_file(filepath):
    names = []
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.replace('|', ' ').replace(',', ' ').split()
                    if parts:
                        names.append(parts[0]) # เก็บคำแรกของบรรทัด
            print(f"✅ โหลดไฟล์ {os.path.basename(filepath)} สำเร็จ ({len(names)} รายการ)")
        except Exception as e:
            print(f"❌ อ่านไฟล์ {os.path.basename(filepath)} ไม่ได้: {e}")
    else:
        print(f"⚠️ ไม่พบไฟล์: {filepath}")
    return names

FIRST_NAMES_DB = load_names_from_file(NAME_FILE)
SURNAMES_DB = load_names_from_file(SURNAME_FILE)

# ==========================================
# 3. ฟังก์ชัน Helper จัดการภาพและข้อมูล
# ==========================================
def make_transparent(img):
    """เปลี่ยนสีขาวให้เป็นสีโปร่งใส"""
    img = img.convert("RGBA")
    datas = img.getdata()
    new_data = []
    for item in datas:
        if item[0] > 200 and item[1] > 200 and item[2] > 200:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)
    return img

def format_thai_date_short(dt_obj):
    thai_year = (dt_obj.year + 543) % 100
    return f"{dt_obj.day:02d}/{dt_obj.month:02d}/{thai_year:02d}"

def generate_bill_data():
    loc = random.choice(VALID_LOCATIONS)
    district, province, zipcode, tambon = loc["amp"], loc["prov"], loc["zip"], loc["tam"]

    pea_branch_name = f"การไฟฟ้า{district}" if "อำเภอ" in district else f"การไฟฟ้าอำเภอ{district}"
    address_line = f"{random.randint(1,999)}/{random.randint(1,99)} หมู่ {random.randint(1,15)} ต.{tambon} อ.{district} จ.{province} {zipcode}"

    # --- สุ่มชื่อจากไฟล์ที่โหลดมา ---
    if FIRST_NAMES_DB and SURNAMES_DB:
        fname = random.choice(FIRST_NAMES_DB)
        lname = random.choice(SURNAMES_DB)
        prefix = random.choice(["นาย", "นาง", "นางสาว"])
        customer_name = f"{prefix} {fname} {lname}"
    else:
        customer_name = "นาย สมชาย ใจดี" # ชื่อสำรองกรณีหาไฟล์ไม่เจอ

    year_ad = random.randint(2024, 2026)
    month = random.randint(1, 12)
    bill_period = f"{month:02d}/{year_ad+543}"

    try:
        read_date_obj = datetime(year_ad, month, random.randint(1, 28))
    except ValueError:
        read_date_obj = datetime(year_ad, month, 28)

    print_date_obj = read_date_obj + timedelta(hours=random.randint(2, 20))
    read_date_str = format_thai_date_short(read_date_obj)
    print_date_str = f"{format_thai_date_short(print_date_obj)} {print_date_obj.strftime('%H:%M:%S')}"

    due_date_obj = read_date_obj + timedelta(days=10)
    due_date_code = f"{(due_date_obj.year + 543) % 100:02d}{due_date_obj.month:02d}{due_date_obj.day:02d}"

    user_type_code = random.choice(["1115", "1125"])
    service_fee = 38.22 if user_type_code == "1115" else 312.24

    prev_read = random.randint(10000, 45000)
    usage = random.randint(150, 800)
    curr_read = prev_read + usage

    base_price = usage * 3.78
    ft_rate = 0.3972
    ft_total = usage * ft_rate

    sub_total = base_price + ft_total + service_fee
    vat = sub_total * 0.07
    grand_total = sub_total + vat

    ca_ref = f"0200{random.randint(10000000, 99999999)}"
    tax_id = "099400016550100"
    pea_code_display = f"{random.randint(100000, 999999)}"

    return {
        "period": bill_period,
        "read_date_obj": read_date_obj,
        "read_date": read_date_str,
        "print_date": print_date_str,
        "prev": prev_read,
        "curr": curr_read,
        "usage": usage,
        "base_price": base_price,
        "ft_rate": ft_rate,
        "ft_total": ft_total,
        "service": service_fee,
        "vat": vat,
        "total": grand_total,
        "ca_ref": ca_ref,
        "pea_code": pea_code_display,
        "tax_id": tax_id,
        "due_date_code": due_date_code,
        "name": customer_name,
        "address": address_line,
        "pea_branch": pea_branch_name,
        "user_type": user_type_code
    }

def generate_barcode(code_data, width, height):
    writer = ImageWriter()
    ean = Code128(code_data, writer=writer)
    barcode_img = ean.render(writer_options={
        'module_height': 5.0,
        'module_width': 0.25,
        'write_text': False,
        'quiet_zone': 1.0,
    })
    barcode_img = barcode_img.resize((width, height))
    return make_transparent(barcode_img)

def generate_qr(code_data, size):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(code_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    img = img.resize((size, size))
    return make_transparent(img)

def draw_rotated_text(target_img, text, pos, font, angle, fill=(30, 30, 30)):
    bbox = font.getbbox(str(text))
    width, height = bbox[2], bbox[3] + 15
    txt_layer = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    d = ImageDraw.Draw(txt_layer)
    d.text((0, 0), str(text), font=font, fill=fill)
    rotated = txt_layer.rotate(angle, expand=1, resample=Image.BICUBIC)
    target_img.paste(rotated, pos, rotated)

# ==========================================
# 4. ฟังก์ชันสร้างบิลหลัก
# ==========================================
def create_bill(index):
    if not os.path.exists(TEMPLATE_FILE):
        print(f"❌ ไม่พบไฟล์ {TEMPLATE_FILE}")
        return
        
    base_img = Image.open(TEMPLATE_FILE).convert("RGBA")
    ink_layer = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(ink_layer)

    # โหลดฟอนต์
    try:
        font_path_bold = os.path.join(FONT_DIR, "Sarabun-Bold.ttf")
        font_path_reg = os.path.join(FONT_DIR, "Sarabun-Regular.ttf")
        
        font_main = ImageFont.truetype(font_path_bold, 23)
        font_header = ImageFont.truetype(font_path_bold, 26)
        font_nums = ImageFont.truetype(font_path_bold, 21)
        font_small = ImageFont.truetype(font_path_reg, 24)
        font_static = ImageFont.truetype(font_path_reg, 22)
    except Exception as e:
        print(f"⚠️ โหลดฟอนต์ไม่สำเร็จ: {e}")
        font_default = ImageFont.load_default()
        font_main = font_header = font_nums = font_small = font_static = font_default

    data = generate_bill_data()
    ink_color = (25, 25, 25)
    
    data_map = [
        (data["pea_branch"], (175, 165), font_main, 0),
        (data["name"], (175, 210), font_main, 0),
        (data["address"], (175, 250), font_main, 0),
        (data["pea_code"], (60, 330), font_nums, 0),
        (f"INC{random.randint(1000,9999)}", (175, 330), font_nums, 0),
        (data["ca_ref"], (330, 320), font_nums, 5),
        (f"{random.randint(20000000,99999999)}", (515, 320), font_nums, -5),
        (f"{random.randint(100000000000,999999999999)}", (670, 330), font_nums, 0),
        (data["period"], (850, 330), font_nums, 0),
        ("176580", (60, 405), font_nums, 0),
        (data["user_type"], (240, 410), font_nums, 0),
        ("1.0000", (370, 410), font_nums, 0),
        (f"{data['read_date']} 09:30", (480, 400), font_small, 0),
        (data['print_date'], (720, 400), font_small, 0),
        ("A Version 5.91.046 /1", (480, 450), font_static, 0),
        (f"{data['curr']}.000", (60, 530), font_nums, 0),
        (f"{data['prev']}.000", (220, 530), font_nums, 0),
        (f"{data['usage']}.00", (375, 530), font_nums, 0),
        (f"{data['base_price']:,.2f}", (800, 490), font_nums, 0),
        (f"{data['ft_rate']}", (550, 575), font_nums, 0),
        (f"{data['service']}", (818, 530), font_nums, 0),
        (f"{data['ft_total']:,.2f}", (828, 570), font_nums, 0),
        ("7", (630, 750), font_nums, 0),
        (f"{data['vat']:,.2f}", (850, 690), font_nums, 0),
        (f"{data['total']:,.2f}", (850, 730), font_nums, 0),
        (f"*** {data['total']:,.2f}", (850, 840), font_nums, 0),
        (f"*** {data['total']:,.2f}", (850, 1055), font_nums, 0),
    ]

    for item in data_map:
        text, pos, font, angle = item
        if angle == 0:
            draw.text(pos, str(text), fill=ink_color, font=font)
        else:
            draw_rotated_text(ink_layer, text, pos, font, angle, fill=ink_color)

    # --- History Logs ---
    current_date = data['read_date_obj']
    history_date_y = 1270
    history_unit_y = 1320
    column_x_coords = [160, 300, 445, 580, 728, 870]

    for i, x_pos in enumerate(column_x_coords):
        prev_month_date = current_date - timedelta(days=30 * (i+1))
        hist_date_str = format_thai_date_short(prev_month_date)
        hist_usage = str(random.randint(200, 500))
        draw.text((x_pos, history_date_y), hist_date_str, fill=(20, 20, 20), font=font_small)
        draw.text((x_pos + 15, history_unit_y), hist_usage, fill=(20, 20, 20), font=font_small)

    try:
        total_satang = int(round(data['total'] * 100))
        barcode_raw_data = f"{data['tax_id']}{data['ca_ref']}{data['due_date_code']}{total_satang}"
        
        barcode_img = generate_barcode(barcode_raw_data, 420, 70)
        ink_layer.paste(barcode_img, (40, 1400), barcode_img)
        
        barcode_human_text = f"|{data['tax_id']} {data['ca_ref']} {data['due_date_code']} {total_satang}"
        draw.text((50, 1455), barcode_human_text, fill=(0, 0, 0), font=font_small)
        
        qr_img = generate_qr(barcode_raw_data, 110)
        ink_layer.paste(qr_img, (750, 1400), qr_img)

    except Exception as e:
        print(f"Barcode/QR Error: {e}")

    # ทำ Effect กระดาษ
    ink_layer = ink_layer.filter(ImageFilter.GaussianBlur(radius=0.5))
    white_bg_for_ink = Image.new("RGB", base_img.size, (255, 255, 255))
    white_bg_for_ink.paste(ink_layer, (0, 0), ink_layer)
    
    final_img = ImageChops.multiply(base_img.convert("RGB"), white_bg_for_ink)
    noise = Image.effect_noise(final_img.size, 10).convert("RGB")
    final_img = Image.blend(final_img, noise, alpha=0.03)

    filename = f"ใบเสร็จการไฟฟ้า_{index:03d}.jpg"
    save_path = f"{OUTPUT_DIR}/images/{filename}"
    final_img.save(save_path, quality=95)
    print(f"✅ สำเร็จ: {save_path}")

# ==========================================
# 5. สั่งรันลูป
# ==========================================
if __name__ == "__main__":
    print("กำลังสร้างใบแจ้งหนี้ (Realism Effect & Custom Names applied)...")
    for i in range(1, 501): 
        create_bill(i)