#-------------------------------------------------------------------------------
#------------------------ SLURM CONFIGURATION PARAMETERS -----------------------
#-------------------------------------------------------------------------------

SLURM_USER = '$USER'
SLURM_MAX_JOBS = 100
SLURM_RETRY_DELAY = 1 * 60
SLURM_SUBMIT_DELAY = 0.1
SLURM_EXCLUDE_NODES = 'kratos[10-20]'

#-------------------------------------------------------------------------------
#----------------------- PERSONAL CONFIGURATION PARAMETERS ---------------------
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#----------------------- RAMULATOR CONFIGURATION PARAMETERS --------------------
#-------------------------------------------------------------------------------

device_list = ['DDR5', 'URAM5',]

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
