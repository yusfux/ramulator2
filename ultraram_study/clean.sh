#!/bin/bash

if [ -d "$PWD/results" ]; then
    rm -rf "$PWD/results/"
fi

if [ -d "$PWD/run_scripts" ]; then
    rm -rf "$PWD/run_scripts/"
fi

if [ -f "$PWD/run_slurm.sh" ]; then
    rm -rf "$PWD/run_slurm.sh"
fi

if [ -f "$PWD/run_personal.sh" ]; then
    rm -rf "$PWD/run_personal.sh"
fi