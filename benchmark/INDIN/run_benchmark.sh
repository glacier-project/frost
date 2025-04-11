# !/bin/bash

benchmark_dir=$1
echo "Running benchmark in $benchmark_dir"
export NUM_RUNS=$2
echo "Number of runs: $NUM_RUNS"
cd $benchmark_dir && ./bin/Main #&>/dev/null