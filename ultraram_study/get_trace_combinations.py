# directly yanked from yct, with minor modifications

import random

output_filename = 'traces/multicore_traces.txt'
mpki_path = 'traces/mpki.csv'

trace_bases = [("H", 25), ("M", 5), ("L", 0)]

trace_groups = {
    "H": [],
    "M": [],
    "L": []
}

with open(mpki_path, 'r') as f:
  for line in f:
    line = line.strip()
    trace_name, trace_mpki = line.split(',')
    for label, base in trace_bases:
      if float(trace_mpki) > base:
        trace_groups[label].append(trace_name)
        break

mix_groups = [
  ("HHHH", 10),
  ("MMMM", 10),
  ("LLLL", 10),
  ("HHMM", 10),
  ("MMLL", 10),
  ("LLHH", 10)
]


def mix_idx_hash(mix_arr):
  val = 0
  for item in mix_arr:
      val *= 1e3
      val += item
  return val

all_mixes = set()
mix_counter = 0
with open(output_filename, 'w') as output_file:
  for mix_types, count in mix_groups:
    for i in range(count):
      num_retry = 10
      while num_retry > 0:
        num_retry -= 1
        mix_traces = []
        mix_idx = []
        for work_type in mix_types:
          work_idx = random.choice(range(len(trace_groups[work_type])))
          mix_idx.append(work_idx)
          mix_traces.append(trace_groups[work_type][work_idx])
        mix_hash = mix_idx_hash(mix_idx)
        if mix_hash not in all_mixes:
          all_mixes.add(mix_hash)
          break

      if num_retry > 0:
        output_file.write(f"Mix{mix_counter},{mix_types},{','.join(mix_traces)}\n")
        mix_counter += 1
