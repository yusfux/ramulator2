#!/bin/bash

AE_SLURM_PART_NAME="cpu_part"
SCRIPTS_DIR="scripts"

echo "[INFO] Generating trace combinations for singlecore and multicore traces"
python3 $SCRIPTS_DIR/setup_trace_combinations.py \
    --trace_path "$PWD/traces" \
    --output_path "$PWD/traces" \
    --mpki_file "$PWD/traces/mpki.csv" \
    --single_core --multi_core

echo "[INFO] Generating Ramulator2 configurations and run scripts for ULTRARAM study"
python3 $SCRIPTS_DIR/setup_scripts.py \
    --working_directory "$PWD" \
    --base_config "$PWD/base_config.yaml" \
    --trace_combination "$PWD/traces/trace_combinations.txt" \
    --trace_directory "$PWD/traces" \
    --result_directory "$PWD/results" \
    --partition_name "$AE_SLURM_PART_NAME" \
    --output_file "$PWD/sbatch_runs.sh"

# echo "[INFO] Starting Ramulator2 ULTRARAM simulations"
# python3 $SCRIPTS_DIR/execute_scripts.py

# echo "[INFO] Removing 'sbatch_runs.sh' and 'run_scripts' folder"
# rm -rf "$PWD/run_scripts/" 
# rm "$PWD/sbatch_runs.sh" 
