import os.path
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
from pybenchmark.utilities.utility import col_bench_name_str

def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)#capture_output=True) 

def compile_benchmark(benchmark_dir: str) -> subprocess.CompletedProcess:
    return run_cmd([f'cd {benchmark_dir} && lfc src/Main.lf'])

def run_benchmark(benchmark_dir: str) -> subprocess.CompletedProcess:
    return run_cmd([f'cd {benchmark_dir} && ./bin/Main'])


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
    benchmark_dir=[
        dir for dir in os.listdir(os.path.dirname(__file__)) if dir not in ['Empty', '.venv'] and os.path.isdir(os.path.join(os.path.dirname(__file__), dir))
    ]
)
class GlacierBenchmark:

    def __init__(self, benchmark_dir:str):
        self._benchmark_dir = benchmark_dir
        # Benchmarks may be compiled before running
        # compile_benchmark('Empty')
        # compile_benchmark(benchmark_dir)
        pass

    @BenchmarkRunner.overhead
    def overhead(self) -> subprocess.CompletedProcess:
        return run_benchmark('Empty')

    @BenchmarkRunner.benchmark
    def glacier(self) -> subprocess.CompletedProcess:
        return run_benchmark(self._benchmark_dir)
    
    # add here the execution of the original LF benchmarks
    # @BenchmarkRunner.benchmark
    # def lf(self) -> subprocess.CompletedProcess:
    #     return run_benchmark(...)
    

if __name__ == "__main__":
    import sys

    config = BenchmarkConfig(
        time_counter=TimedeltaCounter(wall_time=True),
        jitting=False
    )

    results = BenchmarkRunner.run_benchmarks_in_executor(GlacierBenchmark, config=config)
    results.plot()

    df_res = results.get_results()
    # to store the results in a csv file
    # df_res.to_csv(output_path)