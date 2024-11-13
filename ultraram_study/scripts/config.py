#-------------------------------------------------------------------------------
#------------------------ SLURM CONFIGURATION PARAMETERS -----------------------
#-------------------------------------------------------------------------------

SLURM_USER = '$USER'
SLURM_MAX_JOBS = 100
SLURM_RETRY_DELAY = 1 * 60
SLURM_SUBMIT_DELAY = 0.1
SLURM_EXCLUDE_NODES = 'kratos[10]'

#-------------------------------------------------------------------------------
#----------------------- PERSONAL CONFIGURATION PARAMETERS ---------------------
#-------------------------------------------------------------------------------

PERS_NUM_THREADS = 12

#-------------------------------------------------------------------------------
#----------------- ADDITIONAL RAMULATOR CONFIGURATION FUNCTIONS ----------------
#-------------------------------------------------------------------------------

import pandas as pd
df = pd.read_csv('area_scaling.csv', skipinitialspace=True)

def add_uram_scales(config, area_scale, voltage_scale):
  val = df[(df['area_scaling_factor'] == area_scale) & (df['vdd_vpp_scaling_factor'] == voltage_scale)]
  timings = {col.replace('(ns)', ''): float(val[col].iloc[0]) for col in val.columns if col.endswith('(ns)')}
  currents = {col.replace('(ma)', ''): float(val[col].iloc[0]) for col in val.columns if col.endswith('(ma)')}

  config['MemorySystem']['DRAM']['voltageScales'] = {}
  config['MemorySystem']['DRAM']['currentScales'] = {}
  config['MemorySystem']['DRAM']['timingScales']  = {}

  config['MemorySystem']['DRAM']['voltageScales']['VDD'] = voltage_scale
  config['MemorySystem']['DRAM']['voltageScales']['VPP'] = voltage_scale
  for current, value in currents.items():
    config['MemorySystem']['DRAM']['currentScales'][current.upper()] = value
  for timing, value in timings.items():
    config['MemorySystem']['DRAM']['timingScales'][timing] = value

#-------------------------------------------------------------------------------
#-------------------- DEFAULT RAMULATOR CONFIGURATION PARAMETERS ---------------
#-------------------------------------------------------------------------------

device_list = ['DDR5', 'URAM5']

org_list = {
  'DDR5' : ['16Gb_x8'],
  'URAM5': ['16Gb_x8']
}

row_policy_list = {
  'DDR5' :  ['OpenRowPolicy'],
  'URAM5':  ['OpenRowPolicy']
}

refresh_manager_list = {
  'DDR5'   : ['AllBank'],
  'URAM5'  : ['NoRefresh'],
}

timing_list = {
  'DDR5'   : ['3200AN'],
  'URAM5'  : ['3200AN'],
}

plugin_list = {
  'DDR5'   : [('CommandCounter', 'cmd_counts'), ('RFMManager', '')],
  'URAM5'  : [('CommandCounter', 'cmd_counts')]
}

area_scaling_list = {
  'DDR5'   : [1.0],
  'URAM5'  : [float(scale) for scale in df['area_scaling_factor'].unique()]
}

voltage_scaling_list = {
  'DDR5'   : [1.0],
  'URAM5'  : [float(scale) for scale in df['vdd_vpp_scaling_factor'].unique()]
}
