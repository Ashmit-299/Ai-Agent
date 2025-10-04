#!/bin/bash
# Simple bash health check script

set -e

API_URL=${1:-"https://ai-agent-aff6.onrender.com"}
TIMEOUT=${2:-30}

echo "[CHECK] Running health check for $API_URL"

# Function to check endpoint
check_endpoint() {
    local endpoint=$1
    local expected_status=${2:-200}
    
    echo "[TEST] Checking $endpoint..."
    
    response=$(curl -s -w "%{http_code}" -m $TIMEOUT "$API_URL$endpoint" || echo "000")
    status_code="${response: -3}"
    
    if [ "$status_code" = "$expected_status" ]; then
        echo "[OK] $endpoint - Status: $status_code"
        return 0
    else
        echo "[ERROR] $endpoint - Expected: $expected_status, Got: $status_code"
        return 1
    fi
}

# Run health checks
failed_checks=0

# Core endpoints
check_endpoint "/health" 200 || ((failed_checks++))
check_endpoint "/docs" 200 || ((failed_checks++))
check_endpoint "/metrics" 200 || ((failed_checks++))
check_endpoint "/demo-login" 200 || ((failed_checks++))

# Summary
total_checks=4
success_rate=$(( (total_checks - failed_checks) * 100 / total_checks ))

echo ""
echo "=================================="
echo "[RESULTS] HEALTH CHECK SUMMARY"
echo "=================================="
echo "API URL: $API_URL"
echo "Total Checks: $total_checks"
echo "Failed Checks: $failed_checks"
echo "Success Rate: $success_rate%"

if [ $failed_checks -eq 0 ]; then
    echo "Overall Status: [OK] HEALTHY"
    exit 0
else
    echo "Overall Status: [ERROR] UNHEALTHY"
    exit 1
fi