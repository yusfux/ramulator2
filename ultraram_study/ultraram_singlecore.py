from concurrent.futures import ThreadPoolExecutor, as_completed
import copy
import subprocess
import argparse
import yaml
import shlex
import tqdm
import time

MAX_RUNS = 100
EXCLUDE_NODES = "kratos[10-20]"

device_list     = ['DDR4', 'DDR5', 'URAM4', 'URAM5']
org_list        = ['16Gb_x8']
timing_list     = {'DDR4': '3200AA', 'URAM4': '3200AA', 'DDR5': '3200AN', 'URAM5': '3200AN',}
row_policy_list = ['OpenRowPolicy']

refresh_manager = {'DDR4': 'AllBank', 'DDR5': 'AllBank', 'URAM4': 'NoRefresh', 'URAM5': 'NoRefresh',}
ultraram_trcd   = {'URAM4': '100', 'FURAM4': '10', 'URAM5': '100', 'FURAM5': '10'}

trace_list = ['500.perlbench', '502.gcc'      , '505.mcf'      , '507.cactuBSSN', '508.namd',
              '510.parest'   , '511.povray'   , '519.lbm'      , '520.omnetpp'  , '523.xalancbmk', 
              '525.x264'     , '526.blender'  , '531.deepsjeng', '538.imagick'  , '541.leela',
              '544.nab'      , '549.fotonik3d', '557.xz']

def main(base_config, trace_path, output_path, thread_count):
  tasks = get_config(base_config, trace_path, output_path)
  
  with ThreadPoolExecutor(thread_count) as executor:
    futures = [executor.submit(run_benchmark, config, out_file_name) for config, out_file_name in tasks]
    for _ in tqdm.tqdm(as_completed(futures), total=len(futures), desc="Running benchmarks"):
        pass

def get_run_count():
    try:
        runs = int(subprocess.getoutput(f"squeue -u yusufa -h -t running,pending -r | wc -l"))
        return runs
    except:
        return MAX_RUNS

def run_benchmark(config, out_file_name):
  while get_run_count() >= MAX_RUNS:
      print("Run count is " + str(get_run_count()) + ". Waiting...")
      time.sleep(30)

  cmd = 'srun --exclude=kratos10 --mem=6G .././ramulator2 -c "' + str(config) + '"'
  with open(f'{out_file_name}.yaml', 'w') as f:
    subprocess.run(shlex.split(cmd), stdout=f)

def get_config(base_config, trace_path, output_path):
  with open(base_config, 'r') as f:
    config_template = yaml.safe_load(f)

  tasks = []
  for device in device_list:
    for org in org_list:
      for row_policy in row_policy_list:
        for trace in trace_list:
          out_file_name = f'{output_path}/{device}_{org}_{timing_list[device]}_{row_policy}_{trace}'

          config = copy.deepcopy(config_template)
          config['Frontend']['traces'] = [f'{trace_path}/{trace}']
          config['MemorySystem']['DRAM']['impl'] = device
          config['MemorySystem']['DRAM']['org']['preset'] = f'{device}_{org}'
          config['MemorySystem']['DRAM']['timing']['preset'] = f'{device}_{timing_list[device]}'
          config['MemorySystem']['Controller']['RefreshManager']['impl'] = refresh_manager[device]
          config['MemorySystem']['Controller']['RowPolicy']['impl'] = row_policy

          if device == 'DDR5':
            config['MemorySystem']['Controller']['plugins'].append({'ControllerPlugin' : {'impl': 'RFMManager'}})

          if device.startswith('URAM'):
            config['MemorySystem']['DRAM']['timing']['tRCD'] = ultraram_trcd[device]

            fultraram_config = copy.deepcopy(config)
            fultraram_file_name = f'{output_path}/F{device}_{org}_{timing_list[device]}_{row_policy}_{trace}'
            fultraram_config['MemorySystem']['DRAM']['timing']['tRCD'] = ultraram_trcd[f'F{device}']
            tasks.append((fultraram_config, fultraram_file_name))

          tasks.append((config, out_file_name))

  return tasks


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Run ULTRARAM benchamrks in parallel with a specified number of threads.')

  parser.add_argument('--base_config', type=str, help='Path to the base config file', default='./ultraram_template.yaml')
  parser.add_argument('--trace_path', type=str, help='Path to the traces to run', default='./traces')
  parser.add_argument('--output_path', type=str, help='Path to the output of the runs', default='./runs')
  parser.add_argument('--thread_count', type=int, help='Number of threads', default=4)
  args = parser.parse_args()

  main(args.base_config, args.trace_path, args.output_path, args.thread_count)