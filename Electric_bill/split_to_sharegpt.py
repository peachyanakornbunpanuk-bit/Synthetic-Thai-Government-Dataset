import json
import os
import glob
import random
import shutil

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
BASE_DIR = "Mea_Pea"  # โฟลเดอร์หลัก
IMAGE_DIR = os.path.join(BASE_DIR, "image")
LABEL_DIR = os.path.join(BASE_DIR, "labels")

# จำนวนที่ต้องการแบ่ง
TARGET_TEST_SIZE = 200
# Train จะเป็นส่วนที่เหลือ (ประมาณ 800)

SYSTEM_PROMPT = "<image>\nช่วยอ่านรายละเอียดและสรุปข้อมูลสำคัญในบิลค่าไฟฉบับนี้"

# 🔥 KEY MAPPING: แปลงชื่อภาษาอังกฤษใน JSON เป็นภาษาไทยที่อ่านง่าย
# รวมของทั้ง MEA และ PEA ไว้ด้วยกัน
KEY_MAPPING = {
    # --- ข้อมูลทั่วไป ---
    "district_name": "เขต/อำเภอ",
    "branch_name": "สาขา",
    "customer_name": "ชื่อผู้ใช้ไฟฟ้า",
    "customer_address": "สถานที่ใช้ไฟฟ้า",
    
    # --- รหัสต่างๆ ---
    "ca_ref": "บัญชีแสดงสัญญา (CA/Ref)",
    "pea_code": "รหัสการไฟฟ้า",
    "install": "รหัสเครื่องวัด (Installation)", # MEA
    "meter_id": "รหัสเครื่องวัด",            # PEA
    "mru": "MRU",
    "invoice": "เลขที่ใบแจ้งหนี้",
    "invoice_no": "เลขที่ใบแจ้งหนี้",
    "inc_code": "INC Code",
    
    # --- การอ่านมิเตอร์ ---
    "user_type": "ประเภทผู้ใช้",
    "read_date": "วันจดเลขอ่าน",
    "read_datetime": "วันเวลาจดเลข",
    "curr_read": "เลขอ่านครั้งหลัง",
    "current_unit": "เลขอ่านครั้งหลัง",
    "prev_read": "เลขอ่านครั้งก่อน",
    "prev_unit": "เลขอ่านครั้งก่อน",
    "usage_unit": "จำนวนหน่วยที่ใช้",
    "multiplier": "ตัวคูณ",
    
    # --- ยอดเงิน ---
    "base_amount": "ค่าพลังงานไฟฟ้า",
    "service_fee": "ค่าบริการ",
    "ft_amount": "ค่า Ft",
    "ft_rate": "อัตรา Ft",
    "pre_vat_amount": "รวมเงินก่อนภาษี",
    "vat_percent": "อัตราภาษี",
    "vat_amount": "ภาษีมูลค่าเพิ่ม (VAT)",
    
    # --- ยอดรวม ---
    "total_amount": "ยอดเงินรวมที่ต้องชำระ",
    "total_amount_main": "ยอดเงินรวมที่ต้องชำระ",
    "total_amount_highlight": "ยอดเงินรวม (เน้น)",
    
    # --- วันที่ ---
    "due_date_range": "กำหนดชำระ",
    "period": "ประจำเดือน",
    "print_datetime": "วันเวลาที่พิมพ์",
    
    # --- บาร์โค้ด ---
    "barcode_text": "รหัสบาร์โค้ด",
    "barcode_vertical": "รหัสบาร์โค้ด (แนวตั้ง)",
    "barcode_bottom": "รหัสบาร์โค้ด (ล่าง)",
    "barcode": "รหัสบาร์โค้ด"
}

