#!/bin/bash
set -e

echo "╔════════════════════════════════════════╗"
echo "║     Clarity Release Verification       ║"
echo "╚════════════════════════════════════════╝"

ROOT_DIR=$(dirname "$0")/..
cd "$ROOT_DIR"

echo ""
echo "=== [1/5] Backend Lint ==="
cd solacore-api
poetry run ruff check .
echo "✅ Ruff passed"

echo ""
echo "=== [2/5] Backend Type Check ==="
poetry run mypy app --ignore-missing-imports
echo "✅ Mypy passed"

echo ""
echo "=== [3/5] Backend Tests ==="
poetry run pytest -v
echo "✅ Pytest passed"

echo ""
echo "=== [4/5] Mobile Lint ==="
cd ../solacore-mobile
npm run lint
echo "✅ ESLint passed"

echo ""
echo "=== [5/5] Mobile Type Check ==="
npx tsc --noEmit
echo "✅ TypeScript passed"

echo ""
echo "╔════════════════════════════════════════╗"
echo "║     ✅ ALL CHECKS PASSED               ║"
echo "╚════════════════════════════════════════╝"

echo ""
echo "Optional: Run these manually if server is running:"
echo "  curl http://localhost:8000/health"
echo "  curl http://localhost:8000/health/ready"
echo "  curl http://localhost:8000/health/live"
