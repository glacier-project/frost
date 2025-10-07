#!/bin/bash

# Script to build and run Lingua Franca tests
# Usage: ./run_all.sh [--build-only|--run-only|--help] [file1.lf file2.lf ...]

# Don't stop on failures - collect all results for final report
set +e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# Arrays to track test results
BUILD_PASSED=()
BUILD_FAILED=()
RUN_PASSED=()
RUN_FAILED=()
RUN_SKIPPED=()

# Progress bar function
show_progress() {
    local current=$1
    local total=$2
    local prefix=$3
    local test_name=$4
    local bar_length=20
    local percentage=$((current * 100 / total))
    local filled=$((current * bar_length / total))
    local empty=$((bar_length - filled))
    
    printf "\r\033[K${CYAN}%s${RESET} [${GREEN}%s${RESET}%s] ${BOLD}%d/%d${RESET} ${YELLOW}(%d%%)${RESET} ${BLUE}> %s${RESET}" \
        "$prefix" \
        "$(printf "%*s" $filled | tr ' ' '#')" \
        "$(printf "%*s" $empty | tr ' ' '.')" \
        "$current" "$total" "$percentage" "$test_name"
}

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
    
    printf "\n${BOLD}${BLUE}🔨 Building ${#files[@]} test(s)...${RESET}\n"
    local current=0
    
    for file in "${files[@]}"; do
        current=$((current + 1))
        local basename=$(basename "$file" .lf)
        show_progress $current ${#files[@]} "Building" "$basename"
        
        if ! validate_file "$file"; then
            BUILD_FAILED+=("$basename")
            failed_builds=$((failed_builds + 1))
            continue
        fi
        
        # Convert the name to snake_case
        local snake_case_name=$(echo "$basename" | sed -r 's/([a-z])([A-Z])/\1_\2/g' | tr '[:upper:]' '[:lower:]')
        
        # Capture build output to show only on failure
        if build_output=$(lfc "$file" 2>&1); then
            BUILD_PASSED+=("$basename")
        else
            printf "\n"  # New line to preserve progress bar
            echo "Error: Failed to build $file" >&2
            echo "$build_output" >&2
            BUILD_FAILED+=("$basename")
            failed_builds=$((failed_builds + 1))
        fi
    done
    
    echo  # Clear progress bar line
    
    if [ $failed_builds -gt 0 ]; then
        printf "${RED}⚠️  Warning: $failed_builds build(s) failed${RESET}\n" >&2
        return 1
    fi
    
    printf "${GREEN}✅ All builds completed successfully${RESET}\n"
    return 0
}