def create_sharegpt_dataset():
    # 1. ค้นหาไฟล์ JSON ทั้งหมด
    json_pattern = os.path.join(LABEL_DIR, "*.json")
    json_files = glob.glob(json_pattern)
    
    print(f"📂 พบไฟล์ Labels ทั้งหมด: {len(json_files)} ไฟล์")
    
    if len(json_files) == 0:
        print("❌ ไม่พบไฟล์ JSON กรุณาตรวจสอบว่าโฟลเดอร์ Mea_Pea/labels มีไฟล์อยู่จริง")
        return

    dataset = []
    
    # ใช้ Set เพื่อกันข้อมูลซ้ำ
    processed_ids = set()

    for json_path in json_files:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # ดึงชื่อไฟล์รูปจาก JSON
            img_filename = data.get('filename')
            
            # สร้าง ID ที่ไม่ซ้ำ (ใช้ชื่อไฟล์ JSON ตัดนามสกุลออก)
            file_id = os.path.splitext(os.path.basename(json_path))[0]
            
            if file_id in processed_ids:
                continue
            processed_ids.add(file_id)

            # --- ตรวจสอบไฟล์รูปภาพ ---
            # 1. ลองหาตามชื่อใน JSON เป๊ะๆ
            full_image_path = os.path.join(IMAGE_DIR, img_filename)
            
            # 2. ถ้าไม่เจอ ลองหาตามชื่อ ID (กรณีชื่อใน JSON ไม่ตรงกับไฟล์จริง)
            if not os.path.exists(full_image_path):
                # เช่น JSON ชื่อ image_123.json แต่ในไฟล์เขียน image_123.png
                possible_exts = ['.jpg', '.jpeg', '.png']
                found = False
                for ext in possible_exts:
                    temp_path = os.path.join(IMAGE_DIR, file_id + ext)
                    if os.path.exists(temp_path):
                        full_image_path = temp_path
                        found = True
                        break
                
                if not found:
                    # 3. กรณีชื่อภาษาไทย ลอง Encode/Decode หรือหาไฟล์ที่มีชื่อคล้ายกัน
                    # แต่วิธีที่ง่ายสุดคือ listdir แล้วเทียบชื่อ
                    all_images = os.listdir(IMAGE_DIR)
                    if img_filename in all_images:
                         full_image_path = os.path.join(IMAGE_DIR, img_filename)
                    else:
                        print(f"⚠️ ไม่พบรูปภาพสำหรับ: {json_path} (ข้าม)")
                        continue

            # --- สร้างคำตอบ GPT (Ground Truth) ---
            annotations = data.get('annotations', [])
            
            # เรียงลำดับจากบนลงล่าง (แกน Y)
            sorted_anns = sorted(annotations, key=lambda x: x['box'][1])
            
            text_lines = []
            for ann in sorted_anns:
                label = ann.get('label', 'text')
                text = ann.get('text', '')
                
                # ข้ามพวกประวัติการใช้ไฟย้อนหลัง (History) ถ้าไม่อยากให้รก
                if "hist" in label or "history" in label:
                    continue

                # แปลง Key เป็นไทย
                readable_label = KEY_MAPPING.get(label, label)
                
                text_lines.append(f"{readable_label}: {text}")
            
            gpt_response = "\n".join(text_lines)

            # --- จัดรูปแบบ ShareGPT ---
            entry = {
                "id": file_id,
                "image": full_image_path, 
                "conversations": [
                    {
                        "from": "human",
                        "value": SYSTEM_PROMPT
                    },
                    {
                        "from": "gpt",
                        "value": gpt_response
                    }
                ]
            }
            dataset.append(entry)

        except Exception as e:
            print(f"❌ Error processing {json_path}: {e}")

    # 2. สุ่มและแบ่งข้อมูล (Shuffle & Split)
    total_items = len(dataset)
    print(f"📊 ข้อมูลที่พร้อมใช้งาน: {total_items} รายการ")
    
    # Random Shuffle
    random.seed(42) # ล็อคผลการสุ่มให้เหมือนเดิมทุกครั้ง
    random.shuffle(dataset)

    # แบ่งตามจำนวนที่ขอ
    if total_items > TARGET_TEST_SIZE:
        test_set = dataset[:TARGET_TEST_SIZE]       # เอา 200 อันแรกเป็น Test
        train_set = dataset[TARGET_TEST_SIZE:]      # ที่เหลือเป็น Train
    else:
        print("⚠️ ข้อมูลมีน้อยกว่า Test Size ที่กำหนด -> แบ่ง 80/20 แทน")
        split_idx = int(total_items * 0.2)
        test_set = dataset[:split_idx]
        train_set = dataset[split_idx:]

    # 3. บันทึกไฟล์
    train_path = os.path.join(BASE_DIR, "train_dataset.json")
    with open(train_path, 'w', encoding='utf-8') as f:
        json.dump(train_set, f, ensure_ascii=False, indent=4)
        
    test_path = os.path.join(BASE_DIR, "test_dataset.json")
    with open(test_path, 'w', encoding='utf-8') as f:
        json.dump(test_set, f, ensure_ascii=False, indent=4)

    print("="*50)
    print(f"✅ สร้าง Dataset เสร็จสมบูรณ์!")
    print(f"📘 Train Set: {len(train_set)} รายการ")
    print(f"📙 Test Set : {len(test_set)} รายการ")
    print(f"💾 ไฟล์ถูกบันทึกไว้ในโฟลเดอร์: {BASE_DIR}")
    print("="*50)

if __name__ == "__main__":
    create_sharegpt_dataset()