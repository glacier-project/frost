import os.path
import time
import subprocess

from pybenchmark.exporters.table_exporter import TableExporter
from pybenchmark.benchmark_runner import BenchmarkRunner
from pybenchmark.benchmarks.config.benchmark_config import BenchmarkConfig
from pybenchmark.benchmarks.time.timedelta_counter import TimedeltaCounter
from pybenchmark.columns.statistical_column import StatisticalColumn
from pybenchmark.columns.statistical_column import StatisticalColumnValue
from pybenchmark.exporters.histogram_exporter import HistogramExporter
from pybenchmark.columns.formatter.formatter import Formatter
import pandas as pd
from pybenchmark.columns.mean_column import col_mean
from pybenchmark.utilities.utility import col_bench_name_str, col_time

def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)# , capture_output=True)#

def run_benchmark(benchmark_dir: str) -> subprocess.CompletedProcess:
    return run_cmd([f'bash run_benchmark.sh {benchmark_dir}'])


class HistogramPlot(HistogramExporter):
    def __init__(self):
        super().__init__("HistrogramPlot")

    def get_figure(self, df: pd.DataFrame, formatter: Formatter):
        x = "benchmark_dir"
        y = formatter.get_col_name(col_mean)
        color = col_bench_name_str
        fig, ax = super()._create_histogram_figure(df, x, y, color)
        ax.set(xlabel=x)
        ax.set(ylabel=y)
        ax.set(title=self._name)
        ax.legend()
        return fig, ax

@BenchmarkRunner.columns(StatisticalColumn(columns=[StatisticalColumnValue.ERROR, StatisticalColumnValue.MEDIAN, StatisticalColumnValue.STD_DEV, StatisticalColumnValue.MAX, StatisticalColumnValue.MIN], remove_outliers=True))
@BenchmarkRunner.exporters(TableExporter, HistogramPlot)
@BenchmarkRunner.params(
    benchmark_dir=
    [
        'ping_pong',
        'alarm',
        'ring',
        'safe_read',
        'traffic_light',
        'train_door',
    ]
)
class GlacierBenchmark:

    def __init__(self, benchmark_dir:str):
        self._benchmark_dir = benchmark_dir
    
    @BenchmarkRunner.benchmark
    def glacier(self) -> subprocess.CompletedProcess:
        return run_benchmark(f"{self._benchmark_dir}/glacier")
    
    @BenchmarkRunner.baseline
    @BenchmarkRunner.benchmark
    def lf(self) -> subprocess.CompletedProcess:
        return run_benchmark(f"{self._benchmark_dir}/lf")

@BenchmarkRunner.columns(StatisticalColumn(columns=[StatisticalColumnValue.ERROR, StatisticalColumnValue.MEDIAN, StatisticalColumnValue.STD_DEV, StatisticalColumnValue.MAX, StatisticalColumnValue.MIN], remove_outliers=True))
@BenchmarkRunner.exporters(TableExporter, HistogramPlot)
@BenchmarkRunner.params(
    benchmark_dir=
    [
        '../../examples/ICE/',
    ]
)
class ICEBenchmark:

    def __init__(self, benchmark_dir:str):
        self._benchmark_dir = benchmark_dir

    @BenchmarkRunner.benchmark
    def glacier(self) -> subprocess.CompletedProcess:
        return run_benchmark(f"{self._benchmark_dir}")    

if __name__ == "__main__":
    import sys

    # build all the benchmarks
    print("Building all benchmarks...")
    run_cmd(['bash build_all_benchmarks.sh'])
    print("Benchmarks built successfully.")
    
    config = BenchmarkConfig(
        time_counter=TimedeltaCounter(wall_time=True),
        jitting=False,
        pilot_min_iteration_count=0,
        pilot_max_iteration_count=0,
        warmup_min_iteration_count=0,
        warmup_max_iteration_count=0,
        bench_min_iteration_count=50,
        bench_max_iteration_count=50,
    )

    results = BenchmarkRunner.run_benchmarks_in_executor(ICEBenchmark, config=config)
    results.plot()
    df_res = results.get_results()
    # uncomment this line to save the results in a csv file
    # df_res.to_csv(output_path)

    results = BenchmarkRunner.run_benchmarks_in_executor(GlacierBenchmark, config=config)
    results.plot()
    df_res = results.get_results()
    # uncomment this line to save the results in a csv file
    # df_res.to_csv(output_path)