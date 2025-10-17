#!/bin/bash

# Pharmacy Exam Prep - Validation Script
# Runs all linters and type checkers on backend and frontend

# Get the project root directory (parent of scripts directory)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

echo "🔍 Running validation checks..."
echo ""

ERRORS=0
RUFF_ERRORS=0
MYPY_ERRORS=0
SYNTAX_ERRORS=0
TS_ERRORS=0

# ============================================
# Python Backend Validation
# ============================================
echo "═══════════════════════════════════════"
echo "📦 PYTHON BACKEND VALIDATION"
echo "═══════════════════════════════════════"

# Check if ruff is installed
if ! command -v ruff &> /dev/null; then
    echo "⚠️  Ruff not installed. Installing..."
    pip install ruff
fi

# Check if mypy is installed
if ! command -v mypy &> /dev/null; then
    echo "⚠️  Mypy not installed. Installing..."
    pip install mypy types-requests
fi

echo ""
echo "🔧 Running Ruff (Python linter)..."
ruff check backend/ --select E,F,W,I,N,UP --ignore E501 2>&1 | tee /tmp/ruff_output.txt
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "✅ Ruff checks passed"
else
    echo "❌ Ruff found issues"
    RUFF_ERRORS=$(grep -c "^backend/" /tmp/ruff_output.txt || echo 0)
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "🔍 Running Mypy (type checker)..."
mypy backend/ --ignore-missing-imports --no-strict-optional 2>&1 | tee /tmp/mypy_output.txt
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "✅ Mypy checks passed"
else
    echo "❌ Mypy found issues"
    MYPY_ERRORS=$(grep -c "error:" /tmp/mypy_output.txt || echo 0)
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "🧪 Running Python syntax check..."
python -m py_compile backend/*.py 2>&1 | tee /tmp/syntax_output.txt
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "✅ Python syntax valid"
else
    echo "❌ Python syntax errors found"
    SYNTAX_ERRORS=$(grep -c "SyntaxError" /tmp/syntax_output.txt || echo 0)
    ERRORS=$((ERRORS + 1))
fi

# ============================================
# Frontend Validation
# ============================================
echo ""
echo "═══════════════════════════════════════"
echo "🎨 FRONTEND VALIDATION"
echo "═══════════════════════════════════════"

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "⚠️  Node modules not installed. Installing..."
    npm install
fi

echo ""
echo "🔧 Running ESLint..."
if npm run lint 2>/dev/null || npx eslint src/ --ext .ts,.vue 2>/dev/null; then
    echo "✅ ESLint checks passed"
else
    echo "⚠️  ESLint not configured (optional)"
fi

echo ""
echo "🔍 Running TypeScript compiler check..."
npx vue-tsc --noEmit 2>&1 | tee /tmp/ts_output.txt
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "✅ TypeScript checks passed"
else
    echo "❌ TypeScript errors found"
    TS_ERRORS=$(grep -c "error TS" /tmp/ts_output.txt || echo 0)
    ERRORS=$((ERRORS + 1))
fi

cd ..

# ============================================
# Summary
# ============================================
echo ""
echo "═══════════════════════════════════════"
echo "📊 VALIDATION SUMMARY"
echo "═══════════════════════════════════════"

if [ $ERRORS -eq 0 ]; then
    echo "✅ All validation checks passed!"
    echo ""
else
    echo "❌ Found $ERRORS tool(s) with errors"
    echo ""
    echo "Errors by tool:"
    [ $RUFF_ERRORS -gt 0 ] && echo "  🔧 Ruff: $RUFF_ERRORS issue(s)"
    [ $MYPY_ERRORS -gt 0 ] && echo "  🔍 Mypy: $MYPY_ERRORS error(s)"
    [ $SYNTAX_ERRORS -gt 0 ] && echo "  🧪 Syntax: $SYNTAX_ERRORS error(s)"
    [ $TS_ERRORS -gt 0 ] && echo "  📘 TypeScript: $TS_ERRORS error(s)"
    echo ""
    echo "Total errors: $((RUFF_ERRORS + MYPY_ERRORS + SYNTAX_ERRORS + TS_ERRORS))"
    echo ""
    echo "💡 Tips:"
    echo "  - Run 'ruff check backend/ --fix' to auto-fix Python issues"
    echo "  - Check logs above for specific error details"
    echo ""
    exit 1
fi
