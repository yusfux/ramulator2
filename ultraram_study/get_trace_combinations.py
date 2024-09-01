import random

num_samples_per_group = 5

output_filename = "traces/multicore_traces.txt"
output_file = open(output_filename, "w")

group_list = ["HHHH", "HHHL", "HHLL", "HLLL", "LLLL"]


high_traces = ['500.perlbench', '502.gcc', '505.mcf', '507.cactuBSSN', '508.namd', '544.nab', '549.fotonik3d', '557.xz']
low_traces = ['510.parest', '511.povray', '519.lbm', '520.omnetpp', '523.xalancbmk', '525.x264', '526.blender', '531.deepsjeng', '538.imagick', '541.leela',]

for group in group_list:
    num_h = group.count("H")
    num_l = group.count("L")

    for i in range(num_samples_per_group):
        highs = random.sample(high_traces, num_h)
        lows = random.sample(low_traces, num_l)

        traces = highs + lows
        output_file.write(group + str(i) + ",")
        output_file.write(",".join(traces) + "\n")
