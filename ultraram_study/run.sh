#!/bin/bash

AE_SLURM_PART_NAME="cpu_part"
SCRIPTS_DIR="scripts"

echo "[INFO] Generating trace combinations for singlecore and multicore traces"
python3 $SCRIPTS_DIR/setup_trace_combinations.py \
    --output_path "$PWD/traces" \
    --mpki_file "$PWD/traces/mpki.csv" \
    --multi_core --single_core

echo "[INFO] Generating Ramulator2 configurations and run scripts for ULTRARAM study"
python3 $SCRIPTS_DIR/setup_scripts.py \
    --working_directory "$PWD" \
    --base_config "$PWD/base_config.yaml" \
    --trace_combination "$PWD/traces/trace_combinations.txt" \
    --trace_directory "$PWD/traces" \
    --result_directory "$PWD/results" \
    --partition_name "$AE_SLURM_PART_NAME" \
    --output_file "$PWD/run_slurm.sh"

echo "[INFO] Starting Ramulator2 ULTRARAM simulations"
python3 $SCRIPTS_DIR/execute_scripts.py \
    # --run_slurm

echo "[INFO] Checking and removing 'run_slurm.sh', 'run_personal.sh' and 'run_scripts' folder if they exist"
if [ -d "$PWD/run_scripts" ]; then
    rm -rf "$PWD/run_scripts/"
fi

if [ -f "$PWD/run_slurm.sh" ]; then
    rm -rf "$PWD/run_slurm.sh"
fi

if [ -f "$PWD/run_personal.sh" ]; then
    rm -rf "$PWD/run_personal.sh"
fi
