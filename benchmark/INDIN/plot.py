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
    width=9cm, height=6cm,
    legend style={
        fill=none, draw=none,
        anchor=south, at={(0.5,1.0)},
        legend columns=-1 % Align the legend items horizontally
    },
    footnotesize,
    xlabel={Num Runs},
    ylabel={Mean execution time (ms)},
    xtick={
        {%- for tick in xticks -%}{{- tick -}}{%- if not loop.last -%},{% endif %}{%- endfor -%}
        },
    xticklabels={
        {%- for tick in xticks -%}{{- tick -}}{%- if not loop.last -%},{% endif %}{%- endfor -%}
        },
    ymajorgrids=true,
    grid style=dashed]
{% for benchmark in benchmark_data %}
    \\nextgroupplot
        \\addplot[smooth,mark=*,blue!40] plot coordinates {
{% for num_runs in benchmark_data[benchmark]['glacier'] %}
            ({{ num_runs }}, {{ benchmark_data[benchmark]['glacier'][num_runs] }})
{%- endfor -%}
        };
{% if loop.index == 2 %}        \\addlegendentry{\\toolname{}}{% endif %}
        \\addplot[dashed,mark=*,red!40] plot coordinates {
{% for num_runs in benchmark_data[benchmark]['lf'] %}
            ({{ num_runs }}, {{ benchmark_data[benchmark]['lf'][num_runs] }})
{%- endfor -%}
        };
{% if loop.index == 2 %}        \\addlegendentry{\\gls{lf}}{% endif %}
{%- endfor -%}
\\end{groupplot}

\\end{tikzpicture}%
"""


def main():
    scalability_df = pd.read_csv("scalability.csv")
    xticks = scalability_df["num_runs"].unique()
    xticks.sort()
    xticks = xticks.tolist()

    colors = ["blue", "green", "orange", "purple", "yellow", "brown"]
    color_map = {}

    # group the dataframe by benchmark_dir and Bench name
    benchmark_data = {}
    i = 0
    for key, group in scalability_df.groupby(["benchmark_dir", "Bench name"]):
        bench_name = key[1]
        benchmark_dir = key[0]     
        benchmark_dir = benchmark_dir.replace("_", " ").title()

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
            benchmark_data[benchmark_dir][bench_name][row["num_runs"]] = round(row["Mean"]*1000,2)


    env = Environment()
    template = env.from_string(scalability_template)
    rendered = template.render(xticks=xticks, benchmark_data=benchmark_data)
    with open("output.tex", "w") as f:
        f.write(rendered)

if __name__ == "__main__":
    main()