import os
import subprocess
import time
import argparse

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

def run_personal(commands):
  from concurrent.futures import ThreadPoolExecutor, as_completed
  import tqdm
  def run_command(command):
    try:
      result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
      return result.stdout
    except subprocess.CalledProcessError as e:
      print(f"[ERROR] executing command '{command}': {e}")
      print(f"[ERROR] stderr: {e.stderr}")
      return e.stderr

  with ThreadPoolExecutor(max_workers=PERS_NUM_THREADS) as executor:
    futures = [executor.submit(run_command, cmd) for cmd in commands]

    for _ in tqdm.tqdm(as_completed(futures), total=len(futures), desc="Running benchmarks"):
      pass
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

argparser = argparse.ArgumentParser(
  description='Execute generated scripts from setup_scripts.py'
)

argparser.add_argument("-rs", "--run_slurm", action=argparse.BooleanOptionalAction)
args = argparser.parse_args()

RUN_SLURM = args.run_slurm

if RUN_SLURM:
  commands = []
  with open('run_slurm.sh', 'r') as f:
    commands = [l.strip() for l in f.readlines()]

  run_slurm(commands)
else:
  commands = []
  with open('run_personal.sh', 'r') as f:
    commands = [l.strip() for l in f.readlines()]

  run_personal(commands)