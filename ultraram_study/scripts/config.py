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

PERS_NUM_THREADS = 8

#-------------------------------------------------------------------------------
#----------------- ADDITIONAL RAMULATOR CONFIGURATION FUNCTIONS ----------------
#-------------------------------------------------------------------------------

import csv
def get_uram_timings():
  data = []
  with open('area_scaling.csv', 'r') as file:
    for row in csv.DictReader(file):
      for key, value in row.items():
        row[key] = float(value)
      data.append(row)
  return data

def add_uram_timings(config, scale, list):
  config['MemorySystem']['DRAM']['scales'] = {}
  for element in list:
    if element['area_scaling'] == scale:
      for key, value in element.items():
        config['MemorySystem']['DRAM']['scales'][key] = value

area_scaling_list = get_uram_timings()

#-------------------------------------------------------------------------------
#-------------------- DEFAULT RAMULATOR CONFIGURATION PARAMETERS ---------------
#-------------------------------------------------------------------------------

device_list = ['DDR5', 'URAM5']

org_list = {
  'DDR5' : ['16Gb_x8'],
  'URAM5': ['16Gb_x8']
}

row_policy_list = {
  'DDR5' :  ['ClosedRowPolicy', 'OpenRowPolicy'],
  'URAM5':  ['ClosedRowPolicy', 'OpenRowPolicy']
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
  'DDR5'   : [('WriteCounter', 'wr_counts'), ('CommandCounter', 'cmd_counts'), ('RFMManager', '')],
  'URAM5'  : [('WriteCounter', 'wr_counts'), ('CommandCounter', 'cmd_counts')]
}

scale_list = {
  'DDR5'   : [1.0],
  'URAM5'  : [scale['area_scaling'] for scale in area_scaling_list]
}
