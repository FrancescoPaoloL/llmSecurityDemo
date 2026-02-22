#!/bin/bash
# LLM10 Model Theft - API Test Suite
set -euo pipefail
API_URL="http://localhost:5000/api/llm10"
PROMPTS_DIR="./tests/prompts"
RESULTS_DIR="./tests/results"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'
TOTAL=0
PASSED=0
FAILED=0
mkdir -p "$RESULTS_DIR"
RESULT_FILE="$RESULTS_DIR/llm10_$(date +%Y%m%d_%H%M%S).json"
echo "[]" > "$RESULT_FILE"
check_api() {
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 "$API_URL")
    if [ "$status" = "000" ]; then
        echo -e "${RED}Error: API not reachable at $API_URL${NC}"
        exit 1
    else
        echo -e "${GREEN}API reachable (HTTP $status)${NC}"
    fi
}
run_test() {
    local prompt="$1"
    local mode="$2"     # "malicious" or "legitimate"
    local client_ip="$3" # IP per isolamento sessione
    TOTAL=$((TOTAL + 1))
    result=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -H "X-Forwarded-For: $client_ip" \
        -d "{\"prompt\": $(echo "$prompt" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}")
    verdict=$(echo "$result" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("verdict","unknown"))' 2>/dev/null || echo "error")
    score=$(echo "$result"   | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("score",0))' 2>/dev/null || echo "0")
    label="${prompt:0:55}..."
    if [ "$mode" = "malicious" ]; then
        if [ "$verdict" != "low" ]; then
            echo -e "${GREEN}✓${NC} [${CYAN}${verdict}${NC} / ${score}] $label"
            PASSED=$((PASSED + 1))
        else
            echo -e "${RED}✗${NC} [${verdict} / ${score}] MISSED: $label"
            FAILED=$((FAILED + 1))
        fi
    else
        if [ "$verdict" = "low" ]; then
            echo -e "${GREEN}✓${NC} [${CYAN}${verdict}${NC} / ${score}] $label"
            PASSED=$((PASSED + 1))
        else
            echo -e "${RED}✗${NC} [${verdict} / ${score}] FALSE POSITIVE: $label"
            FAILED=$((FAILED + 1))
        fi
    fi
}
main() {
    MALICIOUS_IP="10.0.0.$((RANDOM % 200 + 1))"
    LEGITIMATE_IP="10.0.0.$((RANDOM % 200 + 1))"
    while [ "$MALICIOUS_IP" = "$LEGITIMATE_IP" ]; do
        LEGITIMATE_IP="10.0.0.$((RANDOM % 200 + 1))"
    done
    echo "========================================"
    echo "LLM10 Model Theft - API Test Suite"
    echo "========================================"
    echo "Session IPs: malicious=$MALICIOUS_IP legitimate=$LEGITIMATE_IP"
    check_api
    echo ""
    echo "--- Malicious prompts (expect: medium/high) ---"
    while IFS= read -r line || [ -n "$line" ]; do
        [[ -z "$line" || "$line" =~ ^# ]] && continue
        run_test "$line" "malicious" "$MALICIOUS_IP"
    done < "$PROMPTS_DIR/llm10_malicious.txt"
    echo ""
    echo "--- Legitimate prompts (expect: low) ---"
    while IFS= read -r line || [ -n "$line" ]; do
        [[ -z "$line" || "$line" =~ ^# ]] && continue
        run_test "$line" "legitimate" "$LEGITIMATE_IP"
    done < "$PROMPTS_DIR/llm10_legitimate.txt"
    echo ""
    echo "========================================"
    echo "SUMMARY"
    echo "========================================"
    echo "Total : $TOTAL"
    echo -e "${GREEN}Passed: $PASSED${NC}"
    echo -e "${RED}Failed: $FAILED${NC}"
    echo ""
    RATE=$(python3 -c "print(f'{$PASSED/$TOTAL*100:.1f}%')" 2>/dev/null || echo "n/a")
    echo "Accuracy: $RATE"
    echo ""
    [ $FAILED -eq 0 ] && echo -e "${GREEN}All tests passed!${NC}" && exit 0
    echo -e "${RED}Some tests failed.${NC}" && exit 1
}
main "$@"

