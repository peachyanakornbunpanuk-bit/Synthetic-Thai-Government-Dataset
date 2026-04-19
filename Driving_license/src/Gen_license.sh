#!/bin/bash
#SBATCH -p gpu              # ใช้ partition เดิม (หรือถ้ามี partition 'compute' ก็เปลี่ยนได้ครับ)
#SBATCH -N 1                # ใช้ 1 เครื่อง
#SBATCH --gpus-per-node=1   # จอง 1 GPU (จริงๆ ไม่ได้ใช้ แต่ใส่ไว้เพื่อให้ Slurm ยอมรันในคิว GPU)
#SBATCH --ntasks-per-node=1
#SBATCH -t 02:00:00         # เวลา 2 ชั่วโมง (เหลือเฟือสำหรับการสร้างภาพ)
#SBATCH -A lt200395         # Project ID เดิมของคุณ
#SBATCH -J Gen_License      # เปลี่ยนชื่อ Job
#SBATCH -o ../logs/gen_%j.out # เปลี่ยนชื่อไฟล์ Log

# 1. แสดงเวลาเริ่ม
current_date_time="`date "+%Y-%m-%d %H:%M:%S"`";
echo "Job started at: $current_date_time"

######################
### Load Module ###
######################
# โหลด Module พื้นฐานที่จำเป็นสำหรับ Python environment
module restore
module load Mamba
module load PrgEnv-gnu
module load gcc

######################
### Set Environment ###
######################
# ใช้ Environment เดิมของคุณ (เพราะน่าจะมี Python อยู่แล้ว)
conda deactivate
conda activate /project/lt200393-foullm/train/unslot/env

# เช็ค path python เพื่อความชัวร์
which python

######################
### Install Libs ###
######################
# ติดตั้ง Pillow เผื่อว่าใน Env ยังไม่มี (ถ้ามีแล้วมันจะข้ามไปเอง เร็วมาก)
pip install pillow

######################
### Run Script ###
######################
echo "🚀 Running Generator Script..."

# สั่งรันไฟล์ Python
# (ตรวจสอบว่าไฟล์ generate_license.py อยู่โฟลเดอร์เดียวกับ .sh นี้ หรือใส่ path เต็ม)
python generate_license_alltype.py

echo "✅ Job Finished!"