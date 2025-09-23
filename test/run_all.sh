#!/bin/bash

# Script to build and run Lingua Franca tests
# Usage: ./run_all.sh [--build-only|--run-only|--help] [file1.lf file2.lf ...]

# Stop if any test fails
set -e

# Get all the files in the src directory
get_all_lf_files() {
    find src -type f -name "*.lf" 2>/dev/null || true
}

# Display usage information
show_help() {
    cat << EOF
Usage: $0 [OPTIONS] [FILES...]

Build and run Lingua Franca tests.

OPTIONS:
    --build-only    Only build the specified tests (or all if none specified)
    --run-only      Only run the specified tests (or all if none specified)
    --help, -h      Show this help message

FILES:
    Specify individual .lf files to process. If none specified, all .lf files
    in the src directory will be processed.

Examples:
    $0                          # Build and run all tests
    $0 --build-only             # Build all tests only
    $0 --run-only src/Test1.lf  # Run only Test1
    $0 src/Test1.lf src/Test2.lf # Build and run Test1 and Test2

EOF
}

# Validate that a file exists and is a .lf file
validate_file() {
    local file="$1"
    if [ ! -f "$file" ]; then
        echo "Error: File '$file' does not exist" >&2
        return 1
    fi
    if [ "${file##*.}" != "lf" ]; then
        echo "Error: File '$file' is not a .lf file" >&2
        return 1
    fi
    return 0
}

# Build tests from the provided file list
build_tests() {
    local files=("$@")
    local failed_builds=0
    
    if [ ${#files[@]} -eq 0 ]; then
        echo "No files to build"
        return 0
    fi
    
    echo "Building ${#files[@]} test(s)..."
    
    for file in "${files[@]}"; do
        if ! validate_file "$file"; then
            failed_builds=$((failed_builds + 1))
            continue
        fi
        
        # Convert the name to snake_case
        local basename=$(basename "$file" .lf)
        local snake_case_name=$(echo "$basename" | sed -r 's/([a-z])([A-Z])/\1_\2/g' | tr '[:upper:]' '[:lower:]')
        
        echo "Building ${basename} test..."
        if ! lfc "$file"; then
            echo "Error: Failed to build $file" >&2
            failed_builds=$((failed_builds + 1))
        fi
    done
    
    if [ $failed_builds -gt 0 ]; then
        echo "Warning: $failed_builds build(s) failed" >&2
        return 1
    fi
    
    echo "All builds completed successfully"
    return 0
}

# Run tests from the provided file list
run_tests() {
    local files=("$@")
    local failed_runs=0
    
    if [ ${#files[@]} -eq 0 ]; then
        echo "No files to run"
        return 0
    fi
    
    echo "Running ${#files[@]} test(s)..."
    
    for file in "${files[@]}"; do
        if ! validate_file "$file"; then
            failed_runs=$((failed_runs + 1))
            continue
        fi
        
        # Convert the name to snake_case
        local basename=$(basename "$file" .lf)
        local snake_case_name=$(echo "$basename" | sed -r 's/([a-z])([A-Z])/\1_\2/g' | tr '[:upper:]' '[:lower:]')
        local binary_path="./bin/${basename}"
        local config_path="resources/${snake_case_name}/frost_config.yml"
        
        echo "Running ${basename} test..."
        
        # Check if binary exists
        if [ ! -f "$binary_path" ]; then
            echo "Error: Binary '$binary_path' not found. Did you build the test first?" >&2
            failed_runs=$((failed_runs + 1))
            continue
        fi
        
        # Check if config exists (optional warning)
        if [ ! -f "$config_path" ]; then
            echo "Warning: Config file '$config_path' not found, proceeding without it"
            if ! "$binary_path"; then
                echo "Error: Failed to run $basename" >&2
                failed_runs=$((failed_runs + 1))
            fi
        else
            if ! (export FROST_CONFIG="$config_path" && "$binary_path"); then
                echo "Error: Failed to run $basename" >&2
                failed_runs=$((failed_runs + 1))
            fi
        fi
    done
    
    if [ $failed_runs -gt 0 ]; then
        echo "Warning: $failed_runs test(s) failed" >&2
        return 1
    fi
    
    echo "All tests completed successfully"
    return 0
}

# Parse command line arguments
build_only=false
run_only=false
files=()

while [ $# -gt 0 ]; do
    case "$1" in
        --help|-h)
            show_help
            exit 0
            ;;
        --build-only)
            build_only=true
            shift
            ;;
        --run-only)
            run_only=true
            shift
            ;;
        --*)
            echo "Error: Unknown option '$1'" >&2
            echo "Use --help for usage information" >&2
            exit 1
            ;;
        *)
            files+=("$1")
            shift
            ;;
    esac
done

# Validate conflicting options
if [ "$build_only" = true ] && [ "$run_only" = true ]; then
    echo "Error: --build-only and --run-only cannot be used together" >&2
    exit 1
fi

# If no files specified, get all .lf files
if [ ${#files[@]} -eq 0 ]; then
    mapfile -t files < <(get_all_lf_files)
    if [ ${#files[@]} -eq 0 ]; then
        echo "No .lf files found in src directory" >&2
        exit 1
    fi
    echo "Found ${#files[@]} .lf file(s) in src directory"
fi

# Execute based on options
if [ "$build_only" = true ]; then
    build_tests "${files[@]}"
elif [ "$run_only" = true ]; then
    run_tests "${files[@]}"
else
    build_tests "${files[@]}" && run_tests "${files[@]}"
fi