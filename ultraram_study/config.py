SLURM_USER = 'yusufa'
SLURM_MAX_JOBS = 100
SLURM_RETRY_DELAY = 1 * 60
SLURM_SUBMIT_DELAY = 0.1

device_list     = ['DDR4', 'DDR5', 'URAM4', 'URAM5']
org_list        = ['16Gb_x8']
timing_list     = {'DDR4': '3200AA', 'URAM4': '3200AA', 'DDR5': '3200AN', 'URAM5': '3200AN',}
row_policy_list = ['OpenRowPolicy']

refresh_manager = {'DDR4': 'AllBank', 'DDR5': 'AllBank', 'URAM4': 'NoRefresh', 'URAM5': 'NoRefresh'}
ultraram_trcd   = {'URAM4': '100', 'FURAM4': '10', 'URAM5': '100', 'FURAM5': '10'}

trace_list = ['500.perlbench', '502.gcc'      , '505.mcf'      , '507.cactuBSSN', '508.namd',
              '510.parest'   , '511.povray'   , '519.lbm'      , '520.omnetpp'  , '523.xalancbmk', 
              '525.x264'     , '526.blender'  , '531.deepsjeng', '538.imagick'  , '541.leela',
              '544.nab'      , '549.fotonik3d', '557.xz']