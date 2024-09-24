#!/bin/bash

AE_SLURM_PART_NAME="cpu_part"

echo "[INFO] Generating Ramulator2 configurations and run scripts for ULTRARAM study"
python3 setup_scripts.py \
    --working_directory "$PWD" \
    --base_config "$PWD/base_config.yaml" \
    --trace_combination "$PWD/traces/multicore_traces.txt" \
    --trace_mpki "$PWD/traces/mpki.csv" \
    --trace_directory "$PWD/traces" \
    --result_directory "$PWD/results" \
    --partition_name "$AE_SLURM_PART_NAME"

echo "[INFO] Starting Ramulator2 ULTRARAM simulations"
python3 execute_scripts.py

echo "[INFO] Removing 'run.sh' and 'run_scripts' folder"
rm "$PWD/run.sh" 
rm -rf "$PWD/run_scripts/" 