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
argparser.add_argument("-tm", "--trace_mpki")
argparser.add_argument("-td", "--trace_directory")
argparser.add_argument("-rd", "--result_directory")
argparser.add_argument("-pn", "--partition_name")

args = argparser.parse_args()

WORK_DIR         = args.working_directory
BASE_CONFIG_FILE = args.base_config
TRACE_COMB_FILE  = args.trace_combination
TRACE_MPKI_FILE  = args.trace_mpki
TRACE_DIR        = args.trace_directory
RESULT_DIR       = args.result_directory
PARTITION_NAME   = args.partition_name

SBATCH_CMD = 'sbatch --cpus-per-task=1 --nodes=1 --ntasks=1'
CMD_HEADER = '#!/bin/bash'
CMD        = f'{WORK_DIR}/ramulator2'

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

base_config = None
trace_combs = {}
trace_types = {}

with open(BASE_CONFIG_FILE, 'r') as f:
  try:
    base_config = yaml.safe_load(f)
  except yaml.YAMLError as exc:
    print(exc)

with open(TRACE_COMB_FILE, 'r') as f:
  for line in f:
    line       = line.strip()
    tokens     = line.split(',')
    trace_name = tokens[0]
    trace_type = tokens[1]
    traces     = tokens[2:]

    trace_combs[trace_name] = traces
    trace_types[trace_name] = trace_type

def get_multicore_traces(trace_comb_file):
  multicore_trace_list = set()
  with open(trace_comb_file, "r") as f:
      for line in f:
          line = line.strip()
          tokens = line.split(',')
          trace_name = tokens[0]
          multicore_trace_list.add(trace_name)
  return multicore_trace_list

def get_singlecore_traces(trace_mpki_file):
  singlecore_trace_list = []
  with open(trace_mpki_file, 'r') as f:
    for line in f:
      line = line.strip()
      trace, mpki = line.split(',')
      singlecore_trace_list.append(trace)

  return singlecore_trace_list

def get_singlecore_run_commands():
  run_commands = []
  singlecore_traces = get_singlecore_traces(TRACE_MPKI_FILE)

  for device in device_list:
    for org in org_list:
      for row_policy in row_policy_list:
        for timing in timing_list[device]:
          for scale_idx in range(scale_list['area_scaling_factor'].size):
            for trace in singlecore_traces:
              sbatch_filename    = f'{WORK_DIR}/run_scripts/{device}_{org}_{timing}_{row_policy}_{scale_list['area_scaling_factor'][scale_idx]}_{trace}.sh'
              config_filename    = f'{RESULT_DIR}/configs/{device}_{org}_{timing}_{row_policy}_{scale_list['area_scaling_factor'][scale_idx]}_{trace}.yaml'
              result_filename    = f'{RESULT_DIR}/stats/{device}_{org}_{timing}_{row_policy}_{scale_list['area_scaling_factor'][scale_idx]}_{trace}.yaml'
              error_filename     = f'{RESULT_DIR}/errors/{device}_{org}_{timing}_{row_policy}_{scale_list['area_scaling_factor'][scale_idx]}_{trace}.txt'
              cmd_count_filename = f'{RESULT_DIR}/cmd_counts/{device}_{org}_{timing}_{row_policy}_{scale_list['area_scaling_factor'][scale_idx]}_{trace}.txt'
              wr_count_filename  = f'{RESULT_DIR}/wr_counts/{device}_{org}_{timing}_{row_policy}_{scale_list['area_scaling_factor'][scale_idx]}_{trace}.txt'

              config = copy.deepcopy(base_config)
              config['Frontend']['traces'] = [f'{TRACE_DIR}/{trace}']
              config['MemorySystem']['DRAM']['impl'] = device
              config['MemorySystem']['DRAM']['org']['preset'] = f'{device}_{org}'
              config['MemorySystem']['DRAM']['timing']['preset'] = f'{device}_{timing}'
              config['MemorySystem']['Controller']['RefreshManager']['impl'] = refresh_manager[device]
              config['MemorySystem']['Controller']['RowPolicy']['impl'] = row_policy
              config['MemorySystem']['Controller']['plugins'][0]['ControllerPlugin']['path'] = cmd_count_filename
              config['MemorySystem']['Controller']['plugins'].append({
                'ControllerPlugin' : {
                  'impl': 'WriteCounter',
                  'path': wr_count_filename
                  }
                })

              for scales in scale_list.columns[1:]:
                config['MemorySystem']['DRAM']['scales'][scales] = float(scale_list.loc[scale_idx, scales])
              
              #TODO: need to find a better way for below lines, it looks terrible
              if device == 'DDR5':
                config['MemorySystem']['Controller']['plugins'].append({'ControllerPlugin' : {'impl': 'RFMManager'}})

              with open(config_filename, 'w') as f:
                yaml.dump(config, f)
              
              with open(sbatch_filename, 'w') as f:
                f.write(CMD_HEADER + '\n')
                f.write(f'{CMD} -f {config_filename}' + '\n')

              sbatch_cmd = f'{SBATCH_CMD} --chdir={WORK_DIR} --output={result_filename}'
              sbatch_cmd += f' --error={error_filename} --partition={PARTITION_NAME} --job-name="ramulator2" {sbatch_filename}'

              run_commands.append(sbatch_cmd)
  
  return run_commands

