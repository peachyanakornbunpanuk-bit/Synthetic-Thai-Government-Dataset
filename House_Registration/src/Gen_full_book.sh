#!/bin/bash
#SBATCH -p gpu
#SBATCH -N 1
#SBATCH --gpus-per-node=1
#SBATCH --ntasks-per-node=1
#SBATCH -t 01:00:00
#SBATCH -A lt200395
#SBATCH -J Gen_HouseFull
#SBATCH -o ../logs/house_full_%j.out

echo "Starting Full House Registration Job..."
module restore
module load Mamba
module load PrgEnv-gnu
module load gcc

# ใช้ Environment เดิมที่มี Pillow
conda deactivate
conda activate /project/lt200393-foullm/train/unslot/env

# รันโค้ด Python
python generate_full_book.py

echo "✅ Job Finished!"