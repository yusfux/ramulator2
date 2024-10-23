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
              for area_scale in area_scaling_list[device]:
                for voltage_scale in voltage_scaling_list[device]:
                  sbatch_filename = f'{WORK_DIR}/run_scripts/{device}_{org}_{timing}_{row_policy}_{refresh_manager}_{area_scale}_{voltage_scale}_{trace_group[0]}.sh'
                  config_filename = f'{RESULT_DIR}/configs/{device}_{org}_{timing}_{row_policy}_{refresh_manager}_{area_scale}_{voltage_scale}_{trace_group[0]}.yaml'
                  result_filename = f'{RESULT_DIR}/stats/{device}_{org}_{timing}_{row_policy}_{refresh_manager}_{area_scale}_{voltage_scale}_{trace_group[0]}.yaml'
                  error_filename  = f'{RESULT_DIR}/errors/{device}_{org}_{timing}_{row_policy}_{refresh_manager}_{area_scale}_{voltage_scale}_{trace_group[0]}.txt'
                  plugin_filename = f'{RESULT_DIR}/plugins/PLUGIN_NAME/{device}_{org}_{timing}_{row_policy}_{refresh_manager}_{area_scale}_{voltage_scale}_{trace_group[0]}.txt'

                  config = copy.deepcopy(base_config)
                  config["Frontend"]["traces"] = [f'{TRACE_DIR}/{trace}' for trace in trace_group[1:]]
                  config['MemorySystem']['DRAM']['impl'] = device
                  config['MemorySystem']['DRAM']['org']['preset'] = f'{device}_{org}'
                  config['MemorySystem']['DRAM']['timing']['preset'] = f'{device}_{timing}'
                  config['MemorySystem']['Controller']['RefreshManager']['impl'] = refresh_manager
                  config['MemorySystem']['Controller']['RowPolicy']['impl'] = row_policy

                  config['MemorySystem']['Controller']['plugins'] = []
                  for plugin in plugin_list[device]:
                    config['MemorySystem']['Controller']['plugins'].append({
                      'ControllerPlugin' : {
                        'impl': plugin[0],
                        'path': plugin_filename.replace('PLUGIN_NAME', plugin[1])
                        }
                    })

                  # ------ additional configurations for URAM5 ------
                  if device == 'URAM5':
                    add_uram_scales(config, area_scale, voltage_scale)
                  # ------ additional configurations for URAM5 ------

                  # ------ additional configurations for DDR5 ------
                  if device == 'DDR5':
                    pass
                  # ------ additional configurations for DDR5 ------

                  with open(config_filename, 'w') as f:
                    yaml.dump(config, f)

                  with open(sbatch_filename, 'w') as f:
                    f.write(CMD_HEADER + '\n')
                    f.write(f'{CMD} -f {config_filename}' + '\n')

                  sbatch_cmd = f'{SBATCH_CMD} --exclude={SLURM_EXCLUDE_NODES} --chdir={WORK_DIR} --output={result_filename}'
                  sbatch_cmd += f' --error={error_filename} --partition={PARTITION_NAME} --job-name="ramulator2" {sbatch_filename}'

                  pers_cmd = f'bash {sbatch_filename}'
                  pers_cmd += f' > {result_filename} 2> {error_filename}'

                  run_commands.append((sbatch_cmd, pers_cmd))
  return run_commands
              
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
              
for path in [
        f'{RESULT_DIR}/configs',
        f'{RESULT_DIR}/stats',
        f'{RESULT_DIR}/errors'
    ]:
    if not os.path.exists(path):
        os.makedirs(path)

for device in device_list:
  for plugin in plugin_list[device]:
    if not os.path.exists(f'{RESULT_DIR}/plugins/{plugin[1]}'):
      os.makedirs(f'{RESULT_DIR}/plugins/{plugin[1]}')

if(os.path.exists(f'{WORK_DIR}/run_scripts')):
  os.system(f'rm -r {WORK_DIR}/run_scripts')
os.system(f'mkdir -p {WORK_DIR}/run_scripts')

base_config  = get_config()
trace_list   = get_traces()
slurm_commands, pers_commands = zip(*get_run_commands(base_config, trace_list))

with open('run_slurm.sh', 'w') as f:
  for cmd in slurm_commands:
    f.write(cmd + '\n')

with open('run_personal.sh', 'w') as f:
  for cmd in pers_commands:
    f.write(cmd + '\n')

os.system(f'chmod +x run_slurm.sh')
os.system(f'chmod +x run_personal.sh')
