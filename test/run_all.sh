#!/bin/sh

# Get all the files in the src directory
FILES=$(find src -type f -name "*.lf")

# Stop if any test fails
set -e

# Loop through each file and run the linter
for FILE in $FILES; do
    # convert the name to snake_case
    BASENAME=$(basename "$FILE" .lf)
    SNAKE_CASE_NAME=$(echo "$BASENAME" | sed -r 's/([a-z])([A-Z])/\1_\2/g' | tr '[:upper:]' '[:lower:]')
    echo "Building ${BASENAME} test..."
    lfc ${FILE}
    echo "Running ${BASENAME} test..."
    (export FROST_CONFIG="resources/${SNAKE_CASE_NAME}/frost_config.yml" && ./bin/${BASENAME})
done                