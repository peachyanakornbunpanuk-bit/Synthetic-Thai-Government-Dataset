#!/bin/bash
#SBATCH -p gpu
#SBATCH -N 1
#SBATCH -c 4
#SBATCH --gpus-per-node=1
#SBATCH --ntasks-per-node=1
#SBATCH -t 02:00:00
#SBATCH -A lt200258
#SBATCH -J bill_autolabel
#SBATCH -o slurm_logs/bill_label_%j.out
#SBATCH -e slurm_logs/bill_label_%j.err

# 1. Load Module
module purge
module load Mamba
module load cuda/12.6
module load gcc/12.2.0

# 2. Activate Environment
conda deactivate
conda activate /project/lt200393-foullm/train/unslot/env

# 3. Run Script
# (อย่าลืมเปลี่ยนชื่อไฟล์ python ให้ตรงกับที่คุณเซฟ)
python auto_label_bills.py