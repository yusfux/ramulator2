import random
import argparse

argparser = argparse.ArgumentParser(
  description='Create trace combination file for singlecore/multicore benchmarks..'
)

argparser.add_argument('-op', '--output_path', default='traces')
argparser.add_argument('-mf', '--mpki_file', default='traces/mpki.csv')
argparser.add_argument('-sc', '--single_core', action=argparse.BooleanOptionalAction)
argparser.add_argument('-mc', '--multi_core', action=argparse.BooleanOptionalAction)

args = argparser.parse_args()

OUTPUT_PATH = args.output_path
MPKI_FILE   = args.mpki_file
SINGLE_CORE = args.single_core
MULTI_CORE  = args.multi_core

#TODO: need to find more robust way to determine the mid point
MID_POINT = 10

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def get_singlecore_traces():
  traces = []
  with open(MPKI_FILE, 'r') as f:
    for line in f:
      line = line.strip()
      traces.append(line.split(',')[0])

  return [f'{trace},{trace}' for trace in traces]

def get_multicore_traces():
  traces = []
  high_traces = []
  low_traces = []
  with open(MPKI_FILE, 'r') as f:
    for line in f:
      line = line.strip()
      trace_name, trace_mpki = line.split(',')
      if float(trace_mpki) > MID_POINT:
        high_traces.append(trace_name)
      else:
        low_traces.append(trace_name)
    
  for group in ['HHHH', 'HHHL', 'HHLL', 'HLLL', 'LLLL']:
    num_h = group.count('H')
    num_l = group.count('L')

    for i in range(2):
      highs = random.sample(high_traces, num_h)
      lows = random.sample(low_traces, num_l)

      traces.append(group + str(i) + ',' + ','.join(highs + lows))

  return traces


traces = []
if SINGLE_CORE:
  traces.append(get_singlecore_traces())
if MULTI_CORE:
  traces.append(get_multicore_traces())

with open(f'{OUTPUT_PATH}/trace_combinations.txt', 'w') as f:
  for trace in traces:
    f.write('\n'.join(trace) + '\n')