# Run tests from the provided file list (only successfully built tests)
run_tests() {
    local files=("$@")
    local failed_runs=0
    local runnable_files=()
    local skipped_count=0
    
    # Filter files to only include successfully built tests
    for file in "${files[@]}"; do
        local basename=$(basename "$file" .lf)
        local is_built=false
        
        # If BUILD_PASSED is empty (e.g., --run-only mode), check if binary exists
        if [ ${#BUILD_PASSED[@]} -eq 0 ]; then
            # In run-only mode, check if the binary exists
            if [ -f "./bin/${basename}" ]; then
                is_built=true
            fi
        else
            # Check if this test was successfully built in this session
            for built_test in "${BUILD_PASSED[@]}"; do
                if [ "$built_test" = "$basename" ]; then
                    is_built=true
                    break
                fi
            done
        fi
        
        if [ "$is_built" = true ]; then
            runnable_files+=("$file")
        else
            RUN_SKIPPED+=("$basename")
            skipped_count=$((skipped_count + 1))
        fi
    done
    
    if [ ${#runnable_files[@]} -eq 0 ]; then
        if [ $skipped_count -gt 0 ]; then
            printf "\n${YELLOW}⏭️  All tests skipped due to build failures${RESET}\n"
        else
            echo "No files to run"
        fi
        return 0
    fi
    
    local total_to_run=${#runnable_files[@]}
    printf "\n${BOLD}${CYAN}🚀 Running $total_to_run test(s)...${RESET}"
    if [ $skipped_count -gt 0 ]; then
        printf " ${YELLOW}($skipped_count skipped)${RESET}"
    fi
    printf "\n"
    local current=0
    
    for file in "${runnable_files[@]}"; do
        current=$((current + 1))
        local basename=$(basename "$file" .lf)
        show_progress $current $total_to_run "Running" "$basename"
        
        if ! validate_file "$file"; then
            RUN_FAILED+=("$basename")
            failed_runs=$((failed_runs + 1))
            continue
        fi
        
        # Convert the name to snake_case
        local snake_case_name=$(echo "$basename" | sed -r 's/([a-z])([A-Z])/\1_\2/g' | tr '[:upper:]' '[:lower:]')
        local binary_path="./bin/${basename}"
        local config_path="resources/config/${snake_case_name}.yml"
        
        # Check if binary exists
        if [ ! -f "$binary_path" ]; then
            printf "\n"  # New line to preserve progress bar
            echo "Error: Binary '$binary_path' not found. Did you build the test first?" >&2
            RUN_FAILED+=("$basename")
            failed_runs=$((failed_runs + 1))
            continue
        fi
        
        # Check if config exists (optional warning)
        if [ ! -f "$config_path" ]; then
            if run_output=$("$binary_path" 2>&1); then
                RUN_PASSED+=("$basename")
            else
                printf "\n"  # New line to preserve progress bar
                echo "Warning: Config file '$config_path' not found"
                echo "Error: Failed to run $basename" >&2
                echo "$run_output" >&2
                RUN_FAILED+=("$basename")
                failed_runs=$((failed_runs + 1))
            fi
        else
            if run_output=$(export FROST_CONFIG="$config_path" && "$binary_path" 2>&1); then
                RUN_PASSED+=("$basename")
            else
                printf "\n"  # New line to preserve progress bar
                echo "Error: Failed to run $basename" >&2
                echo "$run_output" >&2
                RUN_FAILED+=("$basename")
                failed_runs=$((failed_runs + 1))
            fi
        fi
    done
    
    echo  # Clear progress bar line
    
    if [ $failed_runs -gt 0 ]; then
        printf "${RED}⚠️  Warning: $failed_runs test(s) failed${RESET}\n" >&2
        return 1
    fi
    
    printf "${GREEN}✅ All tests completed successfully${RESET}\n"
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
    printf "${BOLD}${YELLOW}📁 Found ${#files[@]} test(s) in src directory${RESET}\n"
fi

# Execute based on options
if [ "$build_only" = true ]; then
    build_tests "${files[@]}"
elif [ "$run_only" = true ]; then
    run_tests "${files[@]}"
else
    build_tests "${files[@]}"
    run_tests "${files[@]}"
fi

# Print final colored report
printf "\n${BOLD}${BLUE}═════════════════════════════════════════════${RESET}\n"
printf "${BOLD}${BLUE}             📊 TEST SUMMARY${RESET}\n"
printf "${BOLD}${BLUE}═════════════════════════════════════════════${RESET}\n"

# Build results
if [ ${#BUILD_PASSED[@]} -gt 0 ] || [ ${#BUILD_FAILED[@]} -gt 0 ]; then
    printf "\n${BOLD}${BLUE}🔨 BUILD RESULTS:${RESET}\n"
    printf "${BLUE}┌───────────────────────────────────────────┐${RESET}\n"
    
    if [ ${#BUILD_PASSED[@]} -gt 0 ]; then
        printf "${BLUE}│${RESET} ${GREEN}${BOLD}✅ PASSED (${#BUILD_PASSED[@]})${RESET}                             ${BLUE}│${RESET}\n"
        for test in "${BUILD_PASSED[@]}"; do
            printf "${BLUE}│${RESET}   ${GREEN}🟢 %-36s${RESET} ${BLUE}│${RESET}\n" "$test"
        done
    fi
    
    if [ ${#BUILD_FAILED[@]} -gt 0 ]; then
        if [ ${#BUILD_PASSED[@]} -gt 0 ]; then
            printf "${BLUE}├───────────────────────────────────────────┤${RESET}\n"
        fi
        printf "${BLUE}│${RESET} ${RED}${BOLD}❌ FAILED (${#BUILD_FAILED[@]})${RESET}                             ${BLUE}│${RESET}\n"
        for test in "${BUILD_FAILED[@]}"; do
            printf "${BLUE}│${RESET}   ${RED}🔴 %-36s${RESET} ${BLUE}│${RESET}\n" "$test"
        done
    fi
    
    printf "${BLUE}└───────────────────────────────────────────┘${RESET}\n"
fi

# Run results
if [ ${#RUN_PASSED[@]} -gt 0 ] || [ ${#RUN_FAILED[@]} -gt 0 ] || [ ${#RUN_SKIPPED[@]} -gt 0 ]; then
    printf "\n${BOLD}${CYAN}🚀 RUN RESULTS:${RESET}\n"
    printf "${CYAN}┌───────────────────────────────────────────┐${RESET}\n"
    
    sections_printed=0
    
    if [ ${#RUN_PASSED[@]} -gt 0 ]; then
        printf "${CYAN}│${RESET} ${GREEN}${BOLD}✅ PASSED (${#RUN_PASSED[@]})${RESET}                             ${CYAN}│${RESET}\n"
        for test in "${RUN_PASSED[@]}"; do
            printf "${CYAN}│${RESET}   ${GREEN}🟢 %-36s${RESET} ${CYAN}│${RESET}\n" "$test"
        done
        sections_printed=$((sections_printed + 1))
    fi
    
    if [ ${#RUN_FAILED[@]} -gt 0 ]; then
        if [ $sections_printed -gt 0 ]; then
            printf "${CYAN}├───────────────────────────────────────────┤${RESET}\n"
        fi
        printf "${CYAN}│${RESET} ${RED}${BOLD}❌ FAILED (${#RUN_FAILED[@]})${RESET}                             ${CYAN}│${RESET}\n"
        for test in "${RUN_FAILED[@]}"; do
            printf "${CYAN}│${RESET}   ${RED}🔴 %-36s${RESET} ${CYAN}│${RESET}\n" "$test"
        done
        sections_printed=$((sections_printed + 1))
    fi
    
    if [ ${#RUN_SKIPPED[@]} -gt 0 ]; then
        if [ $sections_printed -gt 0 ]; then
            printf "${CYAN}├───────────────────────────────────────────┤${RESET}\n"
        fi
        printf "${CYAN}│${RESET} ${YELLOW}${BOLD}⏭️  SKIPPED (${#RUN_SKIPPED[@]}) - Build Failed${RESET}             ${CYAN}│${RESET}\n"
        for test in "${RUN_SKIPPED[@]}"; do
            printf "${CYAN}│${RESET}   ${YELLOW}⚪ %-36s${RESET} ${CYAN}│${RESET}\n" "$test"
        done
    fi
    
    printf "${CYAN}└───────────────────────────────────────────┘${RESET}\n"
fi

# Final status
total_build_tests=$((${#BUILD_PASSED[@]} + ${#BUILD_FAILED[@]}))
total_run_tests=$((${#RUN_PASSED[@]} + ${#RUN_FAILED[@]} + ${#RUN_SKIPPED[@]}))
total_failed=$((${#BUILD_FAILED[@]} + ${#RUN_FAILED[@]}))
total_passed=$((${#BUILD_PASSED[@]} + ${#RUN_PASSED[@]}))
total_skipped=${#RUN_SKIPPED[@]}

# Only show summary if we actually processed some tests
if [ $total_build_tests -gt 0 ] || [ $total_run_tests -gt 0 ]; then
    printf "\n${BOLD}${BLUE}═════════════════════════════════════════════${RESET}\n"
    if [ $total_failed -eq 0 ] && [ $total_skipped -eq 0 ] && [ $total_passed -gt 0 ]; then
        printf "${BOLD}${GREEN}🎉 ALL TESTS SUCCESSFUL! 🎉${RESET}\n"
        printf "${GREEN}Total: $total_passed passed, 0 failed${RESET}\n"
    else
        printf "${BOLD}${BLUE}📋 SUMMARY${RESET}\n"
        printf "${GREEN}Passed: $total_passed${RESET} | ${RED}Failed: $total_failed${RESET}"
        if [ $total_skipped -gt 0 ]; then
            printf " | ${YELLOW}Skipped: $total_skipped${RESET}"
        fi
        total_count=$((total_passed + total_failed + total_skipped))
        printf " | ${BLUE}Total: $total_count${RESET}\n"
    fi
    printf "${BOLD}${BLUE}═════════════════════════════════════════════${RESET}\n"
fi

# Exit with appropriate code
if [ ${#BUILD_FAILED[@]} -gt 0 ] || [ ${#RUN_FAILED[@]} -gt 0 ]; then
    exit 1
else
    exit 0
fi