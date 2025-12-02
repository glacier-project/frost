# Makefile for Lingua Franca test suite
# Uses run_all.sh script for building and running tests

# Default shell
SHELL := /bin/bash

# Test script
RUN_SCRIPT := test/run_all.sh

# Source directory
SRC_DIR := test/src

# Find all .lf files in src directory
LF_FILES := $(shell find $(SRC_DIR) -name "*.lf" 2>/dev/null)

# Default target
.PHONY: all
all: test

# Build and run all tests
.PHONY: test
test:
	@$(RUN_SCRIPT)

# Build tests only
.PHONY: build
build:
	@$(RUN_SCRIPT) --build-only

# Run tests only (assumes binaries exist)
.PHONY: run
run:
	@$(RUN_SCRIPT) --run-only

# Clean generated files
.PHONY: clean
clean:
	@echo "🧹 Cleaning generated files..."
	rm -rf test/bin/
	rm -rf test/include/
	rm -rf test/src-gen/
	@echo "✅ Clean complete"

# Individual test targets (build and run specific test)
.PHONY: test-%
test-%:
	@if [ -f "$(SRC_DIR)/$*.lf" ]; then \
		$(RUN_SCRIPT) "$(SRC_DIR)/$*.lf"; \
	else \
		echo "❌ Test file $(SRC_DIR)/$*.lf not found"; \
		exit 1; \
	fi

# Individual build targets
.PHONY: build-%
build-%:
	@if [ -f "$(SRC_DIR)/$*.lf" ]; then \
		$(RUN_SCRIPT) --build-only "$(SRC_DIR)/$*.lf"; \
	else \
		echo "❌ Test file $(SRC_DIR)/$*.lf not found"; \
		exit 1; \
	fi

# Individual run targets
.PHONY: run-%
run-%:
	@if [ -f "$(SRC_DIR)/$*.lf" ]; then \
		$(RUN_SCRIPT) --run-only "$(SRC_DIR)/$*.lf"; \
	else \
		echo "❌ Test file $(SRC_DIR)/$*.lf not found"; \
		exit 1; \
	fi

# List all available tests
.PHONY: list
list:
	@echo "📋 Available tests:"
	@for file in $(LF_FILES); do \
		basename="$$(basename "$$file" .lf)"; \
		echo "  - $$basename"; \
	done
	@echo ""
	@echo "Usage examples:"
	@echo "  make test              # Build and run all tests"
	@echo "  make build             # Build all tests only"
	@echo "  make run               # Run all tests only"
	@echo "  make test-TestName     # Build and run specific test"
	@echo "  make build-TestName    # Build specific test only"
	@echo "  make run-TestName      # Run specific test only"
	@echo "  make clean             # Clean generated files"
	@echo "  make list              # Show this help"

# Help target
.PHONY: help
help: list