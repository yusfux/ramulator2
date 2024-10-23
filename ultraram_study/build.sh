#!/bin/bash

cd ../build/
cmake ..
make -j 16
cp ./ramulator2 ../ultraram_study/ramulator2