#!/bin/bash
#SBATCH -p gpu
#SBATCH -N 1
#SBATCH --gpus-per-node=1
#SBATCH --ntasks-per-node=1
#SBATCH -t 02:00:00
#SBATCH -A lt200395
#SBATCH -J Gen_Passport
#SBATCH -o ../logs/pass_%j.out

# 1. แสดงเวลาเริ่ม
current_date_time="`date "+%Y-%m-%d %H:%M:%S"`";
echo "Job started at: $current_date_time"

######################
### Load Module ###
######################
module restore
module load Mamba
module load PrgEnv-gnu
module load gcc

######################
### Set Environment ###
######################
conda deactivate
conda activate /project/lt200393-foullm/train/unslot/env

which python

######################
### Run Script ###
######################
echo "🚀 Running Passport Generator Script..."

# สั่งรันไฟล์ Python (ไม่ต้อง pip install อะไรแล้ว)
python generate_passport.py

echo "✅ Job Finished!"