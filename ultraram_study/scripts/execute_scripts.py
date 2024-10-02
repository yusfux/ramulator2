from concurrent.futures import ThreadPoolExecutor
import os
import time

from config import *

def check_running_jobs():
  return int(os.popen(f'squeue -u {SLURM_USER} -h | wc -l').read())

def run_slurm(commands):
  for cmd in commands:
    while check_running_jobs() >= SLURM_MAX_JOBS:
      print(f"[INFO] Maximum Slurm Job limit ({SLURM_MAX_JOBS}) reached. Retrying in {SLURM_RETRY_DELAY} seconds")
      time.sleep(SLURM_RETRY_DELAY)
    
    os.system(cmd)
    time.sleep(SLURM_SUBMIT_DELAY)

commands = []
with open('sbatch_runs.sh', 'r') as f:
  commands = [l.strip() for l in f.readlines()]

run_slurm(commands)