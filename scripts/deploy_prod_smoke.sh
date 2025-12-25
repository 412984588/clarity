#!/bin/bash
# =============================================================================
# Production Smoke Test Script
# =============================================================================
# Usage: ./scripts/deploy_prod_smoke.sh <base_url>
# Example: ./scripts/deploy_prod_smoke.sh https://api.solacore.app
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BASE_URL="${1:-https://api.solacore.app}"
BASE_URL="${BASE_URL%/}"

log_pass() { echo -e "${GREEN}✅ $1${NC}"; }
log_fail() { echo -e "${RED}❌ $1${NC}"; }
log_warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }

FAILURES=0

echo ""
echo "=========================================="
echo "🔍 Production Smoke Tests"
echo "=========================================="
echo "Base URL: $BASE_URL"
echo ""

# Test /health
echo "Testing /health..."
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/health" 2>/dev/null)
HEALTH_BODY=$(echo "$HEALTH_RESPONSE" | sed '$d')
HEALTH_CODE=$(echo "$HEALTH_RESPONSE" | tail -n 1)

if [ "$HEALTH_CODE" = "200" ] && echo "$HEALTH_BODY" | grep -q '"status":"healthy"'; then
    log_pass "/health - healthy (HTTP $HEALTH_CODE)"
    echo "    Response: $HEALTH_BODY"
else
    log_fail "/health - HTTP $HEALTH_CODE"
    FAILURES=$((FAILURES + 1))
fi

# Test /health/ready
echo ""
echo "Testing /health/ready..."
READY_RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/health/ready" 2>/dev/null)
READY_BODY=$(echo "$READY_RESPONSE" | sed '$d')
READY_CODE=$(echo "$READY_RESPONSE" | tail -n 1)

if [ "$READY_CODE" = "200" ] && echo "$READY_BODY" | grep -q '"ready":true'; then
    log_pass "/health/ready - ready (HTTP $READY_CODE)"
else
    log_fail "/health/ready - HTTP $READY_CODE"
    FAILURES=$((FAILURES + 1))
fi

# Test /health/live
echo ""
echo "Testing /health/live..."
LIVE_RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/health/live" 2>/dev/null)
LIVE_BODY=$(echo "$LIVE_RESPONSE" | sed '$d')
LIVE_CODE=$(echo "$LIVE_RESPONSE" | tail -n 1)

if [ "$LIVE_CODE" = "200" ] && echo "$LIVE_BODY" | grep -q '"live":true'; then
    log_pass "/health/live - live (HTTP $LIVE_CODE)"
else
    log_fail "/health/live - HTTP $LIVE_CODE"
    FAILURES=$((FAILURES + 1))
fi

# Test webhook endpoints (reachability)
echo ""
echo "Testing webhook endpoints..."

STRIPE_CODE=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/webhooks/stripe" \
    -H "Content-Type: application/json" -d '{}' 2>/dev/null | tail -c 3)

if [ "$STRIPE_CODE" = "400" ] || [ "$STRIPE_CODE" = "401" ] || [ "$STRIPE_CODE" = "422" ]; then
    log_pass "/webhooks/stripe - reachable (HTTP $STRIPE_CODE)"
else
    log_fail "/webhooks/stripe - HTTP $STRIPE_CODE"
    FAILURES=$((FAILURES + 1))
fi

REVENUECAT_CODE=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/webhooks/revenuecat" \
    -H "Content-Type: application/json" -d '{}' 2>/dev/null | tail -c 3)

if [ "$REVENUECAT_CODE" = "400" ] || [ "$REVENUECAT_CODE" = "401" ] || [ "$REVENUECAT_CODE" = "422" ]; then
    log_pass "/webhooks/revenuecat - reachable (HTTP $REVENUECAT_CODE)"
else
    log_fail "/webhooks/revenuecat - HTTP $REVENUECAT_CODE"
    FAILURES=$((FAILURES + 1))
fi

# Summary
echo ""
echo "=========================================="
echo "📊 Summary"
echo "=========================================="

if [ $FAILURES -eq 0 ]; then
    log_pass "All smoke tests passed!"
    exit 0
else
    log_fail "$FAILURES test(s) failed"
    exit 1
fi
