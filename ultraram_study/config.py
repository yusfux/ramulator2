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

device_list     = ['DDR4', 'DDR5', 'URAM4', 'URAM5', 'FURAM4', 'FURAM5']
org_list        = ['16Gb_x8']
row_policy_list = ['ClosedRowPolicy', 'OpenRowPolicy']

refresh_manager = {
  'DDR4'   : 'AllBank',
  'DDR5'   : 'AllBank',
  'URAM4'  : 'NoRefresh',
  'URAM5'  : 'NoRefresh',
  'FURAM4' : 'NoRefresh',
  'FURAM5' : 'NoRefresh',
}

timing_list = {
  'DDR4'   : ['3200AA'],
  'DDR5'   : ['3200AN'],
  'URAM4'  : ['3200AA'],
  'URAM5'  : ['3200AN'],
  'FURAM4' : ['3200AA'],
  'FURAM5' : ['3200AN']
  }

trcd_list = {
  'URAM4'  : '100',
  'URAM5'  : '100',
  'FURAM4' : '10',
  'FURAM5' : '10'
}