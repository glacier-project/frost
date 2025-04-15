# !/bin/bash

benchmark_dir=$1
echo "Running benchmark in $benchmark_dir"
export NUM_RUNS=$2
echo "Number of runs: $NUM_RUNS"
export RECIPE_PATH=$3
echo "Recipe path: $RECIPE_PATH"
export CONDITIONS_PATH=$4
echo "Conditions path: $CONDITIONS_PATH"
cd $benchmark_dir 
./bin/Main #&>/dev/null