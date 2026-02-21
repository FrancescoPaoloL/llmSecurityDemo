#!/bin/bash
# OWASP LLM Security Test Suite
# Usage: ./tests/test_owasp.sh [category]
# Example: ./tests/test_owasp.sh llm01

set -euo pipefail

# Paths
BINARY="./llama.cpp/build/bin/owasp-llm-tool"
PROMPTS_DIR="./tests/prompts"
RESULTS_DIR="./tests/results"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Categories
CATEGORIES=("llm01" "llm02" "llm03" "llm04" "llm05" "llm06" "llm09")

# Create results dir
mkdir -p "$RESULTS_DIR"

# Test counter
TOTAL=0
PASSED=0
FAILED=0

# Function: Run single test
run_test() {
    local prompt_file=$1
    local expected_category=$2
    local should_trigger=$3  # "trigger" or "safe"

    echo -e "${YELLOW}Testing:${NC} $(basename $prompt_file)"

    # Read prompts line by line
    while IFS= read -r prompt || [ -n "$prompt" ]; do
        # Skip empty lines and comments
        [[ -z "$prompt" || "$prompt" =~ ^# ]] && continue

        TOTAL=$((TOTAL + 1))

        # Run detection (load model only for LLM03)
        if [ "$expected_category" = "LLM03" ]; then
            # LLM03 requires model for perplexity calculation
            MODEL=$(ls ./models/*.gguf 2>/dev/null | head -1)
            if [ -z "$MODEL" ]; then
                echo -e "${RED}Error:${NC} No model found for LLM03 testing"
                result='{"category":"ERROR"}'
            else
                result=$("$BINARY" "$MODEL" "$prompt" 2>/dev/null || echo '{"category":"ERROR"}')
            fi
        else
            # Other categories use pattern-based detection (no model needed)
            result=$("$BINARY" --skip_llm_generation --prompt "$prompt" 2>/dev/null || echo '{"category":"ERROR"}')
        fi

        # Parse category from JSON
        detected_category=$(echo "$result" | grep -o '"category": *"[^"]*"' | cut -d'"' -f4)
        [ -z "$detected_category" ] && detected_category="unknown"

        # Check expectation
        if [ "$should_trigger" = "trigger" ]; then
            if [ "$detected_category" = "$expected_category" ]; then
                echo -e "${GREEN}✓${NC} Detected $detected_category: ${prompt:0:50}..."
                PASSED=$((PASSED + 1))
            else
                echo -e "${RED}✗${NC} Expected $expected_category, got $detected_category: ${prompt:0:50}..."
                FAILED=$((FAILED + 1))
            fi
        else
            if [ "$detected_category" = "unknown" ]; then
                echo -e "${GREEN}✓${NC} Safe (no detection): ${prompt:0:50}..."
                PASSED=$((PASSED + 1))
            else
                echo -e "${RED}✗${NC} False positive $detected_category: ${prompt:0:50}..."
                FAILED=$((FAILED + 1))
            fi
        fi
    done < "$prompt_file"
}

# Function: Test category
test_category() {
    local cat=$1

    echo ""
    echo "========================================"
    echo "Testing Category: ${cat^^}"
    echo "========================================"

    # Test malicious prompts
    if [ -f "$PROMPTS_DIR/${cat}_malicious.txt" ]; then
        run_test "$PROMPTS_DIR/${cat}_malicious.txt" "${cat^^}" "trigger"
    fi

    # Test legitimate prompts
    if [ -f "$PROMPTS_DIR/${cat}_legitimate.txt" ]; then
        run_test "$PROMPTS_DIR/${cat}_legitimate.txt" "${cat^^}" "safe"
    fi
}

# Main
main() {
    echo "OWASP LLM Security Test Suite"
    echo "=============================="

    # Check binary exists
    if [ ! -f "$BINARY" ]; then
        echo -e "${RED}Error:${NC} Binary not found: $BINARY"
        exit 1
    fi

    # Test specific category or all
    if [ $# -eq 1 ]; then
        test_category "$1"
    else
        for cat in "${CATEGORIES[@]}"; do
            test_category "$cat"
        done
    fi

    # Summary
    echo ""
    echo "========================================"
    echo "SUMMARY"
    echo "========================================"
    echo "Total tests: $TOTAL"
    echo -e "${GREEN}Passed: $PASSED${NC}"
    echo -e "${RED}Failed: $FAILED${NC}"
    echo ""

    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}Some tests failed.${NC}"
        exit 1
    fi
}

main "$@"
