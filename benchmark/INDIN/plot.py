from jinja2 import Environment
import pandas as pd

scalability_template = """
\\begin{tikzpicture}
\\begin{groupplot}[
    group style={
        group size=3 by 2,
        xlabels at=edge bottom,
        ylabels at=edge left,
    },
    legend style={
        fill=none, draw=none,
        anchor=south, at={(0.5,1.2)},
        legend columns=-1 % Align the legend items horizontally
    },
    footnotesize,
    xlabel={Num Runs},
    ylabel={Mean Execution Time [ms]},
    xtick={
        {%- for tick in xticks -%}{{- tick -}}{%- if not loop.last -%},{% endif %}{%- endfor -%}
        },
    xticklabels={
        {%- for tick in xticks -%}{{- tick -}}{%- if not loop.last -%},{% endif %}{%- endfor -%}
        },
    ymajorgrids=true,
    grid style=dashed]
{% for benchmark in benchmark_data %}
    \\nextgroupplot[title=\\textbf{ {{- benchmark -}} },width=6cm, height=4cm,xlabel style={font=\\footnotesize},ylabel style={font=\\footnotesize, yshift=-0.1cm}]

        \\addplot[name path={{- benchmark -}}_lf_upper,forget plot,draw=none,blue!20] coordinates {
{% for num_runs in benchmark_data[benchmark]['lf'] %}
            ({{ num_runs }}, {{- benchmark_data[benchmark]['lf'][num_runs][0] + benchmark_data[benchmark]['lf'][num_runs][1] -}})
{%- endfor -%}
        };
        \\addplot[name path={{- benchmark -}}_lf_lower,forget plot,draw=none,blue!20] coordinates {
{% for num_runs in benchmark_data[benchmark]['lf'] %}
            ({{ num_runs }}, {{- benchmark_data[benchmark]['lf'][num_runs][0] - benchmark_data[benchmark]['lf'][num_runs][1] -}})
{%- endfor -%}
        };
        \\addplot[fill=blue!20,opacity=0.4,forget plot] fill between[of={{- benchmark -}}_lf_upper and {{ benchmark -}}_lf_lower];

        \\addplot[dashed,mark=*,blue!60] plot coordinates {
{% for num_runs in benchmark_data[benchmark]['lf'] %}
            ({{ num_runs }}, {{ benchmark_data[benchmark]['lf'][num_runs][0] }})
{%- endfor -%}
        };
{% if loop.index == 2 %}        \\addlegendentry{Lingua Franca (Baseline)}{% endif %}


        \\addplot[name path={{- benchmark -}}_glacier_upper,forget plot,draw=none,red!20] coordinates {
{% for num_runs in benchmark_data[benchmark]['glacier'] %}
            ({{ num_runs }}, {{- benchmark_data[benchmark]['glacier'][num_runs][0] + benchmark_data[benchmark]['glacier'][num_runs][1] -}})
{%- endfor -%}
        };
        \\addplot[name path={{- benchmark -}}_glacier_lower,forget plot,draw=none,red!20] coordinates {
{% for num_runs in benchmark_data[benchmark]['glacier'] %}
            ({{ num_runs }}, {{- benchmark_data[benchmark]['glacier'][num_runs][0] - benchmark_data[benchmark]['glacier'][num_runs][1] -}})
{%- endfor -%}
        };
        \\addplot[fill=red!20,forget plot,opacity=0.4] fill between[of={{- benchmark -}}_glacier_upper and {{ benchmark -}}_glacier_lower];

        \\addplot[smooth,mark=*,red!60] plot coordinates {
{% for num_runs in benchmark_data[benchmark]['glacier'] %}
            ({{ num_runs }}, {{ benchmark_data[benchmark]['glacier'][num_runs][0] }})
{%- endfor -%}
        };
{% if loop.index == 2 %}        \\addlegendentry{\\toolname{}}{% endif %}






{%- endfor -%}
\\end{groupplot}
\\end{tikzpicture}%
"""


def main():
    scalability_df = pd.read_csv("scalability.csv")
    xticks = scalability_df["num_runs"].unique()
    xticks.sort()
    xticks = xticks.tolist()
    # keep only 5 ticks
    xticks = xticks[::int(len(xticks)/5)]

    colors = ["blue", "green", "orange", "purple", "yellow", "brown"]
    color_map = {}

    # group the dataframe by benchmark_dir and Bench name
    benchmark_data = {}
    i = 0
    for key, group in scalability_df.groupby(["benchmark", "Bench name"]):
        bench_name = key[1]
        benchmark = key[0]     
        benchmark = benchmark.split("'")[1]
        benchmark_dir = benchmark.replace("_", " ").title()

        if benchmark_dir not in color_map:
            color_map[benchmark_dir] = colors[i%len(colors)]
            i += 1
            
        if benchmark_dir not in benchmark_data:
            benchmark_data[benchmark_dir] = {
                "color": color_map[benchmark_dir]
            }
        if bench_name not in benchmark_data[benchmark_dir]:
            benchmark_data[benchmark_dir][bench_name] = {}
        for index, row in group.iterrows():
            benchmark_data[benchmark_dir][bench_name][row["num_runs"]] = (round(row["Mean"]*1000,2), round(row["StdDev"]*1000,2))


    env = Environment()
    template = env.from_string(scalability_template)
    rendered = template.render(xticks=xticks, benchmark_data=benchmark_data)
    with open("scalability_benchmarks.tex", "w") as f:
        f.write(rendered)

if __name__ == "__main__":
    main()