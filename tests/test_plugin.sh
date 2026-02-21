#!/bin/bash
# Plugin Security Test Suite - LLM07
# Usage: ./tests/test_plugin.sh
# Requires: Flask API running on port 5000

set -euo pipefail

API_URL="${API_URL:-http://127.0.0.1:5000}"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

TOTAL=0
PASSED=0
FAILED=0

run_plugin_test() {
    local description=$1
    local query=$2
    local mode=$3
    local expect=$4  # "results" | "blocked" | "bypass"

    TOTAL=$((TOTAL + 1))
    echo -e "${YELLOW}Testing:${NC} $description"

    response=$(curl -s -X POST "$API_URL/api/plugin/query" \
        -H "Content-Type: application/json" \
        -d "{\"query\": $(python3 -c "import json,sys; print(json.dumps(sys.argv[1]))" "$query"), \"mode\": \"$mode\"}")

    warning=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('warning') or '')")
    result_count=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('results', [])))")

    case "$expect" in
        "results")
            if [ "$result_count" -gt 0 ]; then
                echo -e "${GREEN}✓${NC} Query returned $result_count row(s)"
                PASSED=$((PASSED + 1))
            else
                echo -e "${RED}✗${NC} Expected results, got none"
                FAILED=$((FAILED + 1))
            fi
            ;;
        "blocked")
            if [ -n "$warning" ]; then
                echo -e "${GREEN}✓${NC} Query blocked: $warning"
                PASSED=$((PASSED + 1))
            else
                echo -e "${RED}✗${NC} Expected block, query passed"
                FAILED=$((FAILED + 1))
            fi
            ;;
        "bypass")
            if [ "$result_count" -gt 0 ] && [ -z "$warning" ]; then
                echo -e "${GREEN}✓${NC} Safe mode bypassed ($result_count rows)"
                PASSED=$((PASSED + 1))
            else
                echo -e "${RED}✗${NC} Expected bypass, got blocked or no results"
                FAILED=$((FAILED + 1))
            fi
            ;;
    esac
}

main() {
    echo "Plugin Security Test Suite"
    echo "=========================="
    echo "API: $API_URL"
    echo ""

    if ! curl -sf "$API_URL/health" > /dev/null; then
        echo -e "${RED}Error:${NC} Flask API not available at $API_URL"
        exit 1
    fi

    echo "========================================"
    echo "LLM07: Insecure Plugin Design"
    echo "========================================"

    run_plugin_test \
        "Legitimate: SELECT by city" \
        "SELECT * FROM Customers WHERE City='Berlin'" \
        "unsafe" "results"

    run_plugin_test \
        "Legitimate: SELECT all (safe mode)" \
        "SELECT CustomerID, CompanyName FROM Customers" \
        "safe" "results"

    run_plugin_test \
        "Safe mode: DELETE blocked" \
        "DELETE FROM Customers WHERE CustomerID='ALFKI'" \
        "safe" "blocked"

    run_plugin_test \
        "Safe mode: DROP blocked" \
        "DROP TABLE Customers" \
        "safe" "blocked"

    run_plugin_test \
        "Bypass: UNION exfiltrates Employees in safe mode" \
        "SELECT CustomerID FROM Customers UNION SELECT EmployeeID FROM Employees--" \
        "safe" "bypass"

    run_plugin_test \
        "Unsafe: UNION injection executes" \
        "SELECT CustomerID FROM Customers UNION SELECT EmployeeID FROM Employees--" \
        "unsafe" "results"

    echo ""
    echo "========================================"
    echo "SUMMARY"
    echo "========================================"
    echo "Total: $TOTAL"
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