def get_multicore_run_commands():
  run_commands = []
  multicore_traces = get_multicore_traces(TRACE_COMB_FILE)

  for device in device_list:
    for org in org_list:
      for row_policy in row_policy_list:
        for timing in timing_list[device]:
          for scale_idx in range(scale_list['area_scaling_factor'].size):
            for trace in multicore_traces:
              sbatch_filename    = f'{WORK_DIR}/run_scripts/{device}_{org}_{timing}_{row_policy}_{scale_list['area_scaling_factor'][scale_idx]}_{trace}.sh'
              config_filename    = f'{RESULT_DIR}/configs/{device}_{org}_{timing}_{row_policy}_{scale_list['area_scaling_factor'][scale_idx]}_{trace}.yaml'
              result_filename    = f'{RESULT_DIR}/stats/{device}_{org}_{timing}_{row_policy}_{scale_list['area_scaling_factor'][scale_idx]}_{trace}.yaml'
              error_filename     = f'{RESULT_DIR}/errors/{device}_{org}_{timing}_{row_policy}_{scale_list['area_scaling_factor'][scale_idx]}_{trace}.txt'
              cmd_count_filename = f'{RESULT_DIR}/cmd_counts/{device}_{org}_{timing}_{row_policy}_{scale_list['area_scaling_factor'][scale_idx]}_{trace}.txt'
              wr_count_filename  = f'{RESULT_DIR}/wr_counts/{device}_{org}_{timing}_{row_policy}_{scale_list['area_scaling_factor'][scale_idx]}_{trace}.txt'

              config = copy.deepcopy(base_config)
              config["Frontend"]["traces"] = [f'{TRACE_DIR}/{trace_group}' for trace_group in trace_combs[trace]]
              config['MemorySystem']['DRAM']['impl'] = device
              config['MemorySystem']['DRAM']['org']['preset'] = f'{device}_{org}'
              config['MemorySystem']['DRAM']['timing']['preset'] = f'{device}_{timing}'
              config['MemorySystem']['Controller']['RefreshManager']['impl'] = refresh_manager[device]
              config['MemorySystem']['Controller']['RowPolicy']['impl'] = row_policy
              config['MemorySystem']['Controller']['plugins'][0]['ControllerPlugin']['path'] = cmd_count_filename
              config['MemorySystem']['Controller']['plugins'].append({
                'ControllerPlugin' : {
                  'impl': 'WriteCounter',
                  'path': wr_count_filename
                  }
                })
              
              #TODO: need to find a better way for below lines, it looks terrible
              if device == 'DDR5':
                config['MemorySystem']['Controller']['plugins'].append({'ControllerPlugin' : {'impl': 'RFMManager'}})

              for scales in scale_list.columns[1:]:
                config['MemorySystem']['DRAM']['scales'][scales] = float(scale_list.loc[scale_idx, scales])

              with open(config_filename, 'w') as f:
                yaml.dump(config, f)
              
              with open(sbatch_filename, 'w') as f:
                f.write(CMD_HEADER + '\n')
                f.write(f'{CMD} -f {config_filename}' + '\n')

              sbatch_cmd = f'{SBATCH_CMD} --chdir={WORK_DIR} --output={result_filename}'
              sbatch_cmd += f' --error={error_filename} --partition={PARTITION_NAME} --job-name="ramulator2" {sbatch_filename}'

              run_commands.append(sbatch_cmd)
  return run_commands

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

singlecore_commands = get_singlecore_run_commands()
multicore_commands  = get_multicore_run_commands()
with open('run.sh', 'w') as f:
  for cmd in singlecore_commands + multicore_commands:
    f.write(cmd + '\n')

os.system('chmod +x run.sh')
