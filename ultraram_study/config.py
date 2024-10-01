#-------------------------------------------------------------------------------
#------------------------ SLURM CONFIGURATION PARAMETERS -----------------------
#-------------------------------------------------------------------------------

SLURM_USER = 'yusufa'
SLURM_MAX_JOBS = 100
SLURM_RETRY_DELAY = 1 * 60
SLURM_SUBMIT_DELAY = 0.1

#-------------------------------------------------------------------------------
#----------------------- RAMULATOR CONFIGURATION PARAMETERS --------------------
#-------------------------------------------------------------------------------

device_list     = ['DDR5', 'URAM5',]
org_list        = ['16Gb_x8']
row_policy_list = ['ClosedRowPolicy', 'OpenRowPolicy']

refresh_manager = {
  'DDR4'   : 'AllBank',
  'DDR5'   : 'AllBank',
  'URAM4'  : 'NoRefresh',
  'URAM5'  : 'NoRefresh',
}

timing_list = {
  'DDR4'   : ['3200AA'],
  'DDR5'   : ['3200AN'],
  'URAM4'  : ['3200AA'],
  'URAM5'  : ['3200AN'],
}

import pandas as pd
scale_list = pd.read_csv('scaling.csv')
for column in scale_list.columns[1:]:
  scale_list[column] = scale_list[column].astype(float)