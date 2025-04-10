# !/bin/bash

function compile_lf_prj() {
    local dir="$1"
    
    # check if the directory exists
    if [[ -d "$dir" ]]; then
        # move to the directory
        cd "$dir" || exit
        # run the command
        lfc src/Main.lf
        # move back to the original directory
        cd - || exit
    else
        echo "Directory $dir does not exist."
    fi
}

# compile the empty project
compile_lf_prj "empty"

# compile the all the benchmark projects
for dir in */; do
    # check if the directory is not .venv, config or empty dirs
    if [[ "$dir" != ".venv/" && "$dir" != "config/" && "$dir" != "empty/" ]]; then
        compile_lf_prj "$dir/glacier"
        compile_lf_prj "$dir/lf"
    fi
done