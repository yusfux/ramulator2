#!/bin/bash

cd ../build/
cmake ..
make -j 32
cp ./ramulator2 ../ultraram_study/ramulator2