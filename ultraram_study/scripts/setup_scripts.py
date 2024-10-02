import os
import copy
import argparse
import yaml

from config import *

argparser = argparse.ArgumentParser(
  description='Setup ULTRARAM run generation scripts for SLURM.'
)

argparser.add_argument("-wd", "--working_directory")
argparser.add_argument("-bc", "--base_config")
argparser.add_argument("-tc", "--trace_combination")
argparser.add_argument("-td", "--trace_directory")
argparser.add_argument("-rd", "--result_directory")
argparser.add_argument("-pn", "--partition_name")
argparser.add_argument('-of', '--output_file')

args = argparser.parse_args()

WORK_DIR         = args.working_directory
BASE_CONFIG_FILE = args.base_config
TRACE_COMB_FILE  = args.trace_combination
TRACE_DIR        = args.trace_directory
RESULT_DIR       = args.result_directory
PARTITION_NAME   = args.partition_name
OUTPUT_FILE      = args.output_file

SBATCH_CMD = 'sbatch --cpus-per-task=1 --nodes=1 --ntasks=1'
CMD_HEADER = '#!/bin/bash'
CMD        = f'{WORK_DIR}/ramulator2'

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def get_config():
  base_config = None
  with open(BASE_CONFIG_FILE, 'r') as f:
    try:
      base_config = yaml.safe_load(f)
    except yaml.YAMLError as exc:
      print(exc)
  return base_config

def get_traces():
  trace_list = []
  with open(TRACE_COMB_FILE, "r") as f:
    for line in f:
      trace_list.append(line.strip().split(','))
  return trace_list

def get_run_commands(base_config, trace_list):
  run_commands = []

  for trace_group in trace_list:
    for device in device_list:
      for org in org_list[device]:
        for timing in timing_list[device]:
            for row_policy in row_policy_list[device]:
              for refresh_manager in refresh_manager_list[device]:
                sbatch_filename    = f'{WORK_DIR}/run_scripts/{device}_{org}_{timing}_{row_policy}_{trace_group[0]}.sh'
                config_filename    = f'{RESULT_DIR}/configs/{device}_{org}_{timing}_{row_policy}_{trace_group[0]}.yaml'
                result_filename    = f'{RESULT_DIR}/stats/{device}_{org}_{timing}_{row_policy}_{trace_group[0]}.yaml'
                error_filename     = f'{RESULT_DIR}/errors/{device}_{org}_{timing}_{row_policy}_{trace_group[0]}.txt'
                cmd_count_filename = f'{RESULT_DIR}/cmd_counts/{device}_{org}_{timing}_{row_policy}_{trace_group[0]}.txt'
                wr_count_filename  = f'{RESULT_DIR}/wr_counts/{device}_{org}_{timing}_{row_policy}_{trace_group[0]}.txt'

                config = copy.deepcopy(base_config)
                config["Frontend"]["traces"] = [f'{TRACE_DIR}/{trace}' for trace in trace_group[1:]]
                config['MemorySystem']['DRAM']['impl'] = device
                config['MemorySystem']['DRAM']['org']['preset'] = f'{device}_{org}'
                config['MemorySystem']['DRAM']['timing']['preset'] = f'{device}_{timing}'
                config['MemorySystem']['Controller']['RefreshManager']['impl'] = refresh_manager
                config['MemorySystem']['Controller']['RowPolicy']['impl'] = row_policy
                config['MemorySystem']['Controller']['plugins'][0]['ControllerPlugin']['path'] = cmd_count_filename
                config['MemorySystem']['Controller']['plugins'].append({
                  'ControllerPlugin' : {
                    'impl': 'WriteCounter',
                    'path': wr_count_filename
                    }
                })

              with open(config_filename, 'w') as f:
                yaml.dump(config, f)

              with open(sbatch_filename, 'w') as f:
                f.write(CMD_HEADER + '\n')
                f.write(f'{CMD} -f {config_filename}' + '\n')

              sbatch_cmd = f'{SBATCH_CMD} --exclude={SLURM_EXCLUDE_NODES} --chdir={WORK_DIR} --output={result_filename}'
              sbatch_cmd += f' --error={error_filename} --partition={PARTITION_NAME} --job-name="ramulator2" {sbatch_filename}'

              run_commands.append(sbatch_cmd)
  return run_commands
              
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
              
for path in [
        f'{RESULT_DIR}/stats',
        f'{RESULT_DIR}/errors',
        f'{RESULT_DIR}/configs',
        f'{RESULT_DIR}/cmd_counts',
        f'{RESULT_DIR}/wr_counts'
    ]:
    if not os.path.exists(path):
        os.makedirs(path)

if(os.path.exists(f'{WORK_DIR}/run_scripts')):
  os.system(f'rm -r {WORK_DIR}/run_scripts')
os.system(f'mkdir -p {WORK_DIR}/run_scripts')

base_config  = get_config()
trace_list   = get_traces()
command_list = get_run_commands(base_config, trace_list)

with open(OUTPUT_FILE, 'w') as f:
  for cmd in command_list:
    f.write(cmd + '\n')

os.system(f'chmod +x {OUTPUT_FILE}')